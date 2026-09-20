import base64
from datetime import datetime
from pathlib import Path

import joblib
import pandas as pd
import streamlit as st

# ==========================================
# 1. Page Configuration
# ==========================================
st.set_page_config(
    page_title='Startup Failure Predictor', page_icon='🚀', layout='wide'
)

# Optional: drop a photo named hero.jpg / hero.png next to this file
# and it will replace the default hero image automatically.
HERO_URL = (
    'https://images.unsplash.com/photo-1451187580459-43490279c0fa'
    '?auto=format&fit=crop&w=1800&q=60'
)


@st.cache_data
def hero_image_src():
    here = Path(__file__).parent
    for name, mime in (
        ('hero.jpg', 'image/jpeg'),
        ('hero.jpeg', 'image/jpeg'),
        ('hero.png', 'image/png'),
        ('hero.webp', 'image/webp'),
    ):
        p = here / name
        if p.exists():
            return f'data:{mime};base64,' + base64.b64encode(p.read_bytes()).decode()
    return HERO_URL


_VER = tuple(int(x) for x in st.__version__.split('.')[:2])
# Streamlit 1.50+ prefers width='stretch'; older versions use use_container_width.
STRETCH = {'width': 'stretch'} if _VER >= (1, 50) else {'use_container_width': True}


def H(markup: str):
    """Render HTML. Lines are joined so Markdown never treats indents as code."""
    st.markdown(
        ' '.join(line.strip() for line in markup.strip().splitlines()),
        unsafe_allow_html=True,
    )


