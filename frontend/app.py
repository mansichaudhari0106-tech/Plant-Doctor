import streamlit as st
import api_client as api

st.set_page_config(page_title="🌿 Plant Doctor", page_icon="🌿", layout="wide")

# ---------------- Session state ----------------
if "token" not in st.session_state:
    st.session_state.token = None
if "user_email" not in st.session_state:
    st.session_state.user_email = None
if "selected_plant" not in st.session_state:
    st.session_state.selected_plant = None
if "pending_diagnosis" not in st.session_state:
    st.session_state.pending_diagnosis = None  # {"questions": [...], "diagnosis": {...}}


# ---------------- Auth screens ----------------
def auth_screen():
    st.title("🌿 Plant Doctor")
    st.caption("Upload a photo of your sick houseplant and get a diagnosis + recovery plan.")

    tab_login, tab_signup = st.tabs(["Log in", "Sign up"])

    with tab_login:
        with st.form("login_form"):
            email = st.text_input("Email", key="login_email")
            password = st.text_input("Password", type="password", key="login_password")
            submitted = st.form_submit_button("Log in")
            if submitted:
                r = api.login(email, password)
                if r.status_code == 200:
                    st.session_state.token = r.json()["access_token"]
                    st.session_state.user_email = email
                    st.rerun()
                else:
                    st.error(r.json().get("detail", "Login failed"))

    with tab_signup:
        with st.form("signup_form"):
            email = st.text_input("Email", key="signup_email")
            password = st.text_input("Password", type="password", key="signup_password")
            submitted = st.form_submit_button("Sign up")
            if submitted:
                r = api.signup(email, password)
                if r.status_code == 201:
                    st.success("Account created! Please log in.")
                else:
                    st.error(r.json().get("detail", "Signup failed"))


# ---------------- Dashboard ----------------
def status_badge(status: str) -> str:
    return {
        "healthy": "🟢 Healthy",
        "recovering": "🟡 Recovering",
        "critical": "🔴 Critical",
        "unknown": "⚪ Unknown",
    }.get(status, status)


def dashboard():
    st.sidebar.title("🌿 Plant Doctor")
    st.sidebar.caption(f"Logged in as {st.session_state.user_email}")
    if st.sidebar.button("Log out"):
        st.session_state.token = None
        st.session_state.user_email = None
        st.session_state.selected_plant = None
        st.rerun()

    st.sidebar.divider()
    st.sidebar.subheader("Add a plant")
    with st.sidebar.form("new_plant_form", clear_on_submit=True):
        name = st.text_input("Name", placeholder="e.g. Pothos - living room")
        species = st.text_input("Species (optional)", placeholder="leave blank to auto-detect")
        location = st.text_input("Location (optional)", placeholder="north-facing window")
        if st.form_submit_button("Add plant"):
            if name:
                api.create_plant(name, species, location)
                st.rerun()
            else:
                st.warning("Name is required")

    st.sidebar.divider()
    plants = api.list_plants()

    if not plants:
        st.info("No plants yet — add one from the sidebar to get started 🌱")
        return

    st.sidebar.subheader("My plants")
    plant_names = {p["id"]: f"{p['name']} ({status_badge(p['status'])})" for p in plants}
    selected_id = st.sidebar.radio(
        "Select a plant",
        options=list(plant_names.keys()),
        format_func=lambda pid: plant_names[pid],
        index=0,
    )
    st.session_state.selected_plant = selected_id

    plant = next(p for p in plants if p["id"] == selected_id)

    if st.sidebar.button("🗑️ Delete this plant"):
        api.delete_plant(selected_id)
        st.session_state.selected_plant = None
        st.session_state.pending_diagnosis = None
        st.rerun()

    plant_view(plant)


def plant_view(plant: dict):
    st.title(f"🌱 {plant['name']}")
    cols = st.columns(3)
    cols[0].metric("Status", status_badge(plant["status"]))
    cols[1].metric("Species", plant["species"] or "Unknown")
    cols[2].metric("Location", plant["location"] or "—")

    tab_diagnose, tab_checkin, tab_history, tab_gallery = st.tabs(
        ["🩺 Diagnose", "📅 Weekly check-in", "📋 Care plans", "🖼️ Photo gallery"]
    )

    with tab_diagnose:
        diagnose_tab(plant)

    with tab_checkin:
        checkin_tab(plant)

    with tab_history:
        history_tab(plant)

    with tab_gallery:
        gallery_tab(plant)


