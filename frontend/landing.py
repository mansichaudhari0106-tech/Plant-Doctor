import streamlit as st

def show_landing():
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
    html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
    .stApp { background: #ffffff; }
    #MainMenu, footer, header { visibility: hidden; }
    .block-container { padding: 0 !important; max-width: 100% !important; }

    .hero { background: linear-gradient(135deg, #1B4332 0%, #2D6A4F 50%, #40916C 100%);
            padding: 80px 40px; text-align: center; }
    .hero-badge { display:inline-block; background:rgba(255,255,255,0.15);
                  color:white; padding:6px 16px; border-radius:20px;
                  font-size:13px; font-weight:600; margin-bottom:24px; }
    .hero-title { font-size:56px; font-weight:800; color:white;
                  line-height:1.1; margin:0 0 20px; }
    .hero-title span { color:#95d5b2; }
    .hero-sub { font-size:20px; color:rgba(255,255,255,0.85);
                max-width:600px; margin:0 auto 40px; line-height:1.6; }
    .hero-btns { display:flex; gap:16px; justify-content:center; flex-wrap:wrap; }
    .btn-primary { background:white; color:#1B4332; padding:14px 32px;
                   border-radius:12px; font-weight:700; font-size:16px;
                   text-decoration:none; cursor:pointer; border:none;
                   transition:transform 0.2s; }
    .btn-primary:hover { transform:translateY(-2px); }
    .btn-secondary { background:transparent; color:white; padding:14px 32px;
                     border-radius:12px; font-weight:600; font-size:16px;
                     border:2px solid rgba(255,255,255,0.5); cursor:pointer; }

    .section { padding:80px 40px; text-align:center; }
    .section-dark { background:#f4f7f4; }
    .section-title { font-size:36px; font-weight:800; color:#1a1a1a; margin-bottom:12px; }
    .section-sub { font-size:18px; color:#6b7280; max-width:600px;
                   margin:0 auto 48px; line-height:1.6; }

    .features-grid { display:grid; grid-template-columns:repeat(auto-fit,minmax(260px,1fr));
                     gap:24px; max-width:1100px; margin:0 auto; }
    .feature-card { background:white; border-radius:20px; padding:32px 24px;
                    box-shadow:0 2px 12px rgba(0,0,0,0.06);
                    transition:transform 0.2s, box-shadow 0.2s; text-align:left; }
    .feature-card:hover { transform:translateY(-4px); box-shadow:0 8px 24px rgba(0,0,0,0.1); }
    .feature-icon { font-size:40px; margin-bottom:16px; }
    .feature-title { font-size:18px; font-weight:700; color:#1a1a1a; margin-bottom:8px; }
    .feature-desc { font-size:14px; color:#6b7280; line-height:1.7; }

    .steps-grid { display:grid; grid-template-columns:repeat(auto-fit,minmax(220px,1fr));
                  gap:32px; max-width:900px; margin:0 auto; }
    .step { text-align:center; }
    .step-num { width:48px; height:48px; background:#2D6A4F; color:white;
                border-radius:50%; display:flex; align-items:center; justify-content:center;
                font-size:20px; font-weight:800; margin:0 auto 16px; }
    .step-title { font-size:16px; font-weight:700; color:#1a1a1a; margin-bottom:8px; }
    .step-desc { font-size:14px; color:#6b7280; line-height:1.6; }
    .step-arrow { font-size:24px; color:#d1d5db; margin-top:20px; }

    .testimonials { display:grid; grid-template-columns:repeat(auto-fit,minmax(280px,1fr));
                    gap:24px; max-width:900px; margin:0 auto; }
    .testimonial { background:white; border-radius:16px; padding:24px;
                   box-shadow:0 2px 12px rgba(0,0,0,0.06); text-align:left; }
    .testimonial-text { font-size:15px; color:#374151; line-height:1.7;
                        font-style:italic; margin-bottom:16px; }
    .testimonial-author { display:flex; align-items:center; gap:12px; }
    .testimonial-avatar { width:40px; height:40px; border-radius:50%;
                          background:#d1fae5; display:flex; align-items:center;
                          justify-content:center; font-size:18px; }
    .testimonial-name { font-weight:600; font-size:14px; color:#1a1a1a; }
    .testimonial-role { font-size:12px; color:#9ca3af; }

    .stats { display:grid; grid-template-columns:repeat(auto-fit,minmax(180px,1fr));
             gap:24px; max-width:800px; margin:0 auto 48px; }
    .stat { text-align:center; }
    .stat-num { font-size:48px; font-weight:800; color:#2D6A4F; }
    .stat-label { font-size:14px; color:#6b7280; margin-top:4px; }

    .cta { background:linear-gradient(135deg,#1B4332,#2D6A4F);
           padding:80px 40px; text-align:center; }
    .cta-title { font-size:40px; font-weight:800; color:white; margin-bottom:16px; }
    .cta-sub { font-size:18px; color:rgba(255,255,255,0.8); margin-bottom:40px; }

    .footer { background:#1a1a1a; padding:40px; text-align:center; }
    .footer-logo { font-size:24px; font-weight:800; color:white; margin-bottom:8px; }
    .footer-sub { font-size:14px; color:#6b7280; }
    </style>

    <!-- HERO -->
    <div class="hero">
        <div class="hero-badge">🌿 AI-Powered Plant Care</div>
        <div class="hero-title">Your Plants Deserve<br><span>Expert Care</span></div>
        <div class="hero-sub">
            Upload a photo of your sick plant and get an instant AI diagnosis,
            personalised recovery plan, and week-by-week progress tracking.
        </div>
    </div>
    """, unsafe_allow_html=True)

    # CTA buttons using Streamlit
    _, c1, c2, _ = st.columns([1, 1, 1, 1])
    with c1:
        if st.button("🌿  Get Started Free", use_container_width=True, key="hero_signup"):
            st.session_state.auth_tab = "signup"
            st.session_state.show_landing = False
            st.rerun()
    with c2:
        if st.button("🔑  Login", use_container_width=True, key="hero_login"):
            st.session_state.auth_tab = "login"
            st.session_state.show_landing = False
            st.rerun()

    st.markdown("""
    <!-- HOW IT WORKS -->
    <div class="section">
        <div class="section-title">How It Works</div>
        <div class="section-sub">Get your plant diagnosed in under 2 minutes</div>
        <div class="steps-grid">
            <div class="step">
                <div class="step-num">1</div>
                <div class="step-title">Upload a Photo</div>
                <div class="step-desc">Take a clear photo of your plant showing the affected areas</div>
            </div>
            <div class="step">
                <div class="step-num">2</div>
                <div class="step-title">AI Diagnoses</div>
                <div class="step-desc">Our vision AI identifies the species and detects the issue instantly</div>
            </div>
            <div class="step">
                <div class="step-num">3</div>
                <div class="step-title">Answer Questions</div>
                <div class="step-desc">AI asks targeted follow-up questions to refine the diagnosis</div>
            </div>
            <div class="step">
                <div class="step-num">4</div>
                <div class="step-title">Get Your Plan</div>
                <div class="step-desc">Receive a step-by-step recovery plan with weekly check-ins</div>
            </div>
        </div>
    </div>

    <!-- FEATURES -->
    <div class="section section-dark">
        <div class="section-title">Everything Your Plant Needs</div>
        <div class="section-sub">Comprehensive AI-powered plant care in one place</div>
        <div class="features-grid">
            <div class="feature-card">
                <div class="feature-icon">🔬</div>
                <div class="feature-title">AI Vision Diagnosis</div>
                <div class="feature-desc">Powered by Groq's llama-4-scout vision model. Identifies 500+ plant species and detects issues like overwatering, pests, nutrient deficiency, and disease.</div>
            </div>
            <div class="feature-card">
                <div class="feature-icon">💬</div>
                <div class="feature-title">Smart Clarifying Questions</div>
                <div class="feature-desc">AI generates targeted follow-up questions specific to your plant's symptoms — not generic questions, but ones that actually matter for your diagnosis.</div>
            </div>
            <div class="feature-card">
                <div class="feature-icon">📋</div>
                <div class="feature-title">Personalised Care Plans</div>
                <div class="feature-desc">Get a step-by-step recovery checklist with expected recovery time, specific actions, and what to watch for.</div>
            </div>
            <div class="feature-card">
                <div class="feature-icon">📅</div>
                <div class="feature-title">Weekly Progress Tracking</div>
                <div class="feature-desc">Upload weekly photos and AI compares them side-by-side, tracking your plant's recovery and updating the care plan accordingly.</div>
            </div>
            <div class="feature-card">
                <div class="feature-icon">🖼️</div>
                <div class="feature-title">Private Photo Gallery</div>
                <div class="feature-desc">Your photos are completely private and secure — only you can see your plant's recovery timeline. No sharing, no public access.</div>
            </div>
            <div class="feature-card">
                <div class="feature-icon">🔒</div>
                <div class="feature-title">Secure Authentication</div>
                <div class="feature-desc">Login with Google or email. Your account, data, and plant history are fully protected and private to you.</div>
            </div>
        </div>
    </div>

    <!-- STATS -->
    <div class="section">
        <div class="section-title">Trusted by Plant Lovers</div>
        <div class="section-sub">Join thousands of people saving their plants</div>
        <div class="stats">
            <div class="stat"><div class="stat-num">500+</div><div class="stat-label">Plant Species Identified</div></div>
            <div class="stat"><div class="stat-num">6</div><div class="stat-label">Issue Categories Detected</div></div>
            <div class="stat"><div class="stat-num">2 min</div><div class="stat-label">Average Diagnosis Time</div></div>
            <div class="stat"><div class="stat-num">100%</div><div class="stat-label">Private & Secure</div></div>
        </div>
    </div>

    <!-- TESTIMONIALS -->
    <div class="section section-dark">
        <div class="section-title">What Plant Parents Say</div>
        <div class="section-sub">Real stories from real plant lovers</div>
        <div class="testimonials">
            <div class="testimonial">
                <div class="testimonial-text">"My pothos was dying and I had no idea why. Plant Doctor diagnosed overwatering in seconds and gave me a recovery plan. It's thriving now!"</div>
                <div class="testimonial-author">
                    <div class="testimonial-avatar">🌸</div>
                    <div><div class="testimonial-name">Priya S.</div><div class="testimonial-role">Plant parent of 12</div></div>
                </div>
            </div>
            <div class="testimonial">
                <div class="testimonial-text">"The weekly check-in feature is brilliant. Watching my monstera's health score go from 40% to 90% over a month was so satisfying."</div>
                <div class="testimonial-author">
                    <div class="testimonial-avatar">🌵</div>
                    <div><div class="testimonial-name">Rahul M.</div><div class="testimonial-role">Succulent collector</div></div>
                </div>
            </div>
            <div class="testimonial">
                <div class="testimonial-text">"Finally an app that asks the RIGHT questions. It asked about drainage holes and watering frequency — exactly what I needed to fix my fiddle leaf fig."</div>
                <div class="testimonial-author">
                    <div class="testimonial-avatar">🌿</div>
                    <div><div class="testimonial-name">Ananya K.</div><div class="testimonial-role">Indoor garden enthusiast</div></div>
                </div>
            </div>
        </div>
    </div>

    <!-- CTA -->
    <div class="cta">
        <div class="cta-title">Save Your Plants Today</div>
        <div class="cta-sub">Free to use. No credit card required. Just upload a photo.</div>
    </div>

    <!-- FOOTER -->
    <div class="footer">
        <div class="footer-logo">🌿 Plant Doctor</div>
        <div class="footer-sub">AI-powered plant diagnosis and care · Built with Groq Vision AI</div>
    </div>
    """, unsafe_allow_html=True)

    _, c3, _ = st.columns([1, 2, 1])
    with c3:
        if st.button("🌿  Start Diagnosing Your Plants — It's Free", use_container_width=True, key="cta_btn"):
            st.session_state.auth_tab = "signup"
            st.session_state.show_landing = False
            st.rerun()