# ==========================================
# 2. Styling
# ==========================================
H(
    """
<style>
@import url('https://fonts.googleapis.com/css2?family=Bricolage+Grotesque:opsz,wght@12..96,500;12..96,700;12..96,800&family=Figtree:wght@400;500;600;700&display=swap');

:root{
  --space:#1a2255; --panel:#232d6a; --panel-2:#2d3982; --line:rgba(190,200,255,.30);
  --text:#f6f8ff; --muted:#c8d0f7;
  --teal:#3ee6cb; --violet:#a99cff; --ignite:#ff8f5e;
  --low:#3ee6cb; --mid:#ffd166; --high:#ff6b81;
}
@property --deg{syntax:'<angle>';inherits:false;initial-value:0deg}
@keyframes sweep{from{--deg:0deg}}

html, body, [class*="css"], .stApp{font-family:'Figtree',sans-serif;}
.stApp{
  color:var(--text);
  background:
    radial-gradient(1100px 520px at 78% -8%, rgba(150,130,255,.34), transparent 62%),
    radial-gradient(900px 500px at 5% 35%, rgba(62,230,203,.10), transparent 60%),
    var(--space);
}
.block-container{padding-top:1.4rem;padding-bottom:4rem;max-width:1320px;}
header[data-testid="stHeader"]{background:transparent;}
footer, #MainMenu, .stAppDeployButton{visibility:hidden;}
h1,h2,h3,h4,h5,h6{color:var(--text)!important;}
hr{border-color:var(--line)!important;}

/* ---------- Hero ---------- */
.hero{
  position:relative;border-radius:22px;overflow:hidden;margin-bottom:28px;min-height:300px;
  border:1px solid var(--line);background:linear-gradient(135deg,#243083,#5a3db8);
}
.hero-bg{position:absolute;inset:0;background-size:cover;background-position:center;
  filter:brightness(1.7) contrast(1.08) saturate(1.3);}
.hero-glow{position:absolute;inset:0;mix-blend-mode:screen;
  background:
    radial-gradient(60% 120% at 88% 118%,rgba(96,150,255,.75) 0%,rgba(96,150,255,.28) 42%,transparent 70%),
    radial-gradient(40% 70% at 60% 0%,rgba(190,140,255,.22) 0%,transparent 70%);}
.hero-shade{position:absolute;inset:0;
  background:linear-gradient(90deg,rgba(26,34,85,.88) 0%,rgba(26,34,85,.50) 34%,rgba(26,34,85,0) 62%);}
.hero-body{position:relative;padding:60px 56px 54px;}
.hero h1{
  font-family:'Bricolage Grotesque',sans-serif;font-weight:800;letter-spacing:-.025em;
  font-size:clamp(2.3rem,4.6vw,3.7rem);line-height:1.02;margin:0 0 14px;color:#fff!important;padding:0;
  text-shadow:0 2px 24px rgba(10,14,50,.55);
}
.hero p{max-width:560px;font-size:1.08rem;line-height:1.55;color:#eef1ff!important;margin:0 0 20px;
  text-shadow:0 1px 14px rgba(10,14,50,.6);}
.hero-models{font-size:.94rem;color:#dfe4ff;text-shadow:0 1px 12px rgba(10,14,50,.6);}
.hero-models b{color:#fff;font-weight:600;}

/* ---------- Section titles ---------- */
.sec-title{font-family:'Bricolage Grotesque',sans-serif;font-weight:700;font-size:1.55rem;letter-spacing:-.01em;margin:8px 0 2px;color:#fff;}
.sec-sub{color:var(--muted);margin-bottom:14px;font-size:.98rem;}
.bay-title{font-family:'Bricolage Grotesque',sans-serif;font-weight:700;font-size:1.12rem;margin:0 0 4px;color:#fff;}
.bay-note{color:var(--muted);font-size:.86rem;margin-bottom:8px;}

/* ---------- Input bays ---------- */
div[data-testid="stVerticalBlockBorderWrapper"]{
  background:var(--panel);border:1px solid var(--line)!important;border-radius:16px;
}
div[data-testid="stVerticalBlockBorderWrapper"]:has(.mark-teal){border-top:3px solid var(--teal)!important;}
div[data-testid="stVerticalBlockBorderWrapper"]:has(.mark-violet){border-top:3px solid var(--violet)!important;}
div[data-testid="stVerticalBlockBorderWrapper"]:has(.mark-ignite){border-top:3px solid var(--ignite)!important;}

/* ---------- Widgets (forced dark so it works with or without config.toml) ---------- */
label, .stMarkdown p, [data-testid="stWidgetLabel"] p,
[data-testid="stCheckbox"] p, [data-testid="stToggle"] p{color:#e6eaff!important;font-weight:500;}

[data-testid="stSelectbox"] .react-aria-ComboBox > div,
[data-baseweb="select"] > div,
[data-baseweb="input"], [data-baseweb="base-input"],
div[data-testid="stNumberInput"] input{
  background:var(--panel-2)!important;border-color:var(--line)!important;color:var(--text)!important;border-radius:10px!important;
}
[data-testid="stSelectbox"] input{color:var(--text)!important;-webkit-text-fill-color:var(--text)!important;}
[data-testid="stSelectbox"] button, [data-testid="stSelectbox"] svg{color:var(--text)!important;fill:var(--text)!important;}
[data-baseweb="select"] *{color:var(--text)!important;}
[data-baseweb="select"] svg{fill:var(--text)!important;}
[data-testid="stNumberInput"] button{background:var(--panel-2)!important;color:var(--text)!important;border-color:var(--line)!important;}
[data-testid="stNumberInput"] button svg{fill:var(--text)!important;}
[data-testid="stNumberInputContainer"], [data-testid="stNumberInputContainer"] > div{
  border-color:var(--line)!important;background:var(--panel-2)!important;border-radius:10px!important;}

/* dropdown list (opens in a floating layer outside the page) */
[data-testid="stSelectboxVirtualDropdown"]{background:var(--panel-2)!important;border:1px solid var(--line);border-radius:12px;}
[data-testid="stSelectboxVirtualDropdown"] [role="option"], [data-testid="stSelectboxVirtualDropdown"] [role="option"] *{color:var(--text)!important;}
[data-testid="stSelectboxVirtualDropdown"] [role="option"][data-focused="true"],
[data-testid="stSelectboxVirtualDropdown"] [role="option"][data-selected="true"]{background:rgba(169,156,255,.30)!important;}
[data-baseweb="popover"] [data-baseweb="menu"], [data-baseweb="popover"] ul{background:var(--panel-2)!important;}
[data-baseweb="popover"] li, [data-baseweb="popover"] li *{color:var(--text)!important;background:transparent;}
[data-baseweb="popover"] li:hover, [data-baseweb="popover"] li[aria-selected="true"]{background:rgba(169,156,255,.30)!important;}

/* header icons (sidebar toggle, toolbar) */
[data-testid="stSidebarCollapseButton"] *, [data-testid="stExpandSidebarButton"] *, [data-testid="stToolbar"] *{color:#dfe4ff!important;fill:#dfe4ff!important;}

[data-testid="stSlider"] [role="slider"]{background:var(--ignite)!important;box-shadow:0 0 0 4px rgba(255,143,94,.28);}
[data-testid="stSliderThumbValue"], [data-testid="stSlider"] [data-testid="stThumbValue"]{color:#ffd0b8!important;}
[data-testid="stTickBarMin"], [data-testid="stTickBarMax"]{color:var(--muted)!important;}

/* ---------- Buttons ---------- */
.stButton > button{
  border-radius:12px;border:1px solid var(--line);background:var(--panel-2);color:var(--text);font-weight:600;padding:.55rem 1rem;
}
.stButton > button p{color:var(--text)!important;}
.stButton > button:hover{border-color:var(--violet);color:#fff;}
.stButton > button[kind="primary"]{
  background:linear-gradient(100deg,#ff8f5e,#ff6b81);border:none;color:#fff;font-size:1.05rem;padding:.8rem 1.4rem;
  box-shadow:0 10px 30px rgba(255,107,129,.32);
}
.stButton > button[kind="primary"] p{color:#fff!important;}
.stButton > button[kind="primary"]:hover{filter:brightness(1.07);color:#fff;}
[data-testid="stDownloadButton"] button{border-radius:12px;background:var(--panel-2);border:1px solid var(--line);color:var(--text);}
[data-testid="stDownloadButton"] button p{color:var(--text)!important;}

/* ---------- Expander ---------- */
[data-testid="stExpander"]{background:var(--panel);border:1px solid var(--line);border-radius:14px;}
[data-testid="stExpander"] summary, [data-testid="stExpander"] summary *{color:var(--text)!important;}
.hist{width:100%;border-collapse:collapse;font-size:.95rem;}
.hist th{color:var(--muted);text-align:left;font-weight:600;padding:8px 10px;border-bottom:1px solid var(--line);}
.hist td{color:var(--text);padding:8px 10px;border-bottom:1px solid rgba(190,200,255,.12);}

/* ---------- Result ---------- */
.gauge-panel{background:var(--panel);border:1px solid var(--line);border-radius:18px;padding:28px 20px 22px;text-align:center;}
.gauge{position:relative;width:300px;height:158px;margin:0 auto;overflow:hidden;}
.gauge-arc{
  position:absolute;top:0;left:0;width:300px;height:300px;border-radius:50%;
  background:conic-gradient(from 270deg,var(--c) 0deg,var(--c) var(--deg),rgba(255,255,255,.14) var(--deg),rgba(255,255,255,.14) 180deg,transparent 180deg);
  -webkit-mask:radial-gradient(farthest-side,transparent 68%,#000 69%);
          mask:radial-gradient(farthest-side,transparent 68%,#000 69%);
  animation:sweep 1.5s cubic-bezier(.2,.8,.2,1);
}
.gauge-center{position:absolute;bottom:0;left:0;right:0;}
.g-val{font-family:'Bricolage Grotesque',sans-serif;font-weight:800;font-size:3.1rem;line-height:1;}
.g-lbl{color:var(--muted);font-size:.9rem;margin-top:4px;}
.g-scale{display:flex;justify-content:space-between;width:300px;margin:6px auto 0;color:var(--muted);font-size:.78rem;}
.risk-pill{display:inline-block;margin-top:16px;padding:6px 16px;border-radius:999px;font-weight:700;font-size:.92rem;}

.verdict{border-radius:18px;padding:22px 26px;margin-bottom:16px;border:1px solid;}
.verdict.fail{background:rgba(255,107,129,.16);border-color:rgba(255,107,129,.55);}
.verdict.ok{background:rgba(62,230,203,.15);border-color:rgba(62,230,203,.55);}
.v-title{font-family:'Bricolage Grotesque',sans-serif;font-weight:800;font-size:1.7rem;letter-spacing:-.01em;color:#fff;}
.v-sub{color:#e0e5ff;margin-top:4px;}

.chip{display:inline-block;padding:6px 13px;border-radius:999px;font-size:.88rem;margin:0 8px 8px 0;border:1px solid;}
.chip.bad{color:#ffd3da;background:rgba(255,107,129,.16);border-color:rgba(255,107,129,.5);}
.chip.good{color:#c9fbf2;background:rgba(62,230,203,.15);border-color:rgba(62,230,203,.5);}
.sig-h{font-weight:700;margin:10px 0 8px;font-size:1rem;color:#fff;}
.sig-note{color:var(--muted);font-size:.8rem;margin-top:2px;}

/* ---------- Sidebar ---------- */
[data-testid="stSidebar"]{background:#141b4a;border-right:1px solid var(--line);}
[data-testid="stSidebar"] [data-testid="stWidgetLabel"] p{color:#e6eaff!important;}
.side-brand{font-family:'Bricolage Grotesque',sans-serif;font-weight:800;font-size:1.5rem;margin:4px 0 2px;color:#fff;}
.side-sub{color:var(--muted);font-size:.9rem;margin-bottom:18px;}
.side-h{font-family:'Bricolage Grotesque',sans-serif;font-weight:700;font-size:1.1rem;color:#fff;margin:6px 0 10px;}
.active-pill{background:rgba(62,230,203,.16);border:1px solid rgba(62,230,203,.55);color:#c9fbf2;
  border-radius:12px;padding:11px 14px;font-weight:600;margin:14px 0 0;}
.model-card{background:var(--panel);border:1px solid var(--line);border-left:3px solid var(--violet);border-radius:12px;padding:12px 14px;margin:14px 0 16px;}
.model-card b{display:block;margin-bottom:4px;color:#fff;}
.model-card span{color:var(--muted);font-size:.88rem;line-height:1.5;}
.side-note{color:var(--muted);font-size:.82rem;line-height:1.5;margin-top:18px;}

.footer{margin-top:44px;padding-top:18px;border-top:1px solid var(--line);color:var(--muted);font-size:.86rem;text-align:center;}

@media (max-width:900px){
  .hero-body{padding:34px 24px;}
}
@media (prefers-reduced-motion:reduce){.gauge-arc{animation:none;}}
</style>
"""
)

