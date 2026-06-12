# 🌿 Plant Doctor

A multimodal app: upload a photo of a sick houseplant, get species ID, diagnosis,
clarifying questions, a recovery care plan, and weekly progress tracking.

## Architecture

```
frontend/  Streamlit app (auth, plant dashboard, diagnose, check-in, care plans, gallery)
backend/   FastAPI + SQLAlchemy + LangGraph + Groq vision (llama-4-scout)
```

**Flow (LangGraph-based):**
1. `POST /plants/{id}/diagnose` — identify species → diagnose symptom category
   (water/light/pest/nutrient/disease/healthy) → generate 2-3 clarifying questions.
2. `POST /plants/{id}/diagnose/answer` — resume with the user's answers → prescribe
   a care plan (summary, expected recovery time, checklist).
3. `POST /plants/{id}/checkin` — weekly follow-up: compares new photo vs. last photo,
   produces an updated care plan.

State for the pending clarifying-questions step is persisted in the `conversation_states`
table (SQLite), so the pause/resume works across separate HTTP requests without needing
a LangGraph checkpointer DB — see comments in `backend/app/agents/plant_agent.py` for the
full interrupt()-based alternative.

## Setup

### Backend

```bash
cd backend
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # add your GROQ_API_KEY
alembic upgrade head
uvicorn app.main:app --reload
```

API docs: http://localhost:8000/docs

### Frontend

```bash
cd frontend
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
mkdir -p .streamlit && cp .streamlit/secrets.toml.example .streamlit/secrets.toml
streamlit run app.py
```

## Database schema

- `users` — auth (email + bcrypt hash)
- `plants` — owner_id, name, species, location, status (healthy/recovering/critical/unknown)
- `photos` — plant_id, filepath, taken_at, note
- `diagnoses` — plant_id, photo_id, symptom_category, diagnosis_text, species_guess
- `care_plans` — plant_id, plan_text, expected_recovery, checklist_json
- `conversation_states` — plant_id, pending clarifying questions + serialized agent state

Migrations managed via Alembic (`backend/alembic/`).

## Deployment

- Backend: Render/Railway free tier (FastAPI + Uvicorn). See toolbox ref-deploy-render-railway.pdf.
- Frontend: Streamlit Community Cloud — set `API_BASE` in `secrets.toml` to your deployed
  backend URL.

## Open-ended stretch ideas

- RAG over plant-care guides (ChromaDB) for grounded answers with citations.
- Side-by-side photo diff overlay.
- APScheduler reminders for watering/fertilizing tasks.
- Public anonymized gallery of recovered plants by symptom category.
