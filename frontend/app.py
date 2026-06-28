import streamlit as st
import api_client as api
import json

st.set_page_config(page_title="Plant Doctor", page_icon="🌿", layout="wide")

# ─── Global CSS ───────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

html, body, [class*="css"] { font-family: 'Inter', sans-serif; }

/* Background */
.stApp { background: #f4f7f4; }

/* Hide streamlit chrome */
#MainMenu, footer, header { visibility: hidden; }
.block-container { padding: 0 !important; max-width: 100% !important; }

/* ── Cards ── */
.pd-card {
    background: white;
    border-radius: 16px;
    padding: 24px;
    margin-bottom: 16px;
    box-shadow: 0 1px 4px rgba(0,0,0,0.08);
}

/* ── Sidebar ── */
section[data-testid="stSidebar"] {
    background: white !important;
    border-right: 1px solid #e8f0e8;
    min-width: 240px !important;
    max-width: 240px !important;
}
section[data-testid="stSidebar"] .block-container { padding: 24px 16px !important; }

/* ── Buttons (primary only) ── */
button[data-testid="baseButton-primary"],
.stButton > button:not([data-testid="baseButton-secondary"]) {
    background: #2D6A4F !important;
    color: white !important;
    border: none !important;
    border-radius: 10px !important;
    font-weight: 600 !important;
    padding: 10px 20px !important;
    width: 100%;
    transition: background 0.2s;
}
button[data-testid="baseButton-primary"]:hover { background: #1B4332 !important; }

/* ── Back to Dashboard button (secondary type) ── */
button[data-testid="baseButton-secondary"] {
    background: white !important;
    color: #2D6A4F !important;
    border: 1.5px solid #2D6A4F !important;
    border-radius: 10px !important;
    font-size: 13px !important;
    font-weight: 500 !important;
    padding: 5px 16px !important;
    width: auto !important;
    transition: background 0.2s;
}
button[data-testid="baseButton-secondary"]:hover { background: #f0f7f0 !important; }

/* Secondary button */
.btn-secondary > button {
    background: #f0f7f0 !important;
    color: #2D6A4F !important;
    border: 1.5px solid #2D6A4F !important;
}

/* ── Status badges ── */
.badge {
    display: inline-block;
    padding: 3px 12px;
    border-radius: 20px;
    font-size: 12px;
    font-weight: 600;
}
.badge-healthy   { background: #d1fae5; color: #065f46; }
.badge-recovering{ background: #fef3c7; color: #92400e; }
.badge-critical  { background: #fee2e2; color: #991b1b; }
.badge-unknown   { background: #f3f4f6; color: #6b7280; }

/* ── Plant cards ── */
.plant-card {
    background: white;
    border-radius: 16px;
    overflow: hidden;
    box-shadow: 0 1px 4px rgba(0,0,0,0.08);
    transition: transform 0.2s, box-shadow 0.2s;
    cursor: pointer;
}
.plant-card:hover { transform: translateY(-2px); box-shadow: 0 4px 12px rgba(0,0,0,0.12); }
.plant-card-img { width: 100%; height: 140px; object-fit: cover; background: #e8f5e9; 
                  display:flex; align-items:center; justify-content:center; font-size:48px; }
.plant-card-body { padding: 14px; }
.plant-card-name { font-size: 15px; font-weight: 700; color: #1a1a1a; margin: 0 0 2px 0; }
.plant-card-species { font-size: 12px; color: #6b7280; margin: 0 0 8px 0; }
.plant-card-meta { font-size: 11px; color: #9ca3af; }

/* ── Input fields ── */
.stTextInput > div > div > input, .stTextArea > div > div > textarea {
    border-radius: 10px !important;
    border: 1.5px solid #e5e7eb !important;
    font-family: 'Inter', sans-serif !important;
}
.stTextInput > div > div > input:focus, .stTextArea > div > div > textarea:focus {
    border-color: #2D6A4F !important;
    box-shadow: 0 0 0 3px rgba(45,106,79,0.1) !important;
}

/* ── Page header ── */
.page-header {
    background: white;
    padding: 20px 32px;
    border-bottom: 1px solid #e8f0e8;
    display: flex;
    align-items: center;
    gap: 16px;
    margin-bottom: 24px;
}
.page-header h1 { margin: 0; font-size: 20px; font-weight: 700; color: #1a1a1a; }
.page-header p  { margin: 0; font-size: 13px; color: #6b7280; }

/* ── Chat bubbles ── */
.chat-container { display: flex; flex-direction: column; gap: 12px; padding: 16px 0; }
.chat-bot { display: flex; gap: 10px; align-items: flex-start; }
.chat-bot-icon { background: #2D6A4F; color: white; width: 32px; height: 32px; border-radius: 50%;
                  display:flex; align-items:center; justify-content:center; font-size:14px; flex-shrink:0; }
.chat-bubble-bot { background: #f0f7f0; border-radius: 0 12px 12px 12px;
                    padding: 10px 14px; font-size: 14px; color: #1a1a1a; max-width: 75%; }
.chat-bubble-user { background: #2D6A4F; color: white; border-radius: 12px 0 12px 12px;
                     padding: 10px 14px; font-size: 14px; max-width: 75%; margin-left: auto; }
.chat-time { font-size: 10px; color: #9ca3af; margin-top: 4px; }

/* ── Diagnosis result ── */
.diagnosis-card { background: white; border-radius: 16px; padding: 20px; margin-bottom: 12px;
                   box-shadow: 0 1px 4px rgba(0,0,0,0.08); }
.issue-label { font-size: 13px; color: #6b7280; font-weight: 500; margin-bottom: 4px; }
.issue-value { font-size: 18px; font-weight: 700; color: #dc2626; }
.cause-item { display: flex; align-items: center; gap: 8px; padding: 6px 0;
               font-size: 14px; color: #374151; border-bottom: 1px solid #f3f4f6; }

/* ── Care checklist ── */
.checklist-progress { background: #f3f4f6; border-radius: 8px; height: 8px; overflow: hidden; margin: 8px 0; }
.checklist-progress-bar { background: #2D6A4F; height: 100%; border-radius: 8px; transition: width 0.3s; }

/* ── Health score ── */
.health-score-bar { background: #e5e7eb; border-radius: 8px; height: 10px; overflow: hidden; }
.health-score-fill { height: 100%; border-radius: 8px; }

/* ── Logo ── */
.sidebar-logo { display: flex; align-items: center; gap: 10px; padding: 8px 0 24px; }
.sidebar-logo-icon { background: #2D6A4F; color: white; width: 36px; height: 36px;
                      border-radius: 10px; display:flex; align-items:center; justify-content:center; font-size:18px; }
.sidebar-logo-text { font-size: 18px; font-weight: 700; color: #1a1a1a; }
.sidebar-logo-sub { font-size: 11px; color: #6b7280; }

/* ── Nav items ── */
.nav-item { display: flex; align-items: center; gap: 10px; padding: 10px 12px;
             border-radius: 10px; font-size: 14px; font-weight: 500; color: #374151;
             cursor: pointer; margin-bottom: 2px; transition: background 0.15s; }
.nav-item:hover { background: #f0f7f0; color: #2D6A4F; }
.nav-item.active { background: #f0f7f0; color: #2D6A4F; font-weight: 600; }
.nav-icon { font-size: 16px; width: 20px; text-align: center; }

/* ── Recovery time ── */
.recovery-banner { background: #f0f7f0; border-radius: 12px; padding: 16px 20px;
                    display: flex; align-items: center; gap: 14px; margin-bottom: 16px; }
.recovery-days { font-size: 28px; font-weight: 800; color: #2D6A4F; }

/* ── Auth page ── */
.auth-container { max-width: 420px; margin: 60px auto; }
.auth-logo { text-align: center; margin-bottom: 32px; }
.auth-title { font-size: 28px; font-weight: 800; color: #2D6A4F; margin: 8px 0 4px; }
.auth-sub { font-size: 14px; color: #6b7280; }

/* ── Weekly comparison ── */
.compare-grid { display: grid; grid-template-columns: 1fr auto 1fr; gap: 12px; align-items: center; }
.compare-arrow { font-size: 24px; color: #2D6A4F; text-align: center; }
.compare-label { font-size: 11px; color: #9ca3af; text-align: center; margin-top: 6px; }

/* ── Change list ── */
.change-item { display: flex; align-items: center; gap: 8px; padding: 6px 0; font-size: 14px; }
.change-item .dot { color: #2D6A4F; font-size: 16px; }

/* Tabs */
.stTabs [data-baseweb="tab-list"] { gap: 4px; }
.stTabs [data-baseweb="tab"] { border-radius: 8px 8px 0 0 !important; font-weight: 500; }
</style>
""", unsafe_allow_html=True)

# ─── Session State ─────────────────────────────────────────────────────────────
for k, v in {
    "token": None, "user_email": None, "page": "dashboard",
    "selected_plant": None, "pending_diagnosis": None, "chat_messages": []
}.items():
    if k not in st.session_state:
        st.session_state[k] = v


def nav(page):
    st.session_state.page = page
    st.session_state.pending_diagnosis = None
    st.rerun()


def back_button():
    """← Dashboard button at top of every non-dashboard page."""
    col, _ = st.columns([1, 7])
    with col:
        if st.button("← Dashboard", key="back_to_dash", type="secondary"):
            nav("dashboard")
    st.markdown('<div style="height:4px"></div>', unsafe_allow_html=True)


def badge(status):
    cls = {"healthy": "badge-healthy", "recovering": "badge-recovering",
           "critical": "badge-critical"}.get(status, "badge-unknown")
    label = {"healthy": "✓ Healthy", "recovering": "● Recovering",
              "critical": "! Critical"}.get(status, "● Unknown")
    return f'<span class="badge {cls}">{label}</span>'


def category_icon(cat):
    return {"water": "💧", "light": "☀️", "pest": "🐛",
            "nutrient": "🌱", "disease": "🦠", "healthy": "✅"}.get(cat, "🔍")


# ══════════════════════════════════════════════════════════════════════════════
# AUTH SCREEN
# ══════════════════════════════════════════════════════════════════════════════
def auth_screen():
    _, col, _ = st.columns([1, 1.2, 1])
    with col:
        st.markdown("""
        <div class="auth-logo">
            <div style="font-size:48px">🌿</div>
            <div class="auth-title">Plant Doctor</div>
            <div class="auth-sub">AI-powered plant diagnosis and care guidance</div>
        </div>
        """, unsafe_allow_html=True)

        tab_login, tab_signup = st.tabs(["  Login  ", "  Sign Up  "])

        with tab_login:
            # ── Google OAuth ──
            st.markdown('<div style="height:12px"></div>', unsafe_allow_html=True)
    
            # Get Google OAuth URL from backend
            if st.button("🔵  Continue with Google", use_container_width=True):
                import requests
                r = requests.get(f"{API_BASE}/auth/google/url")
                if r.status_code == 200:
                    google_url = r.json()["url"]
                    st.markdown(f'<meta http-equiv="refresh" content="0;url={google_url}">',
                        unsafe_allow_html=True)
                    st.info("Redirecting to Google...")

            st.markdown("---")
            st.caption("or login with email")

            # Keep existing email/password login below...
            email = st.text_input("Email", ...)
            # rest stays the same
        with tab_signup:
            st.markdown('<div style="height:12px"></div>', unsafe_allow_html=True)
            email2 = st.text_input("Email", placeholder="you@example.com", key="su_email")
            password2 = st.text_input("Password", type="password", placeholder="Create a password", key="su_pass")
            st.markdown('<div style="height:4px"></div>', unsafe_allow_html=True)
            if st.button("Create Account", key="btn_signup"):
                r = api.signup(email2, password2)
                if r.status_code == 201:
                    st.success("Account created! Please log in.")
                else:
                    st.error(r.json().get("detail", "Signup failed"))


# ══════════════════════════════════════════════════════════════════════════════
# SIDEBAR
# ══════════════════════════════════════════════════════════════════════════════
def sidebar(plants):
    with st.sidebar:
        st.markdown("""
        <div class="sidebar-logo">
            <div class="sidebar-logo-icon">🌿</div>
            <div>
                <div class="sidebar-logo-text">Plant Doctor</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        email = st.session_state.user_email or ""
        name = email.split("@")[0].capitalize()
        st.markdown(f"""
        <div style="background:#f0f7f0;border-radius:10px;padding:10px 12px;margin-bottom:20px;">
            <div style="font-weight:600;font-size:13px;color:#1a1a1a">👤 {name}</div>
            <div style="font-size:11px;color:#6b7280">{email}</div>
        </div>
        """, unsafe_allow_html=True)

        page = st.session_state.page
        nav_items = [
            ("dashboard", "🏠", "Dashboard"),
            ("my_plants", "🌿", "My Plants"),
            ("diagnose", "🔬", "Diagnose"),
            ("care_plans", "📋", "Care Plans"),
            ("checkin", "📅", "Check-in"),
            ("gallery", "🖼️", "Gallery"),
        ]
        for key, icon, label in nav_items:
            active = "active" if page == key else ""
            if st.button(f"{icon}  {label}", key=f"nav_{key}",
                         help=label, use_container_width=True):
                nav(key)

        st.markdown('<div style="margin-top:auto;padding-top:32px"></div>', unsafe_allow_html=True)
        st.divider()

        # Plant selector
        if plants:
            plant_names = {p["id"]: p["name"] for p in plants}
            if st.session_state.selected_plant not in plant_names:
                st.session_state.selected_plant = plants[0]["id"]
            selected = st.selectbox(
                "Active Plant",
                options=list(plant_names.keys()),
                format_func=lambda i: f"🌱 {plant_names[i]}",
                index=list(plant_names.keys()).index(st.session_state.selected_plant),
                key="plant_selector"
            )
            st.session_state.selected_plant = selected

        st.markdown('<div style="height:16px"></div>', unsafe_allow_html=True)
        if st.button("🚪  Logout", use_container_width=True, key="nav_logout"):
            for k in ["token", "user_email", "page", "selected_plant", "pending_diagnosis"]:
                st.session_state[k] = None if k != "page" else "dashboard"
            st.rerun()


# ══════════════════════════════════════════════════════════════════════════════
# DASHBOARD
# ══════════════════════════════════════════════════════════════════════════════
def page_dashboard(plants):
    email = st.session_state.user_email or ""
    name = email.split("@")[0].capitalize()

    st.markdown(f"""
    <div class="page-header">
        <div>
            <h1>Welcome back, {name}! 🌿</h1>
            <p>Here's how your plants are doing today.</p>
        </div>
    </div>
    """, unsafe_allow_html=True)

    main_col, side_col = st.columns([2.5, 1])

    with main_col:
        # Stats row
        healthy = sum(1 for p in plants if p["status"] == "healthy")
        recovering = sum(1 for p in plants if p["status"] == "recovering")
        critical = sum(1 for p in plants if p["status"] == "critical")

        c1, c2, c3, c4 = st.columns(4)
        for col, label, val, color in [
            (c1, "Total Plants", len(plants), "#2D6A4F"),
            (c2, "Healthy", healthy, "#059669"),
            (c3, "Recovering", recovering, "#d97706"),
            (c4, "Critical", critical, "#dc2626"),
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
                        <div class="plant-card-img">🌿</div>
                        <div class="plant-card-body">
                            <div class="plant-card-name">{plant['name']}</div>
                            <div class="plant-card-species">{plant.get('species') or 'Unknown species'}</div>
                            {badge(plant['status'])}
                            <div class="plant-card-meta" style="margin-top:8px">📍 {plant.get('location') or '—'}</div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                    if st.button("View", key=f"dash_view_{plant['id']}", use_container_width=True):
                        st.session_state.selected_plant = plant["id"]
                        nav("diagnose")

            if len(plants) < 6:
                with cols[len(plants) % 3]:
                    st.markdown("""
                    <div class="plant-card" style="border:2px dashed #d1d5db;background:#fafafa;
                         text-align:center;padding:40px 0;display:flex;flex-direction:column;align-items:center">
                        <div style="font-size:32px;color:#9ca3af">＋</div>
                        <div style="font-size:13px;color:#9ca3af;margin-top:4px">Add New Plant</div>
                    </div>""", unsafe_allow_html=True)
                    if st.button("Add Plant", key="dash_add", use_container_width=True):
                        nav("my_plants")

    with side_col:
        st.markdown("### Quick Actions")
        if st.button("🔬  Diagnose a Plant", use_container_width=True, key="qa_diag"):
            nav("diagnose")
        st.markdown('<div style="height:8px"></div>', unsafe_allow_html=True)
        if st.button("📅  Weekly Check-in", use_container_width=True, key="qa_checkin"):
            nav("checkin")
        st.markdown('<div style="height:8px"></div>', unsafe_allow_html=True)
        if st.button("➕  Add New Plant", use_container_width=True, key="qa_add"):
            nav("my_plants")

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
        <div><h1>🌿 My Plants</h1><p>Manage your plant collection</p></div>
    </div>""", unsafe_allow_html=True)

    left, right = st.columns([1, 1.8])

    with left:
        st.markdown("""
        <div class="pd-card">
            <div style="font-weight:700;font-size:16px;margin-bottom:16px">➕ Add New Plant</div>
        </div>""", unsafe_allow_html=True)
        with st.form("add_plant_form", clear_on_submit=True):
            name = st.text_input("Plant Name *", placeholder="e.g. Money Plant")
            species = st.text_input("Species (optional)", placeholder="e.g. Pothos")
            location = st.text_input("Location (optional)", placeholder="e.g. Living Room, Near Window")
            st.markdown("**Upload Plant Photo** *(optional)*")
            photo = st.file_uploader("", type=["jpg", "jpeg", "png"], key="add_photo", label_visibility="collapsed")
            if photo:
                st.image(photo, use_column_width=True)
            submitted = st.form_submit_button("Save Plant", use_container_width=True)
            if submitted:
                if name:
                    api.create_plant(name, species, location)
                    st.success(f"✅ {name} added!")
                    st.rerun()
                else:
                    st.error("Plant name is required")

    with right:
        if not plants:
            st.markdown("""
            <div class="pd-card" style="text-align:center;padding:60px">
                <div style="font-size:56px">🌱</div>
                <div style="font-weight:600;margin:12px 0 6px;font-size:18px">No plants yet</div>
                <div style="color:#6b7280">Add your first plant using the form</div>
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
        <div><h1>🔬 Diagnose Plant</h1>
        <p>Upload a clear photo of <strong>{plant['name']}</strong> and describe the issue</p></div>
    </div>""", unsafe_allow_html=True)

    pending = st.session_state.pending_diagnosis

    # ── Step: clarifying questions (chat UI) ──
    if pending and pending.get("plant_id") == plant["id"]:
        left, right = st.columns([1.2, 1])

        with left:
            st.markdown('<div class="pd-card">', unsafe_allow_html=True)
            st.markdown("#### 🤖 Plant Doctor Assistant")
            st.caption("Answer a few questions to get the best care plan")

            diag = pending["diagnosis"]
            cat = diag.get("symptom_category", "unknown")

            # Show diagnosis summary
            st.markdown(f"""
            <div style="background:#f0f7f0;border-radius:10px;padding:12px 16px;margin:8px 0 16px">
                <div style="font-size:12px;color:#6b7280;margin-bottom:4px">Issue Detected</div>
                <div style="font-size:18px;font-weight:700;color:#dc2626">
                    {category_icon(cat)} {cat.title()}
                </div>
                <div style="font-size:13px;color:#374151;margin-top:6px">{diag.get('diagnosis_text','')}</div>
            </div>""", unsafe_allow_html=True)

            # Chat messages
            msgs = st.session_state.chat_messages
            if not msgs:
                for q in pending["questions"]:
                    st.session_state.chat_messages.append({"role": "bot", "text": q})
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

            # Answer input
            answered = [m for m in msgs if m["role"] == "user"]
            questions = pending["questions"]

            if len(answered) < len(questions):
                next_q_idx = len(answered)
                answer = st.text_input(
                    f"Your answer ({next_q_idx + 1}/{len(questions)})",
                    placeholder="Type your answer...",
                    key=f"chat_ans_{next_q_idx}"
                )
                if st.button("Send ➤", key=f"send_{next_q_idx}"):
                    if answer.strip():
                        st.session_state.chat_messages.append({"role": "user", "text": answer})
                        if len(st.session_state.chat_messages) // 2 >= len(questions):
                            pass
                        st.rerun()
            else:
                # All questions answered
                all_answers = [m["text"] for m in msgs if m["role"] == "user"]
                st.markdown('<div style="height:8px"></div>', unsafe_allow_html=True)
                if st.button("✅ Get My Care Plan", use_container_width=True):
                    with st.spinner("Generating your personalised care plan..."):
                        result = api.answer_clarifying(plant["id"], all_answers)
                    st.session_state.pending_diagnosis = None
                    st.session_state.chat_messages = []
                    st.success("Care plan ready!")
                    nav("care_plans")

            st.markdown('</div>', unsafe_allow_html=True)

        with right:
            # Show species & confidence
            diag = pending["diagnosis"]
            st.markdown(f"""
            <div class="pd-card">
                <div class="issue-label">Identified Species</div>
                <div style="font-size:16px;font-weight:700;color:#1a1a1a;margin-bottom:12px">
                    🌿 {diag.get('species_guess') or 'Unknown'}
                </div>
                <div class="issue-label">Issue Category</div>
                <div class="issue-value">{category_icon(diag.get('symptom_category',''))} {(diag.get('symptom_category') or 'Unknown').title()}</div>
                <div style="margin-top:16px">
                    <div class="issue-label">Possible Causes</div>
                    <div class="cause-item">✅ Check watering schedule</div>
                    <div class="cause-item">✅ Review light conditions</div>
                    <div class="cause-item">✅ Inspect soil drainage</div>
                </div>
                <div style="margin-top:16px">
                    <button onclick="" style="background:none;border:1px solid #e5e7eb;border-radius:8px;
                    padding:8px 16px;font-size:13px;color:#6b7280;cursor:pointer;width:100%">
                    🔄 Not correct? Try again</button>
                </div>
            </div>""", unsafe_allow_html=True)
        return

    # ── Step: Upload photo ──
    left, right = st.columns([1.2, 1])

    with left:
        st.markdown('<div class="pd-card">', unsafe_allow_html=True)
        st.markdown("#### Upload Plant Photo")
        uploaded = st.file_uploader(
            "Upload a clear photo of your plant",
            type=["jpg", "jpeg", "png"],
            key=f"diag_upload_{plant['id']}",
            label_visibility="collapsed"
        )

        if uploaded:
            st.image(uploaded, use_column_width=True, caption="")
            if st.button("🔄 Change Photo", key="change_photo"):
                st.rerun()
        else:
            st.markdown("""
            <div style="border:2px dashed #d1d5db;border-radius:12px;padding:48px;text-align:center;
                        background:#fafafa;margin:8px 0">
                <div style="font-size:36px;color:#9ca3af">📷</div>
                <div style="font-size:14px;color:#9ca3af;margin-top:8px">
                    Drag & drop an image here<br>or click to browse
                </div>
                <div style="font-size:11px;color:#d1d5db;margin-top:6px">JPG, PNG up to 10MB</div>
            </div>""", unsafe_allow_html=True)

        st.markdown("#### Describe the Issue *(optional)*")
        note = st.text_area(
            "",
            placeholder="Leaves are turning yellow and some are brown. Not sure what's wrong.",
            height=100,
            key=f"diag_note_{plant['id']}",
            label_visibility="collapsed"
        )
        char_count = len(note)
        st.caption(f"{char_count}/300")

        disabled = uploaded is None
        if st.button("🔬 Analyze Plant", disabled=disabled, use_container_width=True, key="analyze_btn"):
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
                <div>
                    <div style="font-size:11px;color:#9ca3af;font-weight:600;text-transform:uppercase;letter-spacing:.5px">Species</div>
                    <div style="font-size:14px;color:#1a1a1a;margin-top:2px">{plant.get('species') or 'Will be detected automatically'}</div>
                </div>
                <div>
                    <div style="font-size:11px;color:#9ca3af;font-weight:600;text-transform:uppercase;letter-spacing:.5px">Location</div>
                    <div style="font-size:14px;color:#1a1a1a;margin-top:2px">{plant.get('location') or '—'}</div>
                </div>
                <div>
                    <div style="font-size:11px;color:#9ca3af;font-weight:600;text-transform:uppercase;letter-spacing:.5px">Current Status</div>
                    <div style="margin-top:4px">{badge(plant['status'])}</div>
                </div>
            </div>
        </div>
        <div class="pd-card" style="margin-top:0">
            <div style="font-weight:600;margin-bottom:10px">💡 Tips for a great photo</div>
            <div style="font-size:13px;color:#374151;line-height:1.8">
                ✓ Use natural daylight<br>
                ✓ Show affected leaves clearly<br>
                ✓ Include whole plant if possible<br>
                ✓ Avoid blurry or dark images
            </div>
        </div>""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# CARE PLANS
# ══════════════════════════════════════════════════════════════════════════════
def page_care_plans(plant):
    back_button()
    st.markdown(f"""
    <div class="page-header">
        <div><h1>📋 Recovery Care Plan</h1>
        <p>Follow these steps to help <strong>{plant['name']}</strong> recover</p></div>
    </div>""", unsafe_allow_html=True)

    plans = api.list_care_plans(plant["id"])
    if not plans:
        st.markdown("""
        <div class="pd-card" style="text-align:center;padding:60px">
            <div style="font-size:56px">📋</div>
            <div style="font-weight:600;margin:12px 0 6px;font-size:18px">No care plans yet</div>
            <div style="color:#6b7280;margin-bottom:24px">Run a diagnosis first to get a personalised care plan</div>
        </div>""", unsafe_allow_html=True)
        if st.button("🔬 Go to Diagnose", use_container_width=False):
            nav("diagnose")
        return

    plan = plans[0]
    checklist = plan.get("checklist", [])
    done_count = sum(1 for c in checklist if c.get("done"))
    total = len(checklist)
    pct = int(done_count / total * 100) if total else 0

    left, right = st.columns([1.5, 1])

    with left:
        # Recovery time banner
        st.markdown(f"""
        <div class="recovery-banner">
            <div style="font-size:28px">📅</div>
            <div>
                <div style="font-size:11px;color:#2D6A4F;font-weight:600;text-transform:uppercase;letter-spacing:.5px">Expected Recovery Time</div>
                <div class="recovery-days">{plan.get('expected_recovery', '1–2 weeks')}</div>
            </div>
        </div>""", unsafe_allow_html=True)

        # Plan summary
        st.markdown(f"""
        <div class="pd-card">
            <div style="font-size:15px;color:#374151;line-height:1.6">{plan['plan_text']}</div>
        </div>""", unsafe_allow_html=True)

        # Checklist
        st.markdown(f"""
        <div class="pd-card">
            <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:8px">
                <div style="font-weight:700">Care Checklist</div>
                <div style="font-size:13px;color:#6b7280">{done_count}/{total} completed &nbsp; <strong style="color:#2D6A4F">{pct}%</strong></div>
            </div>
            <div class="checklist-progress">
                <div class="checklist-progress-bar" style="width:{pct}%"></div>
            </div>
        </div>""", unsafe_allow_html=True)

        updated = list(checklist)
        changed = False
        for j, item in enumerate(checklist):
            checked = st.checkbox(
                item["item"], value=item["done"],
                key=f"chk_{plan['id']}_{j}"
            )
            if checked != item["done"]:
                updated[j] = {**item, "done": checked}
                changed = True

        if changed:
            api.update_checklist(plant["id"], plan["id"], updated)
            st.rerun()

        st.markdown("""
        <div style="background:#f0f7f0;border-radius:10px;padding:12px 16px;margin-top:8px;
                     font-size:13px;color:#2D6A4F">
            💡 <strong>Tip:</strong> Check back in a week to update your progress!
        </div>""", unsafe_allow_html=True)

    with right:
        # History
        st.markdown("#### Plan History")
        for i, p in enumerate(plans):
            active = i == 0
            st.markdown(f"""
            <div class="pd-card" style="border-left:3px solid {'#2D6A4F' if active else '#e5e7eb'};
                 padding:12px 14px;margin-bottom:8px">
                <div style="font-weight:600;font-size:13px">{'📌 Current Plan' if active else f'Plan {i+1}'}</div>
                <div style="font-size:11px;color:#9ca3af">{p['created_at'][:10]}</div>
                <div style="font-size:12px;color:#6b7280;margin-top:4px">
                    Recovery: {p.get('expected_recovery','—')}
                </div>
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
        <div><h1>📅 Weekly Check-in</h1>
        <p>Track <strong>{plant['name']}</strong>'s progress over time</p></div>
    </div>""", unsafe_allow_html=True)

    diagnoses = api.list_diagnoses(plant["id"])
    photos = api.list_photos(plant["id"])

    if not diagnoses:
        st.info("Run a diagnosis first before doing a weekly check-in.")
        if st.button("🔬 Go to Diagnose"):
            nav("diagnose")
        return

    left, right = st.columns([1.2, 1])

    with left:
        st.markdown('<div class="pd-card">', unsafe_allow_html=True)
        st.markdown("#### Upload Today's Photo")

        uploaded = st.file_uploader("New photo", type=["jpg", "jpeg", "png"],
                                     key=f"ci_{plant['id']}", label_visibility="collapsed")

        if uploaded:
            st.image(uploaded, use_column_width=True)

        note = st.text_area("Any changes you've noticed?",
                             placeholder="e.g. New leaves are growing, yellowing has reduced...",
                             height=80, key=f"ci_note_{plant['id']}")

        if st.button("📸 Submit Check-in", disabled=uploaded is None,
                     use_container_width=True, key="ci_submit"):
            with st.spinner("Comparing with last photo and updating care plan..."):
                plan = api.weekly_checkin(plant["id"], uploaded.getvalue(), uploaded.name, note)
            st.success("✅ Check-in complete! Care plan updated.")
            nav("care_plans")

        st.markdown('</div>', unsafe_allow_html=True)

    with right:
        if len(photos) >= 2:
            prior = photos[-2]
            current = photos[-1]
            st.markdown("#### Photo Comparison")
            st.markdown("""
            <div class="pd-card">
                <div class="compare-grid">
                    <div>
                        <div style="font-size:11px;color:#9ca3af;text-align:center;margin-bottom:6px">
                            Previous (7 days ago)</div>
            """, unsafe_allow_html=True)
            col1, arrow_col, col2 = st.columns([5, 1, 5])
            with col1:
                try:
                    st.image(api.photo_url(prior["filepath"]), use_column_width=True)
                    st.caption(prior["taken_at"][:10])
                except Exception:
                    st.caption("📷 Previous photo")
            with arrow_col:
                st.markdown("<div style='text-align:center;font-size:24px;margin-top:40px'>→</div>",
                            unsafe_allow_html=True)
            with col2:
                try:
                    st.image(api.photo_url(current["filepath"]), use_column_width=True)
                    st.caption(current["taken_at"][:10])
                except Exception:
                    st.caption("📷 Latest photo")
            st.markdown('</div>', unsafe_allow_html=True)

        # Health score
        plans = api.list_care_plans(plant["id"])
        if plans:
            plan = plans[0]
            checklist = plan.get("checklist", [])
            done = sum(1 for c in checklist if c.get("done"))
            total = len(checklist)
            score = int(done / total * 100) if total else 0
            prev_score = max(0, score - 17)

            st.markdown(f"""
            <div class="pd-card">
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
        <div><h1>🖼️ Photo Gallery</h1>
        <p>Visual recovery timeline for <strong>{plant['name']}</strong></p></div>
    </div>""", unsafe_allow_html=True)

    photos = api.list_photos(plant["id"])

    if not photos:
        st.markdown("""
        <div class="pd-card" style="text-align:center;padding:60px">
            <div style="font-size:56px">📷</div>
            <div style="font-weight:600;margin:12px 0 6px;font-size:18px">No photos yet</div>
            <div style="color:#6b7280">Photos will appear here after you run a diagnosis</div>
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
                     align-items:center;justify-content:center;font-size:32px">📷</div>
                """, unsafe_allow_html=True)
            st.caption(f"📅 {photo['taken_at'][:10]}")
            if photo.get("note"):
                st.caption(f"💬 {photo['note'][:40]}...")


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

    # Get selected plant object
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
        if plant:
            page_diagnose(plant)
        else:
            st.info("Add a plant first to run a diagnosis.")
            if st.button("➕ Add Plant"):
                nav("my_plants")
    elif page == "care_plans":
        if plant:
            page_care_plans(plant)
        else:
            st.info("Add a plant first.")
    elif page == "checkin":
        if plant:
            page_checkin(plant)
        else:
            st.info("Add a plant first.")
    elif page == "gallery":
        if plant:
            page_gallery(plant)
        else:
            st.info("Add a plant first.")
