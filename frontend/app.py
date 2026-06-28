import streamlit as st
import requests
import api_client as api

st.set_page_config(page_title="Plant Doctor", page_icon="🌿", layout="wide")

# ─── CSS ──────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
.stApp { background: #f4f7f4; }
#MainMenu, footer, header { visibility: hidden; }
.block-container { padding: 0 !important; max-width: 100% !important; }

.pd-card { background:white; border-radius:16px; padding:24px; margin-bottom:16px;
           box-shadow:0 1px 4px rgba(0,0,0,0.08); }

section[data-testid="stSidebar"] { background:white !important;
    border-right:1px solid #e8f0e8; min-width:240px !important; max-width:240px !important; }
section[data-testid="stSidebar"] .block-container { padding:24px 16px !important; }

/* Primary buttons */
button[data-testid="baseButton-primary"] {
    background:#2D6A4F !important; color:white !important; border:none !important;
    border-radius:10px !important; font-weight:600 !important;
    padding:10px 20px !important; width:100%; transition:background 0.2s; }
button[data-testid="baseButton-primary"]:hover { background:#1B4332 !important; }

/* Secondary = back button */
button[data-testid="baseButton-secondary"] {
    background:white !important; color:#2D6A4F !important;
    border:1.5px solid #2D6A4F !important; border-radius:10px !important;
    font-size:13px !important; font-weight:500 !important;
    padding:5px 16px !important; width:auto !important; transition:background 0.2s; }
button[data-testid="baseButton-secondary"]:hover { background:#f0f7f0 !important; }

.badge { display:inline-block; padding:3px 12px; border-radius:20px;
         font-size:12px; font-weight:600; }
.badge-healthy   { background:#d1fae5; color:#065f46; }
.badge-recovering{ background:#fef3c7; color:#92400e; }
.badge-critical  { background:#fee2e2; color:#991b1b; }
.badge-unknown   { background:#f3f4f6; color:#6b7280; }

.plant-card { background:white; border-radius:16px; overflow:hidden;
              box-shadow:0 1px 4px rgba(0,0,0,0.08); transition:transform 0.2s; }
.plant-card:hover { transform:translateY(-2px); box-shadow:0 4px 12px rgba(0,0,0,0.12); }

.stTextInput > div > div > input, .stTextArea > div > div > textarea {
    border-radius:10px !important; border:1.5px solid #e5e7eb !important; }
.stTextInput > div > div > input:focus, .stTextArea > div > div > textarea:focus {
    border-color:#2D6A4F !important; box-shadow:0 0 0 3px rgba(45,106,79,0.1) !important; }

.page-header { background:white; padding:20px 32px; border-bottom:1px solid #e8f0e8;
               margin-bottom:24px; }
.page-header h1 { margin:0; font-size:20px; font-weight:700; color:#1a1a1a; }
.page-header p  { margin:0; font-size:13px; color:#6b7280; }

.chat-bot { display:flex; gap:10px; align-items:flex-start; }
.chat-bot-icon { background:#2D6A4F; color:white; width:32px; height:32px; border-radius:50%;
                 display:flex; align-items:center; justify-content:center; font-size:14px; flex-shrink:0; }
.chat-bubble-bot { background:#f0f7f0; border-radius:0 12px 12px 12px;
                   padding:10px 14px; font-size:14px; color:#1a1a1a; max-width:75%; }
.chat-bubble-user { background:#2D6A4F; color:white; border-radius:12px 0 12px 12px;
                    padding:10px 14px; font-size:14px; max-width:75%; margin-left:auto; }

.recovery-banner { background:#f0f7f0; border-radius:12px; padding:16px 20px;
                   display:flex; align-items:center; gap:14px; margin-bottom:16px; }
.recovery-days { font-size:28px; font-weight:800; color:#2D6A4F; }

.checklist-progress { background:#f3f4f6; border-radius:8px; height:8px; overflow:hidden; margin:8px 0; }
.checklist-progress-bar { background:#2D6A4F; height:100%; border-radius:8px; transition:width 0.3s; }

/* Google button */
.google-btn { display:flex; align-items:center; justify-content:center; gap:10px;
              background:white; color:#1a1a1a; border:1.5px solid #e5e7eb;
              border-radius:10px; padding:10px 20px; font-weight:600; font-size:14px;
              cursor:pointer; width:100%; transition:box-shadow 0.2s; }
.google-btn:hover { box-shadow:0 2px 8px rgba(0,0,0,0.12); }
.divider-text { text-align:center; color:#9ca3af; font-size:13px; margin:12px 0; position:relative; }
.divider-text::before, .divider-text::after { content:''; position:absolute; top:50%;
    width:42%; height:1px; background:#e5e7eb; }
.divider-text::before { left:0; } .divider-text::after { right:0; }
</style>
""", unsafe_allow_html=True)

# ─── Session state ─────────────────────────────────────────────────────────────
for k, v in {"token": None, "user_email": None, "page": "dashboard",
              "selected_plant": None, "pending_diagnosis": None, "chat_messages": []}.items():
    if k not in st.session_state:
        st.session_state[k] = v


def nav(page):
    st.session_state.page = page
    st.session_state.pending_diagnosis = None
    st.rerun()


def back_button():
    col, _ = st.columns([1, 7])
    with col:
        if st.button("← Dashboard", key="back_to_dash", type="secondary"):
            nav("dashboard")
    st.markdown('<div style="height:4px"></div>', unsafe_allow_html=True)


def badge(status):
    cls = {"healthy":"badge-healthy","recovering":"badge-recovering","critical":"badge-critical"}.get(status,"badge-unknown")
    label = {"healthy":"✓ Healthy","recovering":"● Recovering","critical":"! Critical"}.get(status,"● Unknown")
    return f'<span class="badge {cls}">{label}</span>'


def category_icon(cat):
    return {"water":"💧","light":"☀️","pest":"🐛","nutrient":"🌱","disease":"🦠","healthy":"✅"}.get(cat,"🔍")


# ══════════════════════════════════════════════════════════════════════════════
# OAUTH CALLBACK HANDLER — must run before anything else
# ══════════════════════════════════════════════════════════════════════════════
params = st.query_params
if "access_token" in params and st.session_state.token is None:
    with st.spinner("Logging you in with Google..."):
        try:
            r = api.google_callback(params["access_token"])
            if r.status_code == 200:
                st.session_state.token = r.json()["access_token"]
                # Try to get email from token payload
                import base64, json as _json
                try:
                    payload_b64 = params["access_token"].split(".")[1]
                    payload_b64 += "=" * (4 - len(payload_b64) % 4)
                    payload = _json.loads(base64.b64decode(payload_b64))
                    st.session_state.user_email = payload.get("email", "user@google.com")
                except Exception:
                    st.session_state.user_email = "user@google.com"
                st.query_params.clear()
                st.rerun()
            else:
                st.error("Google login failed. Please try again.")
                st.query_params.clear()
        except Exception as e:
            st.error(f"Login error: {e}")
            st.query_params.clear()


# ══════════════════════════════════════════════════════════════════════════════
# AUTH SCREEN
# ══════════════════════════════════════════════════════════════════════════════
def auth_screen():
    _, col, _ = st.columns([1, 1.2, 1])
    with col:
        st.markdown("""
        <div style="text-align:center;margin-bottom:32px">
            <div style="font-size:56px">🌿</div>
            <div style="font-size:28px;font-weight:800;color:#2D6A4F;margin:8px 0 4px">Plant Doctor</div>
            <div style="font-size:14px;color:#6b7280">AI-powered plant diagnosis and care guidance</div>
        </div>""", unsafe_allow_html=True)

        tab_login, tab_signup = st.tabs(["  Login  ", "  Sign Up  "])

        with tab_login:
            st.markdown('<div style="height:12px"></div>', unsafe_allow_html=True)

            # ── Google OAuth button ──
           ''' google_col, _ = st.columns([1, 0.01])
            with google_col:
                if st.button("🔵  Continue with Google", key="google_login", use_container_width=True):
                          try:
                              r = api.get_google_url()
                              st.write("Status:", r.status_code)
                              st.write("URL:", r.json())
                          except Exception as e:
                              st.error(f"Error: {e}")

                      #st.markdown('<div class="divider-text">or continue with email</div>', unsafe_allow_html=True)

            with st.form("login_form"):
                email = st.text_input("Email", placeholder="you@example.com", key="li_email")
                password = st.text_input("Password", type="password", placeholder="Enter your password")
                if st.form_submit_button("Login", use_container_width=True):
                    r = api.login(email, password)
                    if r.status_code == 200:
                        st.session_state.token = r.json()["access_token"]
                        st.session_state.user_email = email
                        st.rerun()
                    else:
                        st.error(r.json().get("detail", "Login failed"))

        with tab_signup:
            st.markdown('<div style="height:12px"></div>', unsafe_allow_html=True)

            if st.button("🔵  Sign up with Google", key="google_signup", use_container_width=True):
                try:
                    r = api.get_google_url()
                    if r.status_code == 200:
                        st.markdown(
                            f'<meta http-equiv="refresh" content="0;url={r.json()["url"]}">',
                            unsafe_allow_html=True)
                        st.info("Redirecting to Google...")
                    else:
                        st.error("Could not get Google login URL.")
                except Exception as e:
                    st.error(f"Error: {e}")

            st.markdown('<div class="divider-text">or sign up with email</div>', unsafe_allow_html=True)

            with st.form("signup_form"):
                email2 = st.text_input("Email", placeholder="you@example.com", key="su_email")
                password2 = st.text_input("Password", type="password", placeholder="Create a password")
                if st.form_submit_button("Create Account", use_container_width=True):
                    r = api.signup(email2, password2)
                    if r.status_code == 201:
                        st.success("Account created! Please log in.")
                    else:
                        st.error(r.json().get("detail", "Signup failed"))'''


# ══════════════════════════════════════════════════════════════════════════════
# SIDEBAR
# ══════════════════════════════════════════════════════════════════════════════
def sidebar(plants):
    with st.sidebar:
        st.markdown("""
        <div style="display:flex;align-items:center;gap:10px;padding:8px 0 24px">
            <div style="background:#2D6A4F;color:white;width:36px;height:36px;border-radius:10px;
                 display:flex;align-items:center;justify-content:center;font-size:18px">🌿</div>
            <div style="font-size:18px;font-weight:700;color:#1a1a1a">Plant Doctor</div>
        </div>""", unsafe_allow_html=True)

        email = st.session_state.user_email or ""
        name = email.split("@")[0].capitalize()
        st.markdown(f"""
        <div style="background:#f0f7f0;border-radius:10px;padding:10px 12px;margin-bottom:20px">
            <div style="font-weight:600;font-size:13px;color:#1a1a1a">👤 {name}</div>
            <div style="font-size:11px;color:#6b7280">{email}</div>
        </div>""", unsafe_allow_html=True)

        page = st.session_state.page
        for key, icon, label in [
            ("dashboard","🏠","Dashboard"), ("my_plants","🌿","My Plants"),
            ("diagnose","🔬","Diagnose"), ("care_plans","📋","Care Plans"),
            ("checkin","📅","Check-in"), ("gallery","🖼️","Gallery"),
        ]:
            if st.button(f"{icon}  {label}", key=f"nav_{key}", use_container_width=True):
                nav(key)

        st.divider()
        if plants:
            plant_names = {p["id"]: p["name"] for p in plants}
            if st.session_state.selected_plant not in plant_names:
                st.session_state.selected_plant = plants[0]["id"]
            selected = st.selectbox("Active Plant",
                options=list(plant_names.keys()),
                format_func=lambda i: f"🌱 {plant_names[i]}",
                index=list(plant_names.keys()).index(st.session_state.selected_plant))
            st.session_state.selected_plant = selected

        st.markdown('<div style="height:8px"></div>', unsafe_allow_html=True)
        if st.button("🚪  Logout", use_container_width=True, key="nav_logout"):
            for k in list(st.session_state.keys()):
                del st.session_state[k]
            st.rerun()


# ══════════════════════════════════════════════════════════════════════════════
# DASHBOARD
# ══════════════════════════════════════════════════════════════════════════════
def page_dashboard(plants):
    email = st.session_state.user_email or ""
    name = email.split("@")[0].capitalize()
    st.markdown(f"""
    <div class="page-header">
        <h1>Welcome back, {name}! 🌿</h1>
        <p>Here's how your plants are doing today.</p>
    </div>""", unsafe_allow_html=True)

    main_col, side_col = st.columns([2.5, 1])
    with main_col:
        healthy = sum(1 for p in plants if p["status"]=="healthy")
        recovering = sum(1 for p in plants if p["status"]=="recovering")
        critical = sum(1 for p in plants if p["status"]=="critical")
        c1,c2,c3,c4 = st.columns(4)
        for col, label, val, color in [
            (c1,"Total Plants",len(plants),"#2D6A4F"),
            (c2,"Healthy",healthy,"#059669"),
            (c3,"Recovering",recovering,"#d97706"),
            (c4,"Critical",critical,"#dc2626"),
        ]:
            col.markdown(f"""
            <div class="pd-card" style="text-align:center;padding:18px 12px">
                <div style="font-size:28px;font-weight:800;color:{color}">{val}</div>
                <div style="font-size:12px;color:#6b7280;font-weight:500">{label}</div>
            </div>""", unsafe_allow_html=True)

        st.markdown("### My Plants")
        if not plants:
            st.markdown("""
            <div class="pd-card" style="text-align:center;padding:40px">
                <div style="font-size:48px">🌱</div>
                <div style="font-weight:600;margin:12px 0 6px">No plants yet</div>
                <div style="color:#6b7280;font-size:14px">Add your first plant to get started</div>
            </div>""", unsafe_allow_html=True)
        else:
            cols = st.columns(3)
            for i, plant in enumerate(plants[:6]):
                with cols[i % 3]:
                    st.markdown(f"""
                    <div class="plant-card">
                        <div style="background:#e8f5e9;height:120px;display:flex;align-items:center;
                             justify-content:center;font-size:48px">🌿</div>
                        <div style="padding:14px">
                            <div style="font-weight:700;font-size:15px">{plant['name']}</div>
                            <div style="color:#6b7280;font-size:12px;margin-bottom:8px">
                                {plant.get('species') or 'Unknown species'}</div>
                            {badge(plant['status'])}
                            <div style="font-size:11px;color:#9ca3af;margin-top:6px">
                                📍 {plant.get('location') or '—'}</div>
                        </div>
                    </div>""", unsafe_allow_html=True)
                    if st.button("View", key=f"dash_view_{plant['id']}", use_container_width=True):
                        st.session_state.selected_plant = plant["id"]
                        nav("diagnose")
            if len(plants) < 6:
                with cols[len(plants) % 3]:
                    st.markdown("""
                    <div class="plant-card" style="border:2px dashed #d1d5db;background:#fafafa;
                         text-align:center;padding:40px 0">
                        <div style="font-size:32px;color:#9ca3af">＋</div>
                        <div style="font-size:13px;color:#9ca3af;margin-top:4px">Add New Plant</div>
                    </div>""", unsafe_allow_html=True)
                    if st.button("Add Plant", key="dash_add", use_container_width=True):
                        nav("my_plants")

    with side_col:
        st.markdown("### Quick Actions")
        for label, page in [("🔬  Diagnose a Plant","diagnose"),
                             ("📅  Weekly Check-in","checkin"),
                             ("➕  Add New Plant","my_plants")]:
            if st.button(label, use_container_width=True, key=f"qa_{page}"):
                nav(page)
        if plants:
            st.markdown("### Recent Activity")
            for plant in plants[:3]:
                st.markdown(f"""
                <div class="pd-card" style="padding:12px 14px;margin-bottom:8px">
                    <div style="display:flex;justify-content:space-between;align-items:center">
                        <div>
                            <div style="font-weight:600;font-size:13px">{plant['name']}</div>
                            <div style="font-size:11px;color:#6b7280">{plant.get('location') or '—'}</div>
                        </div>
                        {badge(plant['status'])}
                    </div>
                </div>""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# MY PLANTS
# ══════════════════════════════════════════════════════════════════════════════
def page_my_plants(plants):
    back_button()
    st.markdown("""
    <div class="page-header">
        <h1>🌿 My Plants</h1><p>Manage your plant collection</p>
    </div>""", unsafe_allow_html=True)

    left, right = st.columns([1, 1.8])
    with left:
        st.markdown('<div class="pd-card"><div style="font-weight:700;font-size:16px;margin-bottom:16px">➕ Add New Plant</div>', unsafe_allow_html=True)
        with st.form("add_plant_form", clear_on_submit=True):
            name = st.text_input("Plant Name *", placeholder="e.g. Money Plant")
            species = st.text_input("Species (optional)", placeholder="e.g. Pothos")
            location = st.text_input("Location (optional)", placeholder="e.g. Living Room")
            if st.form_submit_button("Save Plant", use_container_width=True):
                if name:
                    api.create_plant(name, species, location)
                    st.success(f"✅ {name} added!")
                    st.rerun()
                else:
                    st.error("Plant name is required")
        st.markdown('</div>', unsafe_allow_html=True)

    with right:
        if not plants:
            st.markdown("""
            <div class="pd-card" style="text-align:center;padding:60px">
                <div style="font-size:56px">🌱</div>
                <div style="font-weight:600;margin:12px 0 6px;font-size:18px">No plants yet</div>
            </div>""", unsafe_allow_html=True)
        else:
            for plant in plants:
                col_info, col_action = st.columns([3, 1])
                with col_info:
                    st.markdown(f"""
                    <div class="pd-card" style="margin-bottom:4px">
                        <div style="display:flex;align-items:center;gap:16px">
                            <div style="font-size:36px">🌿</div>
                            <div style="flex:1">
                                <div style="font-weight:700;font-size:15px">{plant['name']}</div>
                                <div style="color:#6b7280;font-size:13px">{plant.get('species') or 'Unknown species'}</div>
                                <div style="margin-top:6px;display:flex;gap:8px;align-items:center">
                                    {badge(plant['status'])}
                                    <span style="font-size:12px;color:#9ca3af">📍 {plant.get('location') or '—'}</span>
                                </div>
                            </div>
                        </div>
                    </div>""", unsafe_allow_html=True)
                with col_action:
                    st.markdown('<div style="height:16px"></div>', unsafe_allow_html=True)
                    if st.button("🔬 Diagnose", key=f"goto_diag_{plant['id']}", use_container_width=True):
                        st.session_state.selected_plant = plant["id"]
                        nav("diagnose")
                    if st.button("🗑️ Delete", key=f"del_{plant['id']}", use_container_width=True):
                        api.delete_plant(plant["id"])
                        st.rerun()


# ══════════════════════════════════════════════════════════════════════════════
# DIAGNOSE
# ══════════════════════════════════════════════════════════════════════════════
def page_diagnose(plant):
    back_button()
    st.markdown(f"""
    <div class="page-header">
        <h1>🔬 Diagnose Plant</h1>
        <p>Upload a photo of <strong>{plant['name']}</strong> and describe the issue</p>
    </div>""", unsafe_allow_html=True)

    pending = st.session_state.pending_diagnosis

    if pending and pending.get("plant_id") == plant["id"]:
        left, right = st.columns([1.2, 1])
        with left:
            st.markdown('<div class="pd-card">', unsafe_allow_html=True)
            st.markdown("#### 🤖 Plant Doctor Assistant")
            st.caption("Answer a few questions to get the best care plan")
            diag = pending["diagnosis"]
            cat = diag.get("symptom_category", "unknown")
            st.markdown(f"""
            <div style="background:#f0f7f0;border-radius:10px;padding:12px 16px;margin:8px 0 16px">
                <div style="font-size:12px;color:#6b7280;margin-bottom:4px">Issue Detected</div>
                <div style="font-size:18px;font-weight:700;color:#dc2626">
                    {category_icon(cat)} {cat.title()}</div>
                <div style="font-size:13px;color:#374151;margin-top:6px">{diag.get('diagnosis_text','')}</div>
            </div>""", unsafe_allow_html=True)

            msgs = st.session_state.chat_messages
            if not msgs:
                for q in pending["questions"]:
                    st.session_state.chat_messages.append({"role":"bot","text":q})
                msgs = st.session_state.chat_messages

            for msg in msgs:
                if msg["role"] == "bot":
                    st.markdown(f"""
                    <div class="chat-bot">
                        <div class="chat-bot-icon">🌿</div>
                        <div><div class="chat-bubble-bot">{msg['text']}</div></div>
                    </div><br>""", unsafe_allow_html=True)
                else:
                    st.markdown(f"""
                    <div style="text-align:right;margin-bottom:8px">
                        <div class="chat-bubble-user" style="display:inline-block">{msg['text']}</div>
                    </div>""", unsafe_allow_html=True)

            answered = [m for m in msgs if m["role"] == "user"]
            questions = pending["questions"]
            if len(answered) < len(questions):
                answer = st.text_input(
                    f"Your answer ({len(answered)+1}/{len(questions)})",
                    placeholder="Type your answer...", key=f"chat_ans_{len(answered)}")
                if st.button("Send ➤", key=f"send_{len(answered)}"):
                    if answer.strip():
                        st.session_state.chat_messages.append({"role":"user","text":answer})
                        st.rerun()
            else:
                all_answers = [m["text"] for m in msgs if m["role"] == "user"]
                st.markdown('<div style="height:8px"></div>', unsafe_allow_html=True)
                if st.button("✅ Get My Care Plan", use_container_width=True):
                    with st.spinner("Generating your personalised care plan..."):
                        api.answer_clarifying(plant["id"], all_answers)
                    st.session_state.pending_diagnosis = None
                    st.session_state.chat_messages = []
                    nav("care_plans")
            st.markdown('</div>', unsafe_allow_html=True)

        with right:
            st.markdown(f"""
            <div class="pd-card">
                <div style="font-size:12px;color:#6b7280;margin-bottom:4px">Identified Species</div>
                <div style="font-size:16px;font-weight:700;color:#1a1a1a;margin-bottom:12px">
                    🌿 {diag.get('species_guess') or 'Unknown'}</div>
                <div style="font-size:12px;color:#6b7280;margin-bottom:4px">Issue Category</div>
                <div style="font-size:18px;font-weight:700;color:#dc2626">
                    {category_icon(diag.get('symptom_category',''))} {(diag.get('symptom_category') or 'Unknown').title()}</div>
                <div style="margin-top:16px">
                    <div style="font-size:12px;color:#6b7280;margin-bottom:8px">Possible Causes</div>
                    <div style="font-size:14px;color:#374151;line-height:2">
                        ✅ Check watering schedule<br>
                        ✅ Review light conditions<br>
                        ✅ Inspect soil drainage
                    </div>
                </div>
            </div>""", unsafe_allow_html=True)
        return

    left, right = st.columns([1.2, 1])
    with left:
        st.markdown('<div class="pd-card">', unsafe_allow_html=True)
        st.markdown("#### Upload Plant Photo")
        uploaded = st.file_uploader("Photo", type=["jpg","jpeg","png"],
                                     key=f"diag_upload_{plant['id']}", label_visibility="collapsed")
        if uploaded:
            st.image(uploaded, use_column_width=True)
        else:
            st.markdown("""
            <div style="border:2px dashed #d1d5db;border-radius:12px;padding:48px;text-align:center;
                        background:#fafafa;margin:8px 0">
                <div style="font-size:36px;color:#9ca3af">📷</div>
                <div style="font-size:14px;color:#9ca3af;margin-top:8px">
                    Drag & drop an image here<br>or click to browse</div>
                <div style="font-size:11px;color:#d1d5db;margin-top:6px">JPG, PNG up to 10MB</div>
            </div>""", unsafe_allow_html=True)

        st.markdown("#### Describe the Issue *(optional)*")
        note = st.text_area("", placeholder="Leaves are turning yellow and some are brown...",
                             height=100, key=f"diag_note_{plant['id']}", label_visibility="collapsed")
        st.caption(f"{len(note)}/300")

        if st.button("🔬 Analyze Plant", disabled=uploaded is None, use_container_width=True):
            with st.spinner("Analyzing your plant photo with AI..."):
                result = api.diagnose(plant["id"], uploaded.getvalue(), uploaded.name, note)
            if result["status"] == "clarifying":
                st.session_state.pending_diagnosis = {
                    "plant_id": plant["id"],
                    "diagnosis": result["diagnosis"],
                    "questions": result["questions"],
                }
                st.session_state.chat_messages = []
                st.rerun()
            else:
                st.success("✅ Diagnosis complete!")
                nav("care_plans")
        st.markdown('</div>', unsafe_allow_html=True)

    with right:
        st.markdown(f"""
        <div class="pd-card">
            <div style="font-size:16px;font-weight:700;margin-bottom:16px">🌱 {plant['name']}</div>
            <div style="display:grid;gap:10px">
                <div><div style="font-size:11px;color:#9ca3af;font-weight:600;text-transform:uppercase">Species</div>
                     <div style="font-size:14px;margin-top:2px">{plant.get('species') or 'Auto-detected from photo'}</div></div>
                <div><div style="font-size:11px;color:#9ca3af;font-weight:600;text-transform:uppercase">Location</div>
                     <div style="font-size:14px;margin-top:2px">{plant.get('location') or '—'}</div></div>
                <div><div style="font-size:11px;color:#9ca3af;font-weight:600;text-transform:uppercase">Status</div>
                     <div style="margin-top:4px">{badge(plant['status'])}</div></div>
            </div>
        </div>
        <div class="pd-card">
            <div style="font-weight:600;margin-bottom:10px">💡 Tips for a great photo</div>
            <div style="font-size:13px;color:#374151;line-height:1.8">
                ✓ Use natural daylight<br>✓ Show affected leaves clearly<br>
                ✓ Include whole plant if possible<br>✓ Avoid blurry or dark images
            </div>
        </div>""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# CARE PLANS
# ══════════════════════════════════════════════════════════════════════════════
def page_care_plans(plant):
    back_button()
    st.markdown(f"""
    <div class="page-header">
        <h1>📋 Recovery Care Plan</h1>
        <p>Follow these steps to help <strong>{plant['name']}</strong> recover</p>
    </div>""", unsafe_allow_html=True)

    plans = api.list_care_plans(plant["id"])
    if not plans:
        st.markdown("""
        <div class="pd-card" style="text-align:center;padding:60px">
            <div style="font-size:56px">📋</div>
            <div style="font-weight:600;margin:12px 0 6px;font-size:18px">No care plans yet</div>
            <div style="color:#6b7280;margin-bottom:24px">Run a diagnosis first</div>
        </div>""", unsafe_allow_html=True)
        if st.button("🔬 Go to Diagnose"):
            nav("diagnose")
        return

    plan = plans[0]
    checklist = plan.get("checklist", [])
    done_count = sum(1 for c in checklist if c.get("done"))
    total = len(checklist)
    pct = int(done_count / total * 100) if total else 0

    left, right = st.columns([1.5, 1])
    with left:
        st.markdown(f"""
        <div class="recovery-banner">
            <div style="font-size:28px">📅</div>
            <div>
                <div style="font-size:11px;color:#2D6A4F;font-weight:600;text-transform:uppercase">Expected Recovery Time</div>
                <div class="recovery-days">{plan.get('expected_recovery','1–2 weeks')}</div>
            </div>
        </div>
        <div class="pd-card">
            <div style="font-size:15px;color:#374151;line-height:1.6">{plan['plan_text']}</div>
        </div>
        <div class="pd-card">
            <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:8px">
                <div style="font-weight:700">Care Checklist</div>
                <div style="font-size:13px;color:#6b7280">{done_count}/{total} &nbsp; <strong style="color:#2D6A4F">{pct}%</strong></div>
            </div>
            <div class="checklist-progress">
                <div class="checklist-progress-bar" style="width:{pct}%"></div>
            </div>
        </div>""", unsafe_allow_html=True)

        updated = list(checklist)
        changed = False
        for j, item in enumerate(checklist):
            checked = st.checkbox(item["item"], value=item["done"], key=f"chk_{plan['id']}_{j}")
            if checked != item["done"]:
                updated[j] = {**item, "done": checked}
                changed = True
        if changed:
            api.update_checklist(plant["id"], plan["id"], updated)
            st.rerun()

        st.markdown("""
        <div style="background:#f0f7f0;border-radius:10px;padding:12px 16px;margin-top:8px;font-size:13px;color:#2D6A4F">
            💡 <strong>Tip:</strong> Check back in a week to update your progress!
        </div>""", unsafe_allow_html=True)

    with right:
        st.markdown("#### Plan History")
        for i, p in enumerate(plans):
            st.markdown(f"""
            <div class="pd-card" style="border-left:3px solid {'#2D6A4F' if i==0 else '#e5e7eb'};
                 padding:12px 14px;margin-bottom:8px">
                <div style="font-weight:600;font-size:13px">{'📌 Current Plan' if i==0 else f'Plan {i+1}'}</div>
                <div style="font-size:11px;color:#9ca3af">{p['created_at'][:10]}</div>
                <div style="font-size:12px;color:#6b7280;margin-top:4px">Recovery: {p.get('expected_recovery','—')}</div>
            </div>""", unsafe_allow_html=True)
        if st.button("📅 Run Weekly Check-in", use_container_width=True):
            nav("checkin")


# ══════════════════════════════════════════════════════════════════════════════
# WEEKLY CHECK-IN
# ══════════════════════════════════════════════════════════════════════════════
def page_checkin(plant):
    back_button()
    st.markdown(f"""
    <div class="page-header">
        <h1>📅 Weekly Check-in</h1>
        <p>Track <strong>{plant['name']}</strong>'s progress over time</p>
    </div>""", unsafe_allow_html=True)

    if not api.list_diagnoses(plant["id"]):
        st.info("Run a diagnosis first before doing a weekly check-in.")
        if st.button("🔬 Go to Diagnose"):
            nav("diagnose")
        return

    left, right = st.columns([1.2, 1])
    with left:
        st.markdown('<div class="pd-card">', unsafe_allow_html=True)
        st.markdown("#### Upload Today's Photo")
        uploaded = st.file_uploader("New photo", type=["jpg","jpeg","png"],
                                     key=f"ci_{plant['id']}", label_visibility="collapsed")
        if uploaded:
            st.image(uploaded, use_column_width=True)
        note = st.text_area("Any changes you've noticed?",
                             placeholder="e.g. Yellowing has reduced, new leaves growing...",
                             height=80, key=f"ci_note_{plant['id']}")
        if st.button("📸 Submit Check-in", disabled=uploaded is None,
                     use_container_width=True, key="ci_submit"):
            with st.spinner("Comparing with last photo and updating care plan..."):
                api.weekly_checkin(plant["id"], uploaded.getvalue(), uploaded.name, note)
            st.success("✅ Check-in complete! Care plan updated.")
            nav("care_plans")
        st.markdown('</div>', unsafe_allow_html=True)

    with right:
        photos = api.list_photos(plant["id"])
        if len(photos) >= 2:
            st.markdown("#### Photo Comparison")
            col1, arrow_col, col2 = st.columns([5, 1, 5])
            with col1:
                try:
                    st.image(api.photo_url(photos[-2]["filepath"]), use_column_width=True)
                    st.caption(f"Previous\n{photos[-2]['taken_at'][:10]}")
                except Exception:
                    st.caption("📷 Previous photo")
            with arrow_col:
                st.markdown("<div style='text-align:center;font-size:24px;margin-top:40px'>→</div>",
                            unsafe_allow_html=True)
            with col2:
                try:
                    st.image(api.photo_url(photos[-1]["filepath"]), use_column_width=True)
                    st.caption(f"Latest\n{photos[-1]['taken_at'][:10]}")
                except Exception:
                    st.caption("📷 Latest photo")

        plans = api.list_care_plans(plant["id"])
        if plans:
            checklist = plans[0].get("checklist", [])
            done = sum(1 for c in checklist if c.get("done"))
            total = len(checklist)
            score = int(done / total * 100) if total else 0
            prev_score = max(0, score - 17)
            st.markdown(f"""
            <div class="pd-card" style="margin-top:16px">
                <div style="font-weight:700;margin-bottom:12px">📈 Health Score</div>
                <div style="display:flex;align-items:center;gap:12px;margin-bottom:8px">
                    <span style="color:#6b7280;font-size:14px">{prev_score}%</span>
                    <div style="flex:1;background:#e5e7eb;border-radius:8px;height:10px;overflow:hidden">
                        <div style="background:linear-gradient(90deg,#059669,#2D6A4F);
                             height:100%;width:{score}%;border-radius:8px"></div>
                    </div>
                    <span style="color:#2D6A4F;font-weight:700;font-size:16px">{score}%</span>
                </div>
                <div style="display:flex;justify-content:space-between;font-size:11px;color:#9ca3af">
                    <span>Last week</span><span>This week</span>
                </div>
            </div>""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# GALLERY
# ══════════════════════════════════════════════════════════════════════════════
def page_gallery(plant):
    back_button()
    st.markdown(f"""
    <div class="page-header">
        <h1>🖼️ Photo Gallery</h1>
        <p>Visual recovery timeline for <strong>{plant['name']}</strong></p>
    </div>""", unsafe_allow_html=True)

    photos = api.list_photos(plant["id"])
    if not photos:
        st.markdown("""
        <div class="pd-card" style="text-align:center;padding:60px">
            <div style="font-size:56px">📷</div>
            <div style="font-weight:600;margin:12px 0 6px;font-size:18px">No photos yet</div>
            <div style="color:#6b7280">Photos appear here after diagnosis</div>
        </div>""", unsafe_allow_html=True)
        return

    st.markdown(f"""
    <div class="pd-card" style="margin-bottom:16px">
        <div style="display:flex;justify-content:space-between;align-items:center">
            <div style="font-weight:700">{len(photos)} photos in recovery timeline</div>
            <div style="font-size:13px;color:#6b7280">Oldest → Newest</div>
        </div>
    </div>""", unsafe_allow_html=True)

    cols = st.columns(4)
    for i, photo in enumerate(photos):
        with cols[i % 4]:
            try:
                st.image(api.photo_url(photo["filepath"]), use_column_width=True)
            except Exception:
                st.markdown("""
                <div style="background:#f3f4f6;border-radius:10px;height:140px;display:flex;
                     align-items:center;justify-content:center;font-size:32px">📷</div>""",
                    unsafe_allow_html=True)
            st.caption(f"📅 {photo['taken_at'][:10]}")
            if photo.get("note"):
                st.caption(f"💬 {photo['note'][:40]}")


# ══════════════════════════════════════════════════════════════════════════════
# MAIN
# ══════════════════════════════════════════════════════════════════════════════
if st.session_state.token is None:
    auth_screen()
else:
    try:
        plants = api.list_plants()
    except Exception:
        plants = []

    selected_id = st.session_state.selected_plant
    if plants and not selected_id:
        st.session_state.selected_plant = plants[0]["id"]
        selected_id = plants[0]["id"]
    plant = next((p for p in plants if p["id"] == selected_id), plants[0] if plants else None)

    sidebar(plants)

    page = st.session_state.page
    if page == "dashboard":
        page_dashboard(plants)
    elif page == "my_plants":
        page_my_plants(plants)
    elif page == "diagnose":
        if plant: page_diagnose(plant)
        else:
            st.info("Add a plant first.")
            if st.button("➕ Add Plant"): nav("my_plants")
    elif page == "care_plans":
        if plant: page_care_plans(plant)
        else: st.info("Add a plant first.")
    elif page == "checkin":
        if plant: page_checkin(plant)
        else: st.info("Add a plant first.")
    elif page == "gallery":
        if plant: page_gallery(plant)
        else: st.info("Add a plant first.")
