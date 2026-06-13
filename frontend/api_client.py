import requests
import streamlit as st

try:
    API_BASE = st.secrets["API_BASE"]
except Exception:
    API_BASE = "https://plant-doctor-rgk7.onrender.com"


def _headers():
    token = st.session_state.get("token")
    return {"Authorization": f"Bearer {token}"} if token else {}


def signup(email: str, password: str):
    r = requests.post(f"{API_BASE}/auth/signup", json={"email": email, "password": password})
    return r


def login(email: str, password: str):
    r = requests.post(f"{API_BASE}/auth/login", data={"username": email, "password": password})
    return r


def list_plants():
    r = requests.get(f"{API_BASE}/plants", headers=_headers())
    r.raise_for_status()
    return r.json()


def create_plant(name: str, species: str, location: str):
    r = requests.post(
        f"{API_BASE}/plants",
        json={"name": name, "species": species or None, "location": location or None},
        headers=_headers(),
    )
    r.raise_for_status()
    return r.json()


def delete_plant(plant_id: int):
    r = requests.delete(f"{API_BASE}/plants/{plant_id}", headers=_headers())
    r.raise_for_status()


def diagnose(plant_id: int, image_bytes: bytes, filename: str, note: str):
    files = {"file": (filename, image_bytes, "image/jpeg")}
    data = {"note": note}
    r = requests.post(f"{API_BASE}/plants/{plant_id}/diagnose", files=files, data=data, headers=_headers())
    r.raise_for_status()
    return r.json()


def answer_clarifying(plant_id: int, answers: list[str]):
    r = requests.post(
        f"{API_BASE}/plants/{plant_id}/diagnose/answer",
        json={"answers": answers},
        headers=_headers(),
    )
    r.raise_for_status()
    return r.json()


def weekly_checkin(plant_id: int, image_bytes: bytes, filename: str, note: str):
    files = {"file": (filename, image_bytes, "image/jpeg")}
    data = {"note": note}
    r = requests.post(f"{API_BASE}/plants/{plant_id}/checkin", files=files, data=data, headers=_headers())
    r.raise_for_status()
    return r.json()


def list_photos(plant_id: int):
    r = requests.get(f"{API_BASE}/plants/{plant_id}/photos", headers=_headers())
    r.raise_for_status()
    return r.json()


def list_diagnoses(plant_id: int):
    r = requests.get(f"{API_BASE}/plants/{plant_id}/diagnoses", headers=_headers())
    r.raise_for_status()
    return r.json()


def list_care_plans(plant_id: int):
    r = requests.get(f"{API_BASE}/plants/{plant_id}/care-plans", headers=_headers())
    r.raise_for_status()
    return r.json()


def update_checklist(plant_id: int, plan_id: int, checklist: list[dict]):
    r = requests.patch(
        f"{API_BASE}/plants/{plant_id}/care-plans/{plan_id}/checklist",
        json={"checklist": checklist},
        headers=_headers(),
    )
    r.raise_for_status()
    return r.json()


def photo_url(filepath: str) -> str:
    # filepath looks like "uploads/3/abc.jpg" -> serve via /uploads static mount
    rel = filepath.split("uploads", 1)[-1].lstrip("/\\")
    return f"{API_BASE}/uploads/{rel}"