# ==========================================
# 3. Hero
# ==========================================
H(
    f"""
<div class="hero">
  <div class="hero-bg" style="background-image:url('{hero_image_src()}')"></div>
  <div class="hero-glow"></div>
  <div class="hero-shade"></div>
  <div class="hero-body">
    <h1>Startup Failure Predictor</h1>
    <p>Describe the founder and the company. Four trained models estimate how likely the startup is to fail and what is driving that risk.</p>
    <div class="hero-models">Models: <b>Logistic Regression</b>, <b>AdaBoost</b>, <b>XGBoost</b> and a <b>Neural Network</b></div>
  </div>
</div>
"""
)

# ==========================================
# 4. Load Selected Model
# ==========================================
model_files = {
    'Logistic Regression': 'logistic_regression.pkl',
    'Adaboost': 'adaboost.pkl',
    'XGBoost': 'xgboost.pkl',
    'MLP (Neural Network)': 'mlp_neural_network.pkl',
}

MODEL_INFO = {
    'Logistic Regression': 'A fast, transparent baseline. It weighs each metric linearly, so it is easy to explain.',
    'Adaboost': 'Combines many small decision trees. Each new tree focuses on the cases the last one got wrong.',
    'XGBoost': 'Gradient-boosted trees. Strong on mixed numeric and categorical data like this.',
    'MLP (Neural Network)': 'A multilayer perceptron that learns non-linear combinations of the metrics.',
}

