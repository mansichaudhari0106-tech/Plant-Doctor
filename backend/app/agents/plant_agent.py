"""
Plant Doctor diagnosis agent.

Graph flow:
  identify_species -> diagnose_symptom -> generate_questions -> [interrupt] -> prescribe_plan

Because wiring a full SqliteSaver + interrupt() resume cycle through FastAPI's
request/response model adds significant complexity, this module implements the
SAME conceptual graph using LangGraph's StateGraph for the deterministic
identify -> diagnose -> question steps, and a simple two-call pattern for the
interrupt/resume:

  1. POST /plants/{id}/diagnose            -> runs steps 1-3, returns questions,
                                               persists intermediate state to DB.
  2. POST /plants/{id}/diagnose/answer      -> loads persisted state, runs step 4
                                               (prescribe) with the user's answers.

This mirrors the interrupt() pattern (pause -> separate HTTP request -> resume)
while keeping state durable in the existing SQLite DB (ConversationState table),
which is simpler to run/deploy on Render free tier than a separate checkpointer DB.

For comparison / extension: a true LangGraph `interrupt()` + SqliteSaver version
would replace the two functions below with a single compiled graph invoked twice
with `Command(resume=...)`. See ref-langgraph-llm-wiring.pdf for that pattern.
"""

import json
from typing import TypedDict, List, Optional
from langgraph.graph import StateGraph, END

from app.agents.groq_client import vision_chat, text_chat


class DiagnosisState(TypedDict, total=False):
    image_paths: List[str]
    prior_image_path: Optional[str]
    user_note: str
    species_guess: Optional[str]
    symptom_category: Optional[str]
    diagnosis_text: Optional[str]
    questions: List[str]
    answers: List[str]
    plan_text: Optional[str]
    expected_recovery: Optional[str]
    checklist: List[str]
    comparison_notes: Optional[str]


# ---------------- Graph nodes ----------------

def identify_species(state: DiagnosisState) -> DiagnosisState:
    if state.get("species_guess"):
        return state  # already known, skip

    prompt = (
        "You are a houseplant identification expert. Look at this photo and "
        "identify the plant species (common name + scientific name if confident). "
        "If you're unsure, give your best guess and note your uncertainty. "
        "Respond in 1-2 sentences only."
    )
    result = vision_chat(prompt, [state["image_paths"][0]])
    state["species_guess"] = result.strip()
    return state


def diagnose_symptom(state: DiagnosisState) -> DiagnosisState:
    note = state.get("user_note", "")
    prompt = (
        f"You are a plant health expert. The plant is: {state.get('species_guess', 'unknown species')}. "
        f"The owner says: \"{note}\"\n\n"
        "Look at the photo(s) and diagnose the likely issue. "
        "Classify the PRIMARY symptom category as exactly one of: "
        "water, light, pest, nutrient, disease, healthy.\n\n"
        "Respond in this exact format:\n"
        "CATEGORY: <one word from the list above>\n"
        "DIAGNOSIS: <2-4 sentences explaining what you see and the likely cause>"
    )
    result = vision_chat(prompt, state["image_paths"])

    category = "unknown"
    diagnosis_text = result.strip()
    for line in result.splitlines():
        if line.upper().startswith("CATEGORY:"):
            category = line.split(":", 1)[1].strip().lower()
        elif line.upper().startswith("DIAGNOSIS:"):
            diagnosis_text = line.split(":", 1)[1].strip()

    state["symptom_category"] = category
    state["diagnosis_text"] = diagnosis_text
    return state


def generate_questions(state: DiagnosisState) -> DiagnosisState:
    category = state.get("symptom_category", "unknown")
    if category == "healthy":
        state["questions"] = []
        return state

    prompt = (
        f"A houseplant ({state.get('species_guess')}) has a suspected '{category}' issue. "
        f"Initial diagnosis: {state.get('diagnosis_text')}\n\n"
        "Generate exactly 2-3 short, specific clarifying questions to ask the owner "
        "before prescribing a care plan (e.g. about watering frequency, light exposure, "
        "recent changes, pests seen, soil condition). "
        "Return ONLY the questions, one per line, no numbering, no extra text."
    )
    result = text_chat(prompt)
    questions = [q.strip("-•0123456789. ").strip() for q in result.splitlines() if q.strip()]
    state["questions"] = questions[:3]
    return state


