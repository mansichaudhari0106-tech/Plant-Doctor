from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, EmailStr


class UserCreate(BaseModel):
    email: EmailStr
    password: str

class UserOut(BaseModel):
    id: int
    email: EmailStr
    auth_provider: str
    created_at: datetime
    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

class PlantCreate(BaseModel):
    name: str
    species: Optional[str] = None
    location: Optional[str] = None

class PlantOut(BaseModel):
    id: int
    name: str
    species: Optional[str]
    location: Optional[str]
    status: str
    created_at: datetime
    class Config:
        from_attributes = True

class PhotoOut(BaseModel):
    id: int
    filepath: str
    taken_at: datetime
    note: Optional[str]
    class Config:
        from_attributes = True

class DiagnosisOut(BaseModel):
    id: int
    symptom_category: Optional[str]
    diagnosis_text: Optional[str]
    species_guess: Optional[str]
    created_at: datetime
    class Config:
        from_attributes = True

class ChecklistItem(BaseModel):
    item: str
    done: bool = False

class CarePlanOut(BaseModel):
    id: int
    plan_text: str
    expected_recovery: Optional[str]
    checklist: List[ChecklistItem] = []
    created_at: datetime
    class Config:
        from_attributes = True

class DiagnoseResponse(BaseModel):
    status: str
    diagnosis: Optional[DiagnosisOut] = None
    questions: Optional[List[str]] = None
    care_plan: Optional[CarePlanOut] = None

class AnswerClarifyingRequest(BaseModel):
    answers: List[str]

class ChecklistUpdate(BaseModel):
    checklist: List[ChecklistItem]

class SupabaseTokenRequest(BaseModel):
    supabase_access_token: str