st.sidebar.markdown(
    '<div class="side-brand">Startup Predictor</div>'
    '<div class="side-sub">Pick a model, then fill in the metrics.</div>'
    '<div class="side-h">⚙️ Model Selection</div>',
    unsafe_allow_html=True,
)
model_choice = st.sidebar.selectbox('Choose a Model:', list(model_files.keys()))


@st.cache_resource
def load_model(file_name):
    return joblib.load(file_name)


try:
    selected_model = load_model(model_files[model_choice])
    st.sidebar.markdown(
        f'<div class="active-pill">✓ Activated: {model_choice}</div>',
        unsafe_allow_html=True,
    )
except Exception as e:
    st.sidebar.error(f'Error loading {model_files[model_choice]}: {e}')
    st.stop()

st.sidebar.markdown(
    f'<div class="model-card"><b>{model_choice}</b><span>{MODEL_INFO[model_choice]}</span></div>',
    unsafe_allow_html=True,
)
celebrate = st.sidebar.toggle('🎉 Celebrate good results', value=True)
st.sidebar.markdown(
    '<div class="side-note">Results are statistical estimates from a trained model. '
    'Use them as a signal to explore, not as a verdict on a real company.</div>',
    unsafe_allow_html=True,
)

# ==========================================
# 5. Input defaults, presets and helpers
# ==========================================
FOUNDER_TYPES = [
    'Solo Hustler',
    'Technical Builder',
    'Serial Entrepreneur',
    'Growth Obsessed Founder',
    'Visionary CEO',
    'Burned-Out Operator',
    'Chaotic Innovator',
    'Calm Operator',
]
INDUSTRIES = [
    'AI', 'SaaS', 'E-commerce', 'FinTech', 'HealthTech',
    'Cybersecurity', 'EdTech', 'Gaming', 'ClimateTech', 'Biotech',
]
FUNDING_STAGES = ['Seed', 'Pre-Seed', 'Series A', 'Bootstrapped', 'Series B', 'Series C']
WORK_MODES = ['Remote', 'Hybrid', 'Office']
CLIMATES = ['Stable Economy', 'Funding Winter', 'Bull Market', 'Recession']
BURNOUT_LEVELS = ['Low', 'Moderate', 'Severe']