def prescribe_plan(state: DiagnosisState) -> DiagnosisState:
    qa_pairs = ""
    for q, a in zip(state.get("questions", []), state.get("answers", [])):
        qa_pairs += f"Q: {q}\nA: {a}\n"

    comparison = ""
    if state.get("comparison_notes"):
        comparison = f"\nComparison with previous photo: {state['comparison_notes']}\n"

    prompt = (
        f"Plant: {state.get('species_guess')}\n"
        f"Diagnosis: {state.get('diagnosis_text')}\n"
        f"Symptom category: {state.get('symptom_category')}\n"
        f"Owner's note: {state.get('user_note', '')}\n"
        f"{qa_pairs}"
        f"{comparison}\n"
        "Based on all of the above, write a recovery care plan with:\n"
        "1. A short summary paragraph (2-3 sentences)\n"
        "2. An 'Expected recovery time' estimate (one short phrase, e.g. '1-2 weeks')\n"
        "3. A checklist of 4-6 concrete action items, one per line, starting with '- '\n\n"
        "Format your response EXACTLY as:\n"
        "SUMMARY: <paragraph>\n"
        "RECOVERY: <time estimate>\n"
        "CHECKLIST:\n- item1\n- item2\n..."
    )
    result = text_chat(prompt)

    summary, recovery, checklist = "", "", []
    section = None
    for line in result.splitlines():
        stripped = line.strip()
        if stripped.upper().startswith("SUMMARY:"):
            summary = stripped.split(":", 1)[1].strip()
            section = "summary"
        elif stripped.upper().startswith("RECOVERY:"):
            recovery = stripped.split(":", 1)[1].strip()
            section = "recovery"
        elif stripped.upper().startswith("CHECKLIST"):
            section = "checklist"
        elif stripped.startswith("- ") and section == "checklist":
            checklist.append(stripped[2:].strip())
        elif section == "summary" and stripped:
            summary += " " + stripped

    state["plan_text"] = summary or result.strip()
    state["expected_recovery"] = recovery or "1-2 weeks"
    state["checklist"] = checklist or ["Re-check plant in 7 days and upload a new photo."]
    return state


def compare_photos(state: DiagnosisState) -> DiagnosisState:
    """Used for weekly follow-up: compares prior and new photo."""
    if not state.get("prior_image_path"):
        return state

    prompt = (
        "Here are two photos of the same houseplant: the first is from a previous "
        "check-in, the second is from today. Compare them and describe in 2-3 sentences "
        "what has changed (better, worse, no change) — focus on leaf color, new growth, "
        "wilting, spots, or pests."
    )
    result = vision_chat(prompt, [state["prior_image_path"], state["image_paths"][0]])
    state["comparison_notes"] = result.strip()
    return state


# ---------------- Build graphs ----------------

def build_diagnose_graph():
    """Steps 1-3: identify -> diagnose -> generate questions."""
    graph = StateGraph(DiagnosisState)
    graph.add_node("identify_species", identify_species)
    graph.add_node("diagnose_symptom", diagnose_symptom)
    graph.add_node("generate_questions", generate_questions)

    graph.set_entry_point("identify_species")
    graph.add_edge("identify_species", "diagnose_symptom")
    graph.add_edge("diagnose_symptom", "generate_questions")
    graph.add_edge("generate_questions", END)
    return graph.compile()


def build_prescribe_graph():
    """Step 4 (resume): prescribe plan, optionally with photo comparison first."""
    graph = StateGraph(DiagnosisState)
    graph.add_node("compare_photos", compare_photos)
    graph.add_node("prescribe_plan", prescribe_plan)

    graph.set_entry_point("compare_photos")
    graph.add_edge("compare_photos", "prescribe_plan")
    graph.add_edge("prescribe_plan", END)
    return graph.compile()


diagnose_graph = build_diagnose_graph()
prescribe_graph = build_prescribe_graph()


def run_diagnose(image_paths: List[str], user_note: str) -> DiagnosisState:
    initial: DiagnosisState = {"image_paths": image_paths, "user_note": user_note}
    return diagnose_graph.invoke(initial)


def run_prescribe(state: DiagnosisState, answers: List[str]) -> DiagnosisState:
    state = dict(state)
    state["answers"] = answers
    return prescribe_graph.invoke(state)


def run_followup(prior_state: DiagnosisState, new_image_path: str) -> DiagnosisState:
    """Weekly check-in: compare photos + re-prescribe."""
    state = dict(prior_state)
    state["prior_image_path"] = state["image_paths"][0]
    state["image_paths"] = [new_image_path]
    return prescribe_graph.invoke(state)
