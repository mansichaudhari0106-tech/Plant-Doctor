import os
import json
import uuid
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
from typing import List

from app.core.database import get_db
from app.core.security import get_current_user
from app.core.config import settings
from app.models.models import User, Plant, Photo, Diagnosis, CarePlan, ConversationState
from app.models.schemas import (
    DiagnoseResponse, DiagnosisOut, CarePlanOut, AnswerClarifyingRequest,
    PhotoOut, ChecklistUpdate, ChecklistItem
)
from app.agents.plant_agent import run_diagnose, run_prescribe, run_followup

router = APIRouter(prefix="/plants", tags=["diagnosis"])


def _get_plant(plant_id: int, db: Session, user: User) -> Plant:
    plant = db.query(Plant).filter(Plant.id == plant_id, Plant.owner_id == user.id).first()
    if not plant:
        raise HTTPException(status_code=404, detail="Plant not found")
    return plant


def _save_upload(plant_id: int, file: UploadFile) -> str:
    plant_dir = os.path.join(settings.UPLOAD_DIR, str(plant_id))
    os.makedirs(plant_dir, exist_ok=True)
    ext = os.path.splitext(file.filename)[1] or ".jpg"
    filename = f"{uuid.uuid4().hex}{ext}"
    filepath = os.path.join(plant_dir, filename)
    with open(filepath, "wb") as f:
        f.write(file.file.read())
    return filepath


def _checklist_to_json(items: List[str]) -> str:
    return json.dumps([{"item": i, "done": False} for i in items])


def _care_plan_to_out(cp: CarePlan) -> CarePlanOut:
    checklist = json.loads(cp.checklist_json) if cp.checklist_json else []
    return CarePlanOut(
        id=cp.id,
        plan_text=cp.plan_text,
        expected_recovery=cp.expected_recovery,
        checklist=[ChecklistItem(**c) for c in checklist],
        created_at=cp.created_at,
    )