DEFAULTS = {
    'founder_type': 'Solo Hustler', 'founder_age': 34, 'founder_exp': 3,
    'work_hours': 63.0, 'sleep_hours': 5.7, 'exercise_days': 3.7, 'vacation_days': 9.0,
    'industry': 'AI', 'funding_stage': 'Seed', 'work_mode': 'Remote',
    'team_size': 15, 'startup_age': 72, 'monthly_growth': 5.5, 'runway': 12.0, 'turnover': 35.0,
    'climate': 'Stable Economy', 'burnout_level': 'Low', 'mental_support': 'No', 'burnout_flag': 0,
    'stress_score': 5.0, 'fatigue_score': 4.5, 'burnout_score': 3.4, 'pressure_score': 6.0,
    'conflict_score': 4.0, 'pmf_score': 5.3, 'wlb_score': 6.7,
}

PRESETS = {
    'healthy': {
        **DEFAULTS,
        'founder_type': 'Serial Entrepreneur', 'founder_age': 38, 'founder_exp': 12,
        'work_hours': 48.0, 'sleep_hours': 7.5, 'exercise_days': 4.0, 'vacation_days': 20.0,
        'industry': 'SaaS', 'funding_stage': 'Series A', 'work_mode': 'Hybrid',
        'team_size': 40, 'startup_age': 36, 'monthly_growth': 18.0, 'runway': 24.0, 'turnover': 10.0,
        'climate': 'Bull Market', 'burnout_level': 'Low', 'mental_support': 'Yes', 'burnout_flag': 0,
        'stress_score': 3.0, 'fatigue_score': 3.0, 'burnout_score': 2.0, 'pressure_score': 4.0,
        'conflict_score': 1.0, 'pmf_score': 8.5, 'wlb_score': 8.0,
    },
    'struggling': {
        **DEFAULTS,
        'founder_type': 'Burned-Out Operator', 'founder_age': 29, 'founder_exp': 1,
        'work_hours': 95.0, 'sleep_hours': 4.0, 'exercise_days': 0.0, 'vacation_days': 0.0,
        'industry': 'E-commerce', 'funding_stage': 'Pre-Seed', 'work_mode': 'Remote',
        'team_size': 4, 'startup_age': 14, 'monthly_growth': -3.0, 'runway': 3.0, 'turnover': 60.0,
        'climate': 'Recession', 'burnout_level': 'Severe', 'mental_support': 'No', 'burnout_flag': 1,
        'stress_score': 9.0, 'fatigue_score': 8.5, 'burnout_score': 9.0, 'pressure_score': 8.5,
        'conflict_score': 8.0, 'pmf_score': 2.5, 'wlb_score': 2.0,
    },
    'default': DEFAULTS,
}