def diagnose_tab(plant: dict):
    plant_id = plant["id"]
    pending = st.session_state.pending_diagnosis

    if pending and pending.get("plant_id") == plant_id:
        st.subheader("🔍 Diagnosis so far")
        diag = pending["diagnosis"]
        st.write(f"**Species guess:** {diag.get('species_guess', 'Unknown')}")
        st.write(f"**Symptom category:** {diag.get('symptom_category', 'Unknown')}")
        st.write(f"**Initial assessment:** {diag.get('diagnosis_text', '')}")

        st.subheader("🤔 A few quick questions before I prescribe a plan")
        answers = []
        with st.form("clarify_form"):
            for i, q in enumerate(pending["questions"]):
                ans = st.text_input(q, key=f"clarify_{plant_id}_{i}")
                answers.append(ans)
            if st.form_submit_button("Submit answers & get care plan"):
                with st.spinner("Generating your care plan..."):
                    result = api.answer_clarifying(plant_id, answers)
                st.session_state.pending_diagnosis = None
                st.success("Care plan ready! See the 'Care plans' tab.")
                st.rerun()
        return

    st.subheader("Upload a photo of your plant")
    uploaded = st.file_uploader("Photo", type=["jpg", "jpeg", "png"], key=f"diag_upload_{plant_id}")
    note = st.text_area("What's wrong? (describe symptoms, recent changes, etc.)", key=f"diag_note_{plant_id}")

    if uploaded:
        st.image(uploaded, width=300)

    if st.button("🔬 Diagnose", disabled=uploaded is None):
        with st.spinner("Analyzing photo..."):
            result = api.diagnose(plant_id, uploaded.getvalue(), uploaded.name, note)

        if result["status"] == "clarifying":
            st.session_state.pending_diagnosis = {
                "plant_id": plant_id,
                "diagnosis": result["diagnosis"],
                "questions": result["questions"],
            }
            st.rerun()
        else:
            st.success("Diagnosis complete! Your plant looks healthy, or a care plan was generated automatically.")
            st.rerun()


def checkin_tab(plant: dict):
    plant_id = plant["id"]
    diagnoses = api.list_diagnoses(plant_id)
    if not diagnoses:
        st.info("Run a diagnosis first (see the 'Diagnose' tab) before doing a weekly check-in.")
        return

    st.subheader("Weekly check-in")
    st.caption("Upload a new photo to compare against your last one and get an updated care plan.")

    uploaded = st.file_uploader("New photo", type=["jpg", "jpeg", "png"], key=f"checkin_upload_{plant_id}")
    note = st.text_area("Any changes you've noticed?", key=f"checkin_note_{plant_id}")

    if uploaded:
        st.image(uploaded, width=300)

    if st.button("📸 Run check-in", disabled=uploaded is None):
        with st.spinner("Comparing photos and updating your care plan..."):
            plan = api.weekly_checkin(plant_id, uploaded.getvalue(), uploaded.name, note)
        st.success("Care plan updated! See the 'Care plans' tab.")
        st.rerun()


def history_tab(plant: dict):
    plant_id = plant["id"]
    plans = api.list_care_plans(plant_id)

    if not plans:
        st.info("No care plans yet — run a diagnosis to generate one.")
        return

    for i, plan in enumerate(plans):
        with st.expander(f"Care plan from {plan['created_at'][:16].replace('T', ' ')}", expanded=(i == 0)):
            st.write(plan["plan_text"])
            st.write(f"**Expected recovery:** {plan['expected_recovery']}")

            st.write("**Checklist:**")
            updated = []
            changed = False
            for j, item in enumerate(plan["checklist"]):
                checked = st.checkbox(item["item"], value=item["done"], key=f"check_{plan['id']}_{j}")
                if checked != item["done"]:
                    changed = True
                updated.append({"item": item["item"], "done": checked})

            if changed and i == 0:
                api.update_checklist(plant_id, plan["id"], updated)
                st.rerun()


def gallery_tab(plant: dict):
    plant_id = plant["id"]
    photos = api.list_photos(plant_id)

    if not photos:
        st.info("No photos uploaded yet.")
        return

    st.subheader("Recovery timeline")
    cols = st.columns(4)
    for i, photo in enumerate(photos):
        with cols[i % 4]:
            try:
                st.image(api.photo_url(photo["filepath"]), caption=photo["taken_at"][:10])
            except Exception:
                st.caption(f"(image unavailable) {photo['taken_at'][:10]}")
            if photo["note"]:
                st.caption(photo["note"])


# ---------------- Main ----------------
if st.session_state.token is None:
    auth_screen()
else:
    dashboard()