@router.post("/{plant_id}/diagnose", response_model=DiagnoseResponse)
def diagnose(
    plant_id: int,
    file: UploadFile = File(...),
    note: str = Form(""),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Step 1-3: identify species, diagnose symptom, generate clarifying questions."""
    plant = _get_plant(plant_id, db, user)

    filepath = _save_upload(plant_id, file)
    photo = Photo(plant_id=plant.id, filepath=filepath, note=note)
    db.add(photo)
    db.commit()
    db.refresh(photo)

    result_state = run_diagnose([filepath], note)

    # update species if unknown
    if not plant.species and result_state.get("species_guess"):
        plant.species = result_state["species_guess"]

    diagnosis = Diagnosis(
        plant_id=plant.id,
        photo_id=photo.id,
        symptom_category=result_state.get("symptom_category"),
        diagnosis_text=result_state.get("diagnosis_text"),
        species_guess=result_state.get("species_guess"),
    )
    db.add(diagnosis)

    questions = result_state.get("questions", [])

    if not questions:
        # "healthy" or no clarification needed -> prescribe immediately
        plant.status = "healthy" if result_state.get("symptom_category") == "healthy" else "recovering"
        rx_state = run_prescribe(result_state, [])
        care_plan = CarePlan(
            plant_id=plant.id,
            plan_text=rx_state.get("plan_text", ""),
            expected_recovery=rx_state.get("expected_recovery"),
            checklist_json=_checklist_to_json(rx_state.get("checklist", [])),
        )
        db.add(care_plan)
        db.commit()
        db.refresh(diagnosis)
        db.refresh(care_plan)
        return DiagnoseResponse(status="complete", diagnosis=diagnosis, care_plan=_care_plan_to_out(care_plan))

    # Save pending state for resume
    plant.status = "recovering"
    conv = db.query(ConversationState).filter(ConversationState.plant_id == plant.id).first()
    if not conv:
        conv = ConversationState(plant_id=plant.id, thread_id=f"plant-{plant.id}")
        db.add(conv)

    conv.pending_questions_json = json.dumps(questions)
    conv.answers_json = None
    conv.awaiting_input = True
    conv.state_json = json.dumps(result_state)
    conv.updated_at = datetime.utcnow()

    db.commit()
    db.refresh(diagnosis)

    return DiagnoseResponse(status="clarifying", diagnosis=diagnosis, questions=questions)


@router.post("/{plant_id}/diagnose/answer", response_model=DiagnoseResponse)
def answer_clarifying(
    plant_id: int,
    payload: AnswerClarifyingRequest,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Step 4 (resume): use clarifying answers to prescribe a care plan."""
    plant = _get_plant(plant_id, db, user)

    conv = db.query(ConversationState).filter(ConversationState.plant_id == plant.id).first()
    if not conv or not conv.awaiting_input or not conv.state_json:
        raise HTTPException(status_code=400, detail="No pending diagnosis awaiting answers for this plant")

    state = json.loads(conv.state_json)
    rx_state = run_prescribe(state, payload.answers)

    care_plan = CarePlan(
        plant_id=plant.id,
        plan_text=rx_state.get("plan_text", ""),
        expected_recovery=rx_state.get("expected_recovery"),
        checklist_json=_checklist_to_json(rx_state.get("checklist", [])),
    )
    db.add(care_plan)

    conv.awaiting_input = False
    conv.answers_json = json.dumps(payload.answers)
    conv.updated_at = datetime.utcnow()

    db.commit()
    db.refresh(care_plan)

    return DiagnoseResponse(status="complete", care_plan=_care_plan_to_out(care_plan))


@router.post("/{plant_id}/checkin", response_model=CarePlanOut)
def weekly_checkin(
    plant_id: int,
    file: UploadFile = File(...),
    note: str = Form(""),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Weekly follow-up: compare new photo to most recent prior photo, update care plan."""
    plant = _get_plant(plant_id, db, user)

    prior_photo = (
        db.query(Photo)
        .filter(Photo.plant_id == plant.id)
        .order_by(Photo.taken_at.desc())
        .first()
    )

    filepath = _save_upload(plant_id, file)
    photo = Photo(plant_id=plant.id, filepath=filepath, note=note)
    db.add(photo)
    db.commit()
    db.refresh(photo)

    latest_diagnosis = (
        db.query(Diagnosis)
        .filter(Diagnosis.plant_id == plant.id)
        .order_by(Diagnosis.created_at.desc())
        .first()
    )
    if not latest_diagnosis:
        raise HTTPException(status_code=400, detail="No prior diagnosis to follow up on. Run /diagnose first.")

    latest_plan = (
        db.query(CarePlan)
        .filter(CarePlan.plant_id == plant.id)
        .order_by(CarePlan.created_at.desc())
        .first()
    )

    prior_state = {
        "image_paths": [prior_photo.filepath] if prior_photo else [filepath],
        "user_note": note,
        "species_guess": latest_diagnosis.species_guess,
        "symptom_category": latest_diagnosis.symptom_category,
        "diagnosis_text": latest_diagnosis.diagnosis_text,
        "questions": [],
        "answers": [],
    }

    rx_state = run_followup(prior_state, filepath)

    care_plan = CarePlan(
        plant_id=plant.id,
        plan_text=rx_state.get("plan_text", ""),
        expected_recovery=rx_state.get("expected_recovery"),
        checklist_json=_checklist_to_json(rx_state.get("checklist", [])),
    )
    db.add(care_plan)
    db.commit()
    db.refresh(care_plan)

    return _care_plan_to_out(care_plan)


@router.get("/{plant_id}/photos", response_model=List[PhotoOut])
def list_photos(plant_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    plant = _get_plant(plant_id, db, user)
    return db.query(Photo).filter(Photo.plant_id == plant.id).order_by(Photo.taken_at.asc()).all()


@router.get("/{plant_id}/diagnoses", response_model=List[DiagnosisOut])
def list_diagnoses(plant_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    plant = _get_plant(plant_id, db, user)
    return db.query(Diagnosis).filter(Diagnosis.plant_id == plant.id).order_by(Diagnosis.created_at.desc()).all()


@router.get("/{plant_id}/care-plans", response_model=List[CarePlanOut])
def list_care_plans(plant_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    plant = _get_plant(plant_id, db, user)
    plans = db.query(CarePlan).filter(CarePlan.plant_id == plant.id).order_by(CarePlan.created_at.desc()).all()
    return [_care_plan_to_out(p) for p in plans]


@router.patch("/{plant_id}/care-plans/{plan_id}/checklist", response_model=CarePlanOut)
def update_checklist(
    plant_id: int,
    plan_id: int,
    payload: ChecklistUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    plant = _get_plant(plant_id, db, user)
    plan = db.query(CarePlan).filter(CarePlan.id == plan_id, CarePlan.plant_id == plant.id).first()
    if not plan:
        raise HTTPException(status_code=404, detail="Care plan not found")

    plan.checklist_json = json.dumps([item.model_dump() for item in payload.checklist])
    db.commit()
    db.refresh(plan)

    # if all items done, mark plant healthy
    if all(item.done for item in payload.checklist) and payload.checklist:
        plant.status = "healthy"
        db.commit()

    return _care_plan_to_out(plan)