for _k, _v in DEFAULTS.items():
    st.session_state.setdefault(_k, _v)
st.session_state.setdefault('history', [])


def apply_preset(name):
    for k, v in PRESETS[name].items():
        st.session_state[k] = v


def failure_probability(model, df):
    """Probability of class 1 (failure), or None if the model can't provide it."""
    try:
        proba = model.predict_proba(df)[0]
        classes = list(getattr(model, 'classes_', [0, 1]))
        idx = classes.index(1) if 1 in classes else len(proba) - 1
        return float(proba[idx])
    except Exception:
        return None


def risk_band(p):
    if p < 0.33:
        return 'Low risk', 'var(--low)', 'rgba(62,230,203,.18)'
    if p < 0.66:
        return 'Moderate risk', 'var(--mid)', 'rgba(255,209,102,.18)'
    return 'High risk', 'var(--high)', 'rgba(255,107,129,.18)'


def read_signals(s):
    """Simple rule-based read of the inputs (not model output)."""
    bad, good = [], []
    if s['runway'] < 6: bad.append('⏳ Runway under 6 months')
    if s['sleep_hours'] < 5: bad.append('😴 Sleeping under 5 hours')
    if s['work_hours'] > 80: bad.append('🔥 More than 80 work hours a week')
    if s['burnout_score'] >= 7 or s['burnout_level'] == 'Severe': bad.append('🪫 Severe burnout')
    if s['conflict_score'] >= 7: bad.append('⚔️ High cofounder conflict')
    if s['turnover'] >= 40: bad.append('🚪 Employee turnover of 40% or more')
    if s['pmf_score'] < 4: bad.append('🎯 Weak product-market fit')
    if s['monthly_growth'] < 0: bad.append('📉 Revenue is shrinking')
    if s['pressure_score'] >= 8: bad.append('💼 Heavy investor pressure')
    if s['runway'] >= 18: good.append('🛫 Runway of 18 months or more')
    if s['pmf_score'] >= 7: good.append('🎯 Strong product-market fit')
    if s['monthly_growth'] >= 10: good.append('📈 Revenue growing 10%+ a month')
    if s['sleep_hours'] >= 7: good.append('😌 Healthy sleep')
    if s['turnover'] <= 15: good.append('🤝 Stable team')
    if s['conflict_score'] <= 3: good.append('🕊️ Low cofounder conflict')
    if s['wlb_score'] >= 7: good.append('⚖️ Good work-life balance')
    if s['mental_support'] == 'Yes': good.append('💬 Seeks mental health support')
    return bad, good


# ==========================================
# 6. User Input Features
# ==========================================
H(
    '<div class="sec-title">📝 Founder & Startup Metrics</div>'
    '<div class="sec-sub">Start from your own numbers, or load an example to see how the models react.</div>'
)

p1, p2, p3, _ = st.columns([1.1, 1.2, 1, 3])
p1.button('🌱 Healthy startup', on_click=apply_preset, args=('healthy',), **STRETCH)
p2.button('🔥 Struggling startup', on_click=apply_preset, args=('struggling',), **STRETCH)
p3.button('↺ Reset', on_click=apply_preset, args=('default',), **STRETCH)

st.write('')
col1, col2, col3 = st.columns(3)

with col1:
    with st.container(border=True):
        H('<span class="mark-teal"></span><div class="bay-title">👤 Founder Profile</div>'
          '<div class="bay-note">Who is running the company, and how they are holding up.</div>')
        founder_type = st.selectbox('Founder Type', FOUNDER_TYPES, key='founder_type')
        founder_age = st.number_input('Founder Age', min_value=18, max_value=80, key='founder_age')
        founder_exp = st.number_input('Experience (Years)', min_value=0, max_value=40, key='founder_exp')
        work_hours = st.slider('Weekly Work Hours', 20.0, 110.0, step=0.5, key='work_hours')
        sleep_hours = st.slider('Daily Sleep Hours', 2.0, 10.0, step=0.1, key='sleep_hours')
        exercise_days = st.slider('Exercise Days (Weekly)', 0.0, 7.0, step=0.1, key='exercise_days')
        vacation_days = st.number_input(
            'Vacation Days Taken (Yearly)', min_value=0.0, max_value=40.0, key='vacation_days'
        )

