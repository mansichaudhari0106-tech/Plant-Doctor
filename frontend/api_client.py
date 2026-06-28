import requests
import streamlit as st

try:
    API_BASE = st.secrets["API_BASE"]
except Exception:
    API_BASE = "http://localhost:8000"


def _headers():
    token = st.session_state.get("token")
    return {"Authorization": f"Bearer {token}"} if token else {}

def signup(email, password):
    return requests.post(f"{API_BASE}/auth/signup", json={"email": email, "password": password})

def login(email, password):
    return requests.post(f"{API_BASE}/auth/login", data={"username": email, "password": password})

def get_google_url():
    return requests.get(f"{API_BASE}/auth/google/url")

def google_callback(access_token):
    return requests.post(f"{API_BASE}/auth/google/callback",
                         json={"supabase_access_token": access_token})

def list_plants():
    r = requests.get(f"{API_BASE}/plants", headers=_headers()); r.raise_for_status(); return r.json()

def create_plant(name, species, location):
    r = requests.post(f"{API_BASE}/plants",
                      json={"name": name, "species": species or None, "location": location or None},
                      headers=_headers()); r.raise_for_status(); return r.json()

def delete_plant(plant_id):
    r = requests.delete(f"{API_BASE}/plants/{plant_id}", headers=_headers()); r.raise_for_status()

def diagnose(plant_id, image_bytes, filename, note):
    r = requests.post(f"{API_BASE}/plants/{plant_id}/diagnose",
                      files={"file": (filename, image_bytes, "image/jpeg")},
                      data={"note": note}, headers=_headers()); r.raise_for_status(); return r.json()

def answer_clarifying(plant_id, answers):
    r = requests.post(f"{API_BASE}/plants/{plant_id}/diagnose/answer",
                      json={"answers": answers}, headers=_headers()); r.raise_for_status(); return r.json()

def weekly_checkin(plant_id, image_bytes, filename, note):
    r = requests.post(f"{API_BASE}/plants/{plant_id}/checkin",
                      files={"file": (filename, image_bytes, "image/jpeg")},
                      data={"note": note}, headers=_headers()); r.raise_for_status(); return r.json()

def list_photos(plant_id):
    r = requests.get(f"{API_BASE}/plants/{plant_id}/photos", headers=_headers())
    r.raise_for_status(); return r.json()

def list_diagnoses(plant_id):
    r = requests.get(f"{API_BASE}/plants/{plant_id}/diagnoses", headers=_headers())
    r.raise_for_status(); return r.json()

def list_care_plans(plant_id):
    r = requests.get(f"{API_BASE}/plants/{plant_id}/care-plans", headers=_headers())
    r.raise_for_status(); return r.json()

def update_checklist(plant_id, plan_id, checklist):
    r = requests.patch(f"{API_BASE}/plants/{plant_id}/care-plans/{plan_id}/checklist",
                       json={"checklist": checklist}, headers=_headers())
    r.raise_for_status(); return r.json()

def photo_url(filepath):
    rel = filepath.split("uploads", 1)[-1].lstrip("/\\")
    return f"{API_BASE}/uploads/{rel}"