with col2:
    with st.container(border=True):
        H('<span class="mark-violet"></span><div class="bay-title">🏢 Startup & Funding Details</div>'
          '<div class="bay-note">The company, its money and its momentum.</div>')
        industry = st.selectbox('Industry', INDUSTRIES, key='industry')
        funding_stage = st.selectbox('Funding Stage', FUNDING_STAGES, key='funding_stage')
        work_mode = st.selectbox('Work Mode', WORK_MODES, key='work_mode')
        team_size = st.number_input('Team Size', min_value=1, max_value=1000, key='team_size')
        startup_age = st.number_input('Startup Age (Months)', min_value=1, max_value=200, key='startup_age')
        monthly_growth = st.number_input('Monthly Revenue Growth (%)', key='monthly_growth')
        runway = st.number_input('Runway Months Remaining', key='runway')
        turnover = st.number_input('Employee Turnover (%)', key='turnover')

with col3:
    with st.container(border=True):
        H('<span class="mark-ignite"></span><div class="bay-title">🧠 Psychological & Environmental Metrics</div>'
          '<div class="bay-note">Pressure, stress and the market around the team.</div>')
        climate = st.selectbox('Economic Climate', CLIMATES, key='climate')
        burnout_level = st.selectbox('Burnout Level', BURNOUT_LEVELS, key='burnout_level')
        mental_support = st.selectbox('Seeks Mental Health Support?', ['No', 'Yes'], key='mental_support')
        founder_burnout_flag = st.selectbox('Founder Burnout Flag', [0, 1], key='burnout_flag')
        stress_score = st.slider('Stress Score (1-10)', 1.0, 10.0, step=0.1, key='stress_score')
        fatigue_score = st.slider('Decision Fatigue Score (1-10)', 1.0, 10.0, step=0.1, key='fatigue_score')
        burnout_score = st.slider('Burnout Score (1-10)', 1.0, 10.0, step=0.1, key='burnout_score')
        pressure_score = st.slider('Investor Pressure Score (1-10)', 1.0, 10.0, step=0.1, key='pressure_score')
        conflict_score = st.slider('Cofounder Conflict Score (0-10)', 0.0, 10.0, step=0.1, key='conflict_score')
        pmf_score = st.slider('Product-Market Fit Score (1-10)', 1.0, 10.0, step=0.1, key='pmf_score')
        wlb_score = st.slider('Work-Life Balance Score (1-10)', 1.0, 10.0, step=0.1, key='wlb_score')

# ==========================================
# 7. Prediction & Output Display
# ==========================================
st.markdown('---')

if st.button('🔮 Predict Startup Failure Risk', type='primary', **STRETCH):
    user_input_df = pd.DataFrame(
        [
            {
                'Founder_Type': founder_type,
                'Economic_Climate': climate,
                'Founder_Age': founder_age,
                'Founder_Experience_Years': founder_exp,
                'Industry': industry,
                'Funding_Stage': funding_stage,
                'Work_Mode': work_mode,
                'Team_Size': team_size,
                'Startup_Age_Months': startup_age,
                'Weekly_Work_Hours': work_hours,
                'Sleep_Hours': sleep_hours,
                'Exercise_Days_Per_Week': exercise_days,
                'Vacation_Days_Taken': vacation_days,
                'Investor_Pressure_Score': pressure_score,
                'Cofounder_Conflict_Score': conflict_score,
                'Stress_Score': stress_score,
                'Decision_Fatigue_Score': fatigue_score,
                'Burnout_Score': burnout_score,
                'Burnout_Level': burnout_level,
                'Founder_Burnout_Flag': founder_burnout_flag,
                'Monthly_Revenue_Growth_Percent': monthly_growth,
                'Runway_Months_Remaining': runway,
                'Product_Market_Fit_Score': pmf_score,
                'Employee_Turnover_Percent': turnover,
                'Work_Life_Balance_Score': wlb_score,
                'Seeks_Mental_Health_Support': mental_support,
            }
        ]
    )

    try:
        with st.spinner('Running the model...'):
            prediction = selected_model.predict(user_input_df)[0]
            prob = failure_probability(selected_model, user_input_df)

        failed = prediction == 1

        H('<div class="sec-title">📊 Prediction Result</div>')
        left, right = st.columns([5, 6], gap='large')

        with left:
            if prob is not None:
                label, color, tint = risk_band(prob)
                H(
                    f"""
                <div class="gauge-panel">
                  <div class="gauge">
                    <div class="gauge-arc" style="--c:{color};--deg:{prob * 180:.1f}deg"></div>
                    <div class="gauge-center">
                      <div class="g-val" style="color:{color}">{prob:.0%}</div>
                      <div class="g-lbl">Chance of failure</div>
                    </div>
                  </div>
                  <div class="g-scale"><span>0%</span><span>100%</span></div>
                  <div class="risk-pill" style="color:{color};background:{tint}">{label}</div>
                </div>
                """
                )
            else:
                st.info('This model does not expose probabilities, so only the verdict is shown.')

        with right:
            if failed:
                H(
                    '<div class="verdict fail"><div class="v-title">⚠️ Startup Failure: YES</div>'
                    '<div class="v-sub">High risk of failure</div></div>'
                )
            else:
                H(
                    '<div class="verdict ok"><div class="v-title">✅ Startup Failure: NO</div>'
                    '<div class="v-sub">Low risk, likely to succeed</div></div>'
                )

            bad, good = read_signals(
                dict(
                    runway=runway, sleep_hours=sleep_hours, work_hours=work_hours,
                    burnout_score=burnout_score, burnout_level=burnout_level,
                    conflict_score=conflict_score, turnover=turnover, pmf_score=pmf_score,
                    monthly_growth=monthly_growth, pressure_score=pressure_score,
                    wlb_score=wlb_score, mental_support=mental_support,
                )
            )
            if bad:
                H('<div class="sig-h">Warning signs in your inputs</div>'
                  + ''.join(f'<span class="chip bad">{b}</span>' for b in bad))
            if good:
                H('<div class="sig-h">Strengths in your inputs</div>'
                  + ''.join(f'<span class="chip good">{g}</span>' for g in good))
            if not bad and not good:
                H('<div class="sig-note">No standout strengths or warning signs in these inputs.</div>')
            H('<div class="sig-note">These chips come from simple rules on your inputs. The verdict above comes from the model.</div>')

        # ---- History + download ----
        st.session_state.history.append(
            {
                'Time': datetime.now().strftime('%H:%M:%S'),
                'Model': model_choice,
                'Result': 'Failure' if failed else 'Survives',
                'Failure probability': f'{prob:.0%}' if prob is not None else '-',
            }
        )
        report = user_input_df.assign(
            Model=model_choice,
            Prediction='Failure' if failed else 'Survives',
            Failure_Probability=prob,
        )
        st.write('')
        st.download_button(
            '⬇️ Download this result (CSV)',
            report.to_csv(index=False).encode('utf-8'),
            file_name='startup_prediction.csv',
            mime='text/csv',
        )

        if celebrate and not failed:
            st.balloons()

    except Exception as err:
        st.error(f'An error occurred during prediction: {err}')

if st.session_state.history:
    with st.expander(f'🕘 Prediction history ({len(st.session_state.history)})'):
        cols = ['Time', 'Model', 'Result', 'Failure probability']
        body = ''.join(
            '<tr>' + ''.join(f'<td>{row[c]}</td>' for c in cols) + '</tr>'
            for row in st.session_state.history[::-1]
        )
        head = ''.join(f'<th>{c}</th>' for c in cols)
        H(f'<table class="hist"><thead><tr>{head}</tr></thead><tbody>{body}</tbody></table>')

H('<div class="footer">Graduation project · Built with Streamlit and scikit-learn</div>')


# py -m streamlit run stream.py