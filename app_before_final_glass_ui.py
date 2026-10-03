import streamlit as st
import numpy as np
import hashlib
import time
from qiskit import QuantumCircuit
from qiskit.quantum_info import Statevector
from qiskit.primitives import StatevectorSampler

from qds_attack_simulator import QDSAttackSimulator

# ============================================================
# SESSION STATE INITIALIZATION
# ============================================================

if "attack_simulator" not in st.session_state:
    st.session_state.attack_simulator = QDSAttackSimulator()
else:
    st.session_state.attack_simulator = QDSAttackSimulator()

if "used_signatures" not in st.session_state:
    st.session_state.used_signatures = set()

attack_simulator = st.session_state.attack_simulator


# ============================================================
# PAGE CONFIG & PREMIUM DARK GLASSMORPHISM THEME
# ============================================================

st.set_page_config(
    page_title="Quantum Digital Signature Security",
    page_icon="⚛️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Premium Dark Glassmorphism CSS Engine
st.markdown("""
<style>
:root {
    --bg-dark: #05070D;
    --bg-gradient: radial-gradient(circle at 15% 20%, rgba(139, 92, 246, 0.12), transparent 40%),
                    radial-gradient(circle at 85% 75%, rgba(6, 182, 212, 0.08), transparent 40%),
                    radial-gradient(circle at 50% 50%, rgba(11, 16, 32, 0.9), #05070D);
                    
    --glass-bg: rgba(255, 255, 255, 0.04);
    --glass-bg-hover: rgba(255, 255, 255, 0.07);
    --glass-surface: rgba(17, 21, 28, 0.65);
    --glass-border: rgba(255, 255, 255, 0.10);
    --glass-border-purple: rgba(139, 92, 246, 0.35);
    --glass-border-green: rgba(34, 197, 94, 0.35);
    --glass-border-amber: rgba(245, 158, 11, 0.35);
    --glass-border-red: rgba(239, 68, 68, 0.35);
    
    --text-primary: #F5F7FA;
    --text-secondary: #94A3B8;
    --text-muted: #64748B;
    
    --purple-primary: #8B5CF6;
    --purple-light: #A78BFA;
    --cyan-accent: #06B6D4;
    --blue-accent: #3B82F6;
    --green-accent: #22C55E;
    --amber-accent: #F59E0B;
    --red-accent: #EF4444;
}

/* Base App Setup */
.stApp {
    background: var(--bg-gradient) !important;
    background-attachment: fixed !important;
    color: var(--text-primary) !important;
    font-family: -apple-system, BlinkMacSystemFont, "Inter", "Segoe UI", Roboto, sans-serif !important;
}

.block-container {
    max-width: 1440px !important;
    padding-top: 1.2rem !important;
    padding-bottom: 2.5rem !important;
}

/* Sidebar Styling - Frosted Glass Panel */
[data-testid="stSidebar"] {
    background: rgba(8, 11, 18, 0.75) !important;
    backdrop-filter: blur(20px) !important;
    -webkit-backdrop-filter: blur(20px) !important;
    border-right: 1px solid var(--glass-border) !important;
}

[data-testid="stSidebar"] * {
    color: var(--text-primary) !important;
}

[data-testid="stSidebar"] .stCaption {
    color: var(--text-secondary) !important;
}

/* Authoritative Dark Glass Controls in Sidebar */

/* Digital Message & Sidebar Inputs */
[data-testid="stSidebar"] [data-testid="stTextInput"],
[data-testid="stSidebar"] [data-testid="stTextInput"] > div,
[data-testid="stSidebar"] [data-testid="stTextInput"] [data-baseweb="input"],
[data-testid="stSidebar"] [data-testid="stTextInput"] [data-baseweb="input"] > div,
[data-testid="stSidebar"] [data-testid="stTextInput"] input,
[data-testid="stSidebar"] input,
[data-testid="stSidebar"] textarea,
[data-testid="stSidebar"] [data-testid="stNumberInput"] input {
    background-color: #151922 !important;
    background: #151922 !important;
    color: #F5F7FA !important;
    -webkit-text-fill-color: #F5F7FA !important;
    border: 1px solid rgba(255, 255, 255, 0.18) !important;
    border-radius: 12px !important;
    box-shadow: none !important;
    caret-color: #FFFFFF !important;
    font-weight: 500 !important;
}

[data-testid="stSidebar"] [data-testid="stTextInput"] input::placeholder,
[data-testid="stSidebar"] input::placeholder,
[data-testid="stSidebar"] textarea::placeholder {
    color: #9CA3AF !important;
    -webkit-text-fill-color: #9CA3AF !important;
}

[data-testid="stSidebar"] [data-testid="stTextInput"] input:focus,
[data-testid="stSidebar"] [data-testid="stTextInput"] [data-baseweb="input"]:focus-within,
[data-testid="stSidebar"] input:focus {
    border-color: #8B5CF6 !important;
    box-shadow: 0 0 0 1px rgba(139, 92, 246, 0.35) !important;
    outline: none !important;
}

/* Quantum Signature State & Attack Simulation Dropdowns (BaseWeb Select) */
[data-testid="stSidebar"] [data-testid="stSelectbox"],
[data-testid="stSidebar"] [data-testid="stSelectbox"] [data-baseweb="select"],
[data-testid="stSidebar"] [data-testid="stSelectbox"] [data-baseweb="select"] > div,
[data-testid="stSidebar"] [data-testid="stSelectbox"] [data-baseweb="select"] div,
[data-testid="stSidebar"] [data-testid="stSelectbox"] [data-baseweb="select"] [data-baseweb="value-container"],
[data-testid="stSidebar"] [data-testid="stSelectbox"] [data-baseweb="select"] [data-baseweb="single-value"],
[data-testid="stSidebar"] [data-testid="stSelectbox"] [data-baseweb="select"] input {
    background-color: #151922 !important;
    background: #151922 !important;
    color: #F5F7FA !important;
    -webkit-text-fill-color: #F5F7FA !important;
}

[data-testid="stSidebar"] [data-testid="stSelectbox"] [data-baseweb="select"] > div {
    border: 1px solid rgba(255, 255, 255, 0.18) !important;
    border-radius: 12px !important;
    background-color: #151922 !important;
    background: #151922 !important;
}

[data-testid="stSidebar"] [data-testid="stSelectbox"] [data-baseweb="select"]:hover > div {
    border-color: rgba(139, 92, 246, 0.5) !important;
    background-color: #151922 !important;
    background: #151922 !important;
}

[data-testid="stSidebar"] [data-testid="stSelectbox"] [data-baseweb="select"]:focus-within > div {
    border-color: #8B5CF6 !important;
    box-shadow: 0 0 0 1px rgba(139, 92, 246, 0.35) !important;
}

[data-testid="stSidebar"] [data-testid="stSelectbox"] [data-baseweb="select"] span,
[data-testid="stSidebar"] [data-testid="stSelectbox"] [data-baseweb="select"] p,
[data-testid="stSidebar"] [data-testid="stSelectbox"] [data-baseweb="select"] div[role="button"] {
    color: #F5F7FA !important;
    -webkit-text-fill-color: #F5F7FA !important;
}

[data-testid="stSidebar"] [data-testid="stSelectbox"] [data-baseweb="select"] svg {
    color: #D1D5DB !important;
    fill: #D1D5DB !important;
}

/* BaseWeb Opened Dropdown Popup Menu Options */
div[data-baseweb="popover"],
div[data-baseweb="popover"] > div,
div[data-baseweb="menu"],
ul[data-baseweb="menu"],
div[role="listbox"],
ul[role="listbox"] {
    background-color: #151922 !important;
    background: #151922 !important;
    border: 1px solid rgba(255, 255, 255, 0.18) !important;
    border-radius: 12px !important;
    box-shadow: 0 10px 30px rgba(0, 0, 0, 0.5) !important;
}

div[data-baseweb="popover"] li,
div[data-baseweb="menu"] li,
ul[data-baseweb="menu"] li,
li[role="option"] {
    background-color: #151922 !important;
    background: #151922 !important;
    color: #F5F7FA !important;
    -webkit-text-fill-color: #F5F7FA !important;
}

div[data-baseweb="popover"] li *,
div[data-baseweb="menu"] li *,
ul[data-baseweb="menu"] li *,
li[role="option"] * {
    color: #F5F7FA !important;
    -webkit-text-fill-color: #F5F7FA !important;
}

li[role="option"]:hover,
li[role="option"]:hover * {
    background-color: rgba(139, 92, 246, 0.18) !important;
    background: rgba(139, 92, 246, 0.18) !important;
    color: #FFFFFF !important;
    -webkit-text-fill-color: #FFFFFF !important;
}

li[role="option"][aria-selected="true"],
li[role="option"][aria-selected="true"] *,
div[data-baseweb="menu"] [aria-selected="true"] {
    background-color: rgba(139, 92, 246, 0.25) !important;
    background: rgba(139, 92, 246, 0.25) !important;
    color: #FFFFFF !important;
    -webkit-text-fill-color: #FFFFFF !important;
}

/* Sidebar Buttons */
/* Primary Run Verification Button - Purple Glass Gradient */
[data-testid="stSidebar"] [data-testid="stButton"] button[kind="primary"],
[data-testid="stSidebar"] button[kind="primary"] {
    background: linear-gradient(135deg, rgba(139, 92, 246, 0.85) 0%, rgba(109, 40, 217, 0.95) 100%) !important;
    backdrop-filter: blur(12px) !important;
    border: 1px solid rgba(167, 139, 250, 0.4) !important;
    box-shadow: 0 4px 20px rgba(139, 92, 246, 0.4) !important;
    border-radius: 12px !important;
    min-height: 48px !important;
    transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1) !important;
}

[data-testid="stSidebar"] [data-testid="stButton"] button[kind="primary"] p,
[data-testid="stSidebar"] [data-testid="stButton"] button[kind="primary"] span,
[data-testid="stSidebar"] button[kind="primary"] p,
[data-testid="stSidebar"] button[kind="primary"] span {
    color: #FFFFFF !important;
    -webkit-text-fill-color: #FFFFFF !important;
    font-weight: 800 !important;
    letter-spacing: 0.3px !important;
}

[data-testid="stSidebar"] [data-testid="stButton"] button[kind="primary"]:hover,
[data-testid="stSidebar"] button[kind="primary"]:hover {
    background: linear-gradient(135deg, rgba(167, 139, 250, 0.95) 0%, rgba(124, 58, 237, 1) 100%) !important;
    box-shadow: 0 6px 24px rgba(139, 92, 246, 0.6) !important;
    transform: translateY(-1px) !important;
}

/* Reset Replay History Button - Dark Neutral Glass */
[data-testid="stSidebar"] [data-testid="stButton"] button[kind="secondary"],
[data-testid="stSidebar"] [data-testid="stButton"] button:not([kind="primary"]),
[data-testid="stSidebar"] button[kind="secondary"] {
    background: rgba(23, 27, 34, 0.65) !important;
    backdrop-filter: blur(12px) !important;
    border: 1px solid rgba(255, 255, 255, 0.12) !important;
    border-radius: 12px !important;
    min-height: 42px !important;
    transition: all 0.2s ease-in-out !important;
}

[data-testid="stSidebar"] [data-testid="stButton"] button[kind="secondary"] p,
[data-testid="stSidebar"] [data-testid="stButton"] button[kind="secondary"] span,
[data-testid="stSidebar"] [data-testid="stButton"] button:not([kind="primary"]) p,
[data-testid="stSidebar"] [data-testid="stButton"] button:not([kind="primary"]) span,
[data-testid="stSidebar"] button[kind="secondary"] p,
[data-testid="stSidebar"] button[kind="secondary"] span {
    color: #CBD5E1 !important;
    -webkit-text-fill-color: #CBD5E1 !important;
    font-weight: 600 !important;
}

[data-testid="stSidebar"] [data-testid="stButton"] button[kind="secondary"]:hover,
[data-testid="stSidebar"] [data-testid="stButton"] button:not([kind="primary"]):hover,
[data-testid="stSidebar"] button[kind="secondary"]:hover {
    background: rgba(30, 36, 46, 0.85) !important;
    border-color: rgba(245, 158, 11, 0.4) !important;
}

[data-testid="stSidebar"] [data-testid="stButton"] button[kind="secondary"]:hover p,
[data-testid="stSidebar"] [data-testid="stButton"] button[kind="secondary"]:hover span,
[data-testid="stSidebar"] [data-testid="stButton"] button:not([kind="primary"]):hover p,
[data-testid="stSidebar"] [data-testid="stButton"] button:not([kind="primary"]):hover span,
[data-testid="stSidebar"] button[kind="secondary"]:hover p,
[data-testid="stSidebar"] button[kind="secondary"]:hover span {
    color: #FFFFFF !important;
    -webkit-text-fill-color: #FFFFFF !important;
}

/* Main Body Controlled Benchmark Buttons - Dark Glass + Purple Glow */
.main [data-testid="stButton"] button,
div:not([data-testid="stSidebar"]) > [data-testid="stButton"] button,
button[aria-label*="Benchmark"],
button[aria-label*="Controlled"] {
    background: rgba(17, 21, 28, 0.75) !important;
    backdrop-filter: blur(14px) !important;
    -webkit-backdrop-filter: blur(14px) !important;
    border: 1px solid rgba(139, 92, 246, 0.4) !important;
    border-radius: 12px !important;
    min-height: 46px !important;
    box-shadow: 0 4px 18px rgba(139, 92, 246, 0.18) !important;
    transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1) !important;
}

.main [data-testid="stButton"] button p,
.main [data-testid="stButton"] button span,
div:not([data-testid="stSidebar"]) > [data-testid="stButton"] button p,
div:not([data-testid="stSidebar"]) > [data-testid="stButton"] button span {
    color: #F5F7FA !important;
    -webkit-text-fill-color: #F5F7FA !important;
    font-weight: 700 !important;
}

.main [data-testid="stButton"] button:hover,
div:not([data-testid="stSidebar"]) > [data-testid="stButton"] button:hover {
    background: rgba(34, 26, 53, 0.85) !important;
    border-color: rgba(167, 139, 250, 0.7) !important;
    box-shadow: 0 6px 24px rgba(139, 92, 246, 0.4) !important;
    transform: translateY(-1px) !important;
}

.main [data-testid="stButton"] button:hover p,
.main [data-testid="stButton"] button:hover span,
div:not([data-testid="stSidebar"]) > [data-testid="stButton"] button:hover p,
div:not([data-testid="stSidebar"]) > [data-testid="stButton"] button:hover span {
    color: #FFFFFF !important;
    -webkit-text-fill-color: #FFFFFF !important;
}

/* Glass Hero Card */
.glass-hero {
    background: rgba(17, 21, 28, 0.65);
    backdrop-filter: blur(20px);
    -webkit-backdrop-filter: blur(20px);
    border: 1px solid rgba(255, 255, 255, 0.10);
    border-radius: 20px;
    padding: 30px 36px;
    margin-bottom: 24px;
    position: relative;
    box-shadow: 0 14px 40px rgba(0, 0, 0, 0.45);
    overflow: hidden;
}

.glass-hero::before {
    content: "";
    position: absolute;
    top: -50px; right: -50px;
    width: 250px; height: 250px;
    border-radius: 50%;
    background: radial-gradient(circle, rgba(139, 92, 246, 0.25) 0%, transparent 70%);
    pointer-events: none;
}

.glass-hero::after {
    content: "";
    position: absolute;
    bottom: -40px; left: -40px;
    width: 200px; height: 200px;
    border-radius: 50%;
    background: radial-gradient(circle, rgba(6, 182, 212, 0.15) 0%, transparent 70%);
    pointer-events: none;
}

.hero-kicker {
    color: var(--purple-light);
    font-size: 12px;
    font-weight: 800;
    letter-spacing: 2.2px;
    text-transform: uppercase;
    margin-bottom: 6px;
}

.hero-title {
    color: #F5F7FA;
    font-size: clamp(26px, 3.5vw, 42px);
    font-weight: 900;
    line-height: 1.15;
    margin: 0 0 8px 0;
}

.hero-subtitle {
    color: var(--text-secondary);
    font-size: 16px;
    margin-bottom: 20px;
    max-width: 900px;
}

/* Glass Badges */
.glass-badge-purple {
    display: inline-block;
    padding: 5px 14px;
    margin-right: 8px;
    margin-bottom: 6px;
    border-radius: 999px;
    background: rgba(139, 92, 246, 0.12);
    backdrop-filter: blur(8px);
    border: 1px solid rgba(139, 92, 246, 0.35);
    color: #C4B5FD;
    font-size: 12px;
    font-weight: 700;
}

.glass-badge-blue {
    display: inline-block;
    padding: 5px 14px;
    margin-right: 8px;
    margin-bottom: 6px;
    border-radius: 999px;
    background: rgba(59, 130, 246, 0.12);
    backdrop-filter: blur(8px);
    border: 1px solid rgba(59, 130, 246, 0.35);
    color: #93C5FD;
    font-size: 12px;
    font-weight: 700;
}

.glass-badge-cyan {
    display: inline-block;
    padding: 5px 14px;
    margin-right: 8px;
    margin-bottom: 6px;
    border-radius: 999px;
    background: rgba(6, 182, 212, 0.12);
    backdrop-filter: blur(8px);
    border: 1px solid rgba(6, 182, 212, 0.35);
    color: #67E8F9;
    font-size: 12px;
    font-weight: 700;
}

.glass-badge-amber {
    display: inline-block;
    padding: 5px 14px;
    margin-right: 8px;
    margin-bottom: 6px;
    border-radius: 999px;
    background: rgba(245, 158, 11, 0.12);
    backdrop-filter: blur(8px);
    border: 1px solid rgba(245, 158, 11, 0.35);
    color: #FCD34D;
    font-size: 12px;
    font-weight: 700;
}

.glass-badge-green {
    display: inline-block;
    padding: 5px 14px;
    margin-right: 8px;
    margin-bottom: 6px;
    border-radius: 999px;
    background: rgba(34, 197, 94, 0.12);
    backdrop-filter: blur(8px);
    border: 1px solid rgba(34, 197, 94, 0.35);
    color: #86EFAC;
    font-size: 12px;
    font-weight: 700;
}

.glass-badge-red {
    display: inline-block;
    padding: 5px 14px;
    margin-right: 8px;
    margin-bottom: 6px;
    border-radius: 999px;
    background: rgba(239, 68, 68, 0.12);
    backdrop-filter: blur(8px);
    border: 1px solid rgba(239, 68, 68, 0.35);
    color: #FCA5A5;
    font-size: 12px;
    font-weight: 700;
}

/* Glass Section Title */
.section-header {
    color: #F5F7FA;
    font-size: 20px;
    font-weight: 800;
    margin: 28px 0 6px 0;
    display: flex;
    align-items: center;
    gap: 12px;
}

.sec-num {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    width: 30px;
    height: 30px;
    border-radius: 10px;
    background: rgba(139, 92, 246, 0.15);
    backdrop-filter: blur(8px);
    border: 1px solid rgba(139, 92, 246, 0.4);
    color: #C4B5FD;
    font-size: 13px;
    font-weight: 800;
}

.sec-num-green {
    background: rgba(34, 197, 94, 0.15);
    border-color: rgba(34, 197, 94, 0.4);
    color: #4ADE80;
}

.sec-num-amber {
    background: rgba(245, 158, 11, 0.15);
    border-color: rgba(245, 158, 11, 0.4);
    color: #FBBF24;
}

.sec-num-red {
    background: rgba(239, 68, 68, 0.15);
    border-color: rgba(239, 68, 68, 0.4);
    color: #F87171;
}

.section-subheader {
    color: var(--text-secondary);
    font-size: 14px;
    margin-bottom: 18px;
}

/* Glass Cards */
.glass-card {
    background: rgba(17, 21, 28, 0.55);
    backdrop-filter: blur(18px);
    -webkit-backdrop-filter: blur(18px);
    border: 1px solid rgba(255, 255, 255, 0.08);
    border-radius: 16px;
    padding: 22px;
    margin-bottom: 16px;
    box-shadow: 0 8px 32px rgba(0, 0, 0, 0.35);
    transition: all 0.25s ease;
}

.glass-card:hover {
    background: rgba(22, 27, 34, 0.65);
    border-color: rgba(255, 255, 255, 0.14);
    transform: translateY(-1px);
}

.glass-card-accent-purple { border-top: 3px solid var(--purple-primary); }
.glass-card-accent-green { border-top: 3px solid var(--green-accent); }
.glass-card-accent-amber { border-top: 3px solid var(--amber-accent); }
.glass-card-accent-red { border-top: 3px solid var(--red-accent); }
.glass-card-accent-cyan { border-top: 3px solid var(--cyan-accent); }

.glass-card h3, .glass-card h4 {
    color: #F5F7FA;
    margin-top: 0;
    margin-bottom: 8px;
    font-weight: 800;
}

.glass-card p {
    color: var(--text-secondary);
    line-height: 1.55;
    margin: 0;
    font-size: 14px;
}

/* Code / Terminal Glass Container */
.statevector-box {
    background: rgba(9, 13, 20, 0.85);
    backdrop-filter: blur(10px);
    border: 1px solid rgba(255, 255, 255, 0.1);
    border-radius: 12px;
    padding: 14px;
    font-family: 'SFMono-Regular', Consolas, 'Liberation Mono', Menlo, monospace;
    color: #C4B5FD;
    font-size: 13px;
    word-break: break-all;
    margin-top: 10px;
}

/* Result Banners */
.result-card-safe {
    padding: 22px 26px;
    border-radius: 16px;
    background: linear-gradient(135deg, rgba(34, 197, 94, 0.12), rgba(10, 38, 26, 0.85));
    backdrop-filter: blur(18px);
    border: 1px solid rgba(34, 197, 94, 0.45);
    box-shadow: 0 8px 32px rgba(34, 197, 94, 0.15);
    margin-bottom: 20px;
}

.result-card-threat {
    padding: 22px 26px;
    border-radius: 16px;
    background: linear-gradient(135deg, rgba(239, 68, 68, 0.14), rgba(48, 14, 19, 0.85));
    backdrop-filter: blur(18px);
    border: 1px solid rgba(239, 68, 68, 0.45);
    box-shadow: 0 8px 32px rgba(239, 68, 68, 0.15);
    margin-bottom: 20px;
}

.result-card-invisible {
    padding: 22px 26px;
    border-radius: 16px;
    background: linear-gradient(135deg, rgba(245, 158, 11, 0.12), rgba(42, 30, 10, 0.85));
    backdrop-filter: blur(18px);
    border: 1px solid rgba(245, 158, 11, 0.45);
    box-shadow: 0 8px 32px rgba(245, 158, 11, 0.15);
    margin-bottom: 20px;
}

.result-title {
    font-size: 24px;
    font-weight: 900;
    color: #F5F7FA;
}

.result-subtitle {
    font-size: 14px;
    color: var(--text-secondary);
    margin-top: 6px;
}

/* Metric Boxes */
[data-testid="stMetric"] {
    background: rgba(17, 21, 28, 0.60) !important;
    backdrop-filter: blur(14px) !important;
    border: 1px solid rgba(255, 255, 255, 0.08) !important;
    border-radius: 14px !important;
    padding: 14px 16px !important;
    box-shadow: 0 6px 20px rgba(0, 0, 0, 0.25) !important;
}

[data-testid="stMetricValue"] {
    color: #F5F7FA !important;
    font-size: 22px !important;
    font-weight: 800 !important;
}

[data-testid="stMetricLabel"] {
    color: #94A3B8 !important;
    font-size: 12px !important;
    text-transform: uppercase !important;
    letter-spacing: 0.6px !important;
}

/* Pipeline Flow */
.pipeline-flow {
    display: flex;
    gap: 12px;
    align-items: center;
    justify-content: space-between;
    margin: 18px 0;
    flex-wrap: wrap;
}

.pipeline-step {
    flex: 1;
    min-width: 140px;
    background: rgba(17, 21, 28, 0.65);
    backdrop-filter: blur(14px);
    border: 1px solid rgba(255, 255, 255, 0.1);
    border-radius: 14px;
    padding: 16px 12px;
    text-align: center;
    color: #F5F7FA;
    font-size: 13px;
    font-weight: 700;
}

.pipeline-arrow {
    color: #A78BFA;
    font-size: 20px;
    font-weight: bold;
}

.disclaimer-box {
    background: rgba(6, 182, 212, 0.06);
    backdrop-filter: blur(14px);
    border: 1px solid rgba(6, 182, 212, 0.3);
    border-radius: 14px;
    padding: 16px 20px;
    color: #A5F3FC;
    font-size: 13px;
    line-height: 1.5;
    margin-top: 24px;
}

.footer-text {
    text-align: center;
    color: var(--text-muted);
    font-size: 13px;
    margin-top: 40px;
    padding-top: 20px;
    border-top: 1px solid rgba(255, 255, 255, 0.08);
}
</style>
""", unsafe_allow_html=True)


# ============================================================
# HELPER QUANTUM FUNCTIONS (BACKEND UNCHANGED)
# ============================================================

def get_quantum_statevector(state_name):
    """Generate exact Qiskit Statevector for |0>, |1>, |+>, |->."""
    qc = QuantumCircuit(1)
    if state_name == "0":
        pass
    elif state_name == "1":
        qc.x(0)
    elif state_name == "+":
        qc.h(0)
    elif state_name == "-":
        qc.x(0)
        qc.h(0)
    return Statevector.from_instruction(qc)


def format_statevector_str(sv):
    """Format statevector complex coefficients cleanly."""
    data = sv.data
    c0 = data[0]
    c1 = data[1]
    
    parts = []
    if abs(c0) > 1e-6:
        parts.append(f"{c0.real:.4f}|0⟩")
    if abs(c1) > 1e-6:
        sign = "+" if c1.real >= 0 else "-"
        parts.append(f"{sign} {abs(c1.real):.4f}|1⟩")
        
    ket_str = " ".join(parts) if parts else "0"
    raw_array_str = f"[{c0.real:.4f}{c0.imag:+.4f}j,  {c1.real:.4f}{c1.imag:+.4f}j]"
    return ket_str, raw_array_str


def get_basis_for_state(state_name):
    """Determine theoretical measurement basis."""
    return "Z" if state_name in ["0", "1"] else "X"


def create_teleportation_circuit(state_name):
    """Build exact 3-qubit Qiskit teleportation circuit with coherent corrections."""
    qc = QuantumCircuit(3)
    
    # 1. State preparation on q0
    if state_name == "1":
        qc.x(0)
    elif state_name == "+":
        qc.h(0)
    elif state_name == "-":
        qc.x(0)
        qc.h(0)
        
    # 2. Entanglement preparation (Bell pair on q1, q2)
    qc.h(1)
    qc.cx(1, 2)
    
    # 3. Alice's Bell-state measurement operations
    qc.cx(0, 1)
    qc.h(0)
    
    # 4. Coherent corrections on Bob's qubit (q2)
    qc.cx(1, 2)
    qc.cz(0, 2)
    
    return qc


def measure_state_in_basis(statevector, basis, shots=1000):
    """Simulate measurement of statevector in selected basis using StatevectorSampler."""
    qc = QuantumCircuit(1, 1)
    qc.initialize(statevector.data, 0)
    if basis == "X":
        qc.h(0)
    qc.measure(0, 0)
    
    sampler = StatevectorSampler()
    result = sampler.run([qc], shots=shots).result()
    counts = result[0].data.c.get_counts()
    
    return {
        "0": counts.get("0", 0),
        "1": counts.get("1", 0)
    }


def calculate_expected_distribution(statevector, basis):
    """Calculate theoretical outcome probabilities."""
    if basis == "Z":
        probs = statevector.probabilities()
    else:
        qc = QuantumCircuit(1)
        qc.initialize(statevector.data, 0)
        qc.h(0)
        x_sv = Statevector.from_instruction(qc)
        probs = x_sv.probabilities()
    return {"0": probs[0], "1": probs[1]}


def calculate_chi_square_stat(observed, expected_probs, shots):
    """Compute Chi-Square statistic between observed counts and expected probabilities."""
    chi = 0.0
    for bit in ["0", "1"]:
        exp = expected_probs[bit] * shots
        obs = observed.get(bit, 0)
        if exp > 0:
            chi += ((obs - exp) ** 2) / exp
    return chi


def calculate_error_rate(counts_orig, counts_recv):
    """Compute normalized measurement error rate between original and received distributions."""
    total = sum(counts_recv.values())
    if total == 0:
        return 0.0
    diff = abs(counts_orig.get("0", 0) - counts_recv.get("0", 0)) + \
           abs(counts_orig.get("1", 0) - counts_recv.get("1", 0))
    return diff / (2 * total)


# ============================================================
# SIDEBAR CONFIGURATION (FROSTED GLASS)
# ============================================================

st.sidebar.markdown("## ⚛️ Security Configuration")
st.sidebar.caption("Configure quantum signature state and attack scenario.")

digital_message = st.sidebar.text_input(
    "Digital Message",
    value="SIH Quantum Digital Signature"
)

state_option = st.sidebar.selectbox(
    "Quantum Signature State",
    ["0", "1", "+", "-"],
    format_func=lambda x: f"|{x}⟩"
)

attack_option = st.sidebar.selectbox(
    "Attack Simulation",
    ["NONE", "FORGERY", "IMPERSONATION", "REPLAY", "CHANNEL"],
    format_func=lambda x: {
        "NONE": "Genuine / No Attack",
        "FORGERY": "Forgery Attack",
        "IMPERSONATION": "Impersonation Attack",
        "REPLAY": "Replay Attack",
        "CHANNEL": "Channel Manipulation"
    }.get(x, x)
)

# Conditional Sidebar Parameters
channel_gate = "Z"
if attack_option == "CHANNEL":
    channel_gate = st.sidebar.radio(
        "Channel Manipulation Gate",
        ["Z", "X"],
        format_func=lambda x: f"Pauli-{x} ({'Phase-Flip' if x=='Z' else 'Bit-Flip'})"
    )

expected_sender = "Alice"
received_sender = "Attacker"
if attack_option == "IMPERSONATION":
    expected_sender = st.sidebar.text_input("Expected Sender", value="Alice")
    received_sender = st.sidebar.text_input("Received Sender", value="Attacker")

session_nonce = "SESSION-2026-001"
if attack_option == "REPLAY":
    session_nonce = st.sidebar.text_input("Session ID / Nonce", value="SESSION-2026-001")

shots_val = st.sidebar.slider(
    "Measurement Shots",
    min_value=100,
    max_value=2000,
    value=1000,
    step=100
)

st.sidebar.divider()

run_verification = st.sidebar.button(
    "🚀 Run Security Verification",
    use_container_width=True,
    type="primary"
)

if st.sidebar.button("🔄 Reset Replay History", use_container_width=True, type="secondary"):
    st.session_state.used_signatures = set()
    st.sidebar.success("Replay signature history cleared!")


# ============================================================
# HERO HEADER BANNER (FROSTED GLASS CARD)
# ============================================================

st.markdown("""
<div class="glass-hero">
    <div class="hero-kicker">SIH 2026 • Quantum Cybersecurity Research Prototype</div>
    <div class="hero-title">Quantum Digital Signature Security</div>
    <div class="hero-subtitle">
        Quantum-Inspired Cyber Threat Detection for Digital Signature Security
    </div>
    <div>
        <span class="glass-badge-purple">QDS-Inspired</span>
        <span class="glass-badge-blue">Qiskit 2.x</span>
        <span class="glass-badge-cyan">3-Qubit Teleportation</span>
        <span class="glass-badge-amber">Chi-Square Detection</span>
        <span class="glass-badge-red">4-Attack Evaluator</span>
    </div>
</div>
""", unsafe_allow_html=True)


def section_title(number, title, subtitle="", color_class=""):
    num_html = f'<span class="sec-num {color_class}">{number}</span>' if number else ''
    st.markdown(f'<div class="section-header">{num_html} {title}</div>', unsafe_allow_html=True)
    if subtitle:
        st.markdown(f'<div class="section-subheader">{subtitle}</div>', unsafe_allow_html=True)


# ============================================================
# DEFAULT OVERVIEW LANDING VIEW (WHEN NOT RUN)
# ============================================================

if not run_verification:
    section_title("", "🔍 Verification Console", "Select parameters in the sidebar and click 'Run Security Verification'.")
    
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown("""
        <div class="glass-card glass-card-accent-purple">
            <h3>📜 Signature Generation</h3>
            <p>Maps digital messages to pure quantum superposition state vector representations.</p>
        </div>
        """, unsafe_allow_html=True)
    with c2:
        st.markdown("""
        <div class="glass-card glass-card-accent-cyan">
            <h3>🔗 Quantum Teleportation</h3>
            <p>3-qubit Bell pair entanglement transmission channel with coherent corrections.</p>
        </div>
        """, unsafe_allow_html=True)
    with c3:
        st.markdown("""
        <div class="glass-card glass-card-accent-green">
            <h3>🛡️ Threat Detection</h3>
            <p>Evaluates Forgery, Impersonation, Replay, and Channel Manipulation attacks.</p>
        </div>
        """, unsafe_allow_html=True)
    with c4:
        st.markdown("""
        <div class="glass-card glass-card-accent-amber">
            <h3>📊 Chi-Square Engine</h3>
            <p>Statistical hypothesis testing comparing observed vs expected shot distributions.</p>
        </div>
        """, unsafe_allow_html=True)

    section_title("", "⚛️ Supported Quantum States & Basis Selection")
    s1, s2, s3, s4 = st.columns(4)
    for col, st_name, b_name, desc in [
        (s1, "0", "Z", "Computational |0⟩ State"),
        (s2, "1", "Z", "Computational |1⟩ State"),
        (s3, "+", "X", "Superposition |+⟩ = (|0⟩+|1⟩)/√2"),
        (s4, "-", "X", "Superposition |-⟩ = (|0⟩-|1⟩)/√2")
    ]:
        with col:
            st.markdown(f"""
            <div class="glass-card glass-card-accent-purple" style="text-align:center;">
                <h2 style="color:var(--purple-light);margin:0;">|{st_name}⟩</h2>
                <p><b>Basis:</b> {b_name}-Basis</p>
                <p><small>{desc}</small></p>
            </div>
            """, unsafe_allow_html=True)

    # Controlled evaluation launcher on homepage
    st.markdown("---")
    section_title("", "📋 Controlled Prototype Evaluation", "Run automated benchmark evaluation across all test scenarios.")
    if st.button("▶️ Run Controlled Benchmark Evaluation", type="secondary"):
        benchmark_data = attack_simulator.run_controlled_evaluation(shots=shots_val)
        m = benchmark_data["metrics"]
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Detection Rate / TPR", f"{m['TPR']:.1f}%", help="True Positive Rate = TP / (TP + FN)")
        with col2:
            st.metric("False Negative Rate / FNR", f"{m['FNR']:.1f}%", help="Miss Rate = FN / (TP + FN)")
        with col3:
            st.metric("False Positive Rate / FPR", f"{m['FPR']:.1f}%", help="False Alarm Rate = FP / (FP + TN)")
        with col4:
            st.metric("Specificity / TNR", f"{m['TNR']:.1f}%", help="Specificity = TN / (TN + FP)")

        st.write("#### Benchmark Results Table (Controlled Prototype Evaluation)")
        st.dataframe(benchmark_data["results"], use_container_width=True)

    st.markdown("""
    <div class="disclaimer-box">
        <b>Notice:</b> This system is an <b>Educational / Research Prototype</b> for SIH 2026.
        Detection results depend on the selected quantum state, measurement basis, attack model, and statistical threshold.
    </div>
    """, unsafe_allow_html=True)


# ============================================================
# LIVE SECURITY VERIFICATION EXECUTION
# ============================================================

else:
    # 1. State creation & Qiskit Statevector
    original_sv = get_quantum_statevector(state_option)
    basis = get_basis_for_state(state_option)
    ket_text, raw_array_text = format_statevector_str(original_sv)

    # Attack simulation execution
    attack_res = {}
    received_sv = original_sv
    identity_threat = False
    replay_threat = False
    forgery_threat = False
    channel_threat = False

    if attack_option == "NONE":
        attack_res = {"attack": "Genuine / No Attack", "received_state": state_option, "detected": False}
        received_sv = original_sv

    elif attack_option == "FORGERY":
        attack_res = attack_simulator.simulate_forgery_attack(state_option)
        received_sv = get_quantum_statevector(attack_res["received_state"])
        forgery_threat = attack_res["detected"]

    elif attack_option == "IMPERSONATION":
        attack_res = attack_simulator.simulate_impersonation_attack(expected_sender, received_sender)
        identity_threat = attack_res["detected"]
        received_sv = original_sv

    elif attack_option == "REPLAY":
        sig_id = f"{digital_message}:{session_nonce}:{state_option}"
        attack_res = attack_simulator.simulate_replay_attack(
            digital_message, sig_id, st.session_state.used_signatures
        )
        replay_threat = attack_res["detected"]
        received_sv = original_sv

    elif attack_option == "CHANNEL":
        attack_res = attack_simulator.simulate_channel_manipulation(state_option, channel_gate, basis)
        received_sv = get_quantum_statevector(attack_res["received_state"])
        channel_threat = attack_res["detected"]

    # Measurements & Statistical Analysis
    orig_counts = measure_state_in_basis(original_sv, basis, shots_val)
    recv_counts = measure_state_in_basis(received_sv, basis, shots_val)
    expected_probs = calculate_expected_distribution(original_sv, basis)
    chi_val = calculate_chi_square_stat(recv_counts, expected_probs, shots_val)
    err_rate = calculate_error_rate(orig_counts, recv_counts)

    threshold = 10.0
    stat_threat = (chi_val > threshold)

    threat_detected = (
        stat_threat or identity_threat or replay_threat or forgery_threat or channel_threat
    )

    # Determine status labels
    is_invisible = attack_res.get("invisible", False)

    if is_invisible:
        card_class = "result-card-invisible"
        card_title = "⚠️ ATTACK NOT DETECTED UNDER SELECTED BASIS"
        card_desc = attack_res.get("invisibility_reason", "State remains invariant under selected basis.")
        status_label = "ATTACK NOT DETECTED (INVISIBLE IN BASIS)"
    elif threat_detected:
        card_class = "result-card-threat"
        card_title = f"🚨 THREAT DETECTED — {attack_res.get('attack', attack_option).upper()}"
        card_desc = f"Security verification anomaly detected. Signature Status: REJECTED."
        status_label = "THREAT DETECTED"
    else:
        card_class = "result-card-safe"
        card_title = "● SECURITY VERIFIED — NORMAL"
        card_desc = "Received quantum state and session parameters match expected security baseline."
        status_label = "VALID"

    # --------------------------------------------------------
    # SECURITY RESULT CARD (GLASS PANEL)
    # --------------------------------------------------------
    section_title("", "🔍 Security Verification Result")
    st.markdown(f"""
    <div class="{card_class}">
        <div class="result-title">{card_title}</div>
        <div class="result-subtitle">{card_desc}</div>
    </div>
    """, unsafe_allow_html=True)

    m1, m2, m3, m4, m5, m6 = st.columns(6)
    with m1:
        st.metric("Attack Scenario", attack_res.get("attack", attack_option))
    with m2:
        st.metric("Detection Verdict", "THREAT DETECTED" if threat_detected else ("INVISIBLE" if is_invisible else "NORMAL"))
    with m3:
        st.metric("Signature Status", status_label)
    with m4:
        st.metric("Verification Basis", f"{basis}-Basis")
    with m5:
        st.metric("Original State", f"|{state_option}⟩")
    with m6:
        st.metric("Received State", f"|{attack_res.get('received_state', state_option)}⟩")

    st.markdown("---")

    # --------------------------------------------------------
    # 1. DIGITAL SIGNATURE GENERATION
    # --------------------------------------------------------
    section_title("1", "Digital Signature Generation", "Quantum state signature generation and exact statevector.")
    
    st.markdown("""
    <div class="pipeline-flow">
        <div class="pipeline-step">1. Digital Message<br><b>{}</b></div>
        <div class="pipeline-arrow">›</div>
        <div class="pipeline-step">2. Quantum State<br><b>|{}⟩</b></div>
        <div class="pipeline-arrow">›</div>
        <div class="pipeline-step">3. Quantum Statevector<br><b>{}</b></div>
        <div class="pipeline-arrow">›</div>
        <div class="pipeline-step">4. Status<br><b>Signature Generated</b></div>
    </div>
    """.format(digital_message, state_option, ket_text), unsafe_allow_html=True)

    c1, c2 = st.columns(2)
    with c1:
        st.markdown("""
        <div class="glass-card glass-card-accent-purple">
            <h4>⚛️ Qiskit Quantum Statevector Data</h4>
            <p><b>State Notation:</b> {}</p>
            <div class="statevector-box">Statevector = {}</div>
        </div>
        """.format(ket_text, raw_array_text), unsafe_allow_html=True)
    with c2:
        st.markdown("""
        <div class="glass-card glass-card-accent-purple">
            <h4>📜 Signed Parameters</h4>
            <p><b>Digital Message:</b> {}</p>
            <p><b>Verification Basis:</b> {}-Basis</p>
            <p><b>Signature Type:</b> Quantum State Vector (Qiskit 2.x)</p>
        </div>
        """.format(digital_message, basis), unsafe_allow_html=True)

    st.markdown("---")

    # --------------------------------------------------------
    # 2. QUANTUM TELEPORTATION LAYER
    # --------------------------------------------------------
    section_title("2", "Quantum Teleportation Layer", "3-qubit entanglement channel transmission.")

    st.markdown("""
    <div class="pipeline-flow">
        <div class="pipeline-step">Unknown State<br>(q0)</div>
        <div class="pipeline-arrow">›</div>
        <div class="pipeline-step">Bell Pair Prep<br>(q1-q2)</div>
        <div class="pipeline-arrow">›</div>
        <div class="pipeline-step">Alice Operations<br>(CX, H)</div>
        <div class="pipeline-arrow">›</div>
        <div class="pipeline-step">Coherent Corrections<br>(CX, CZ)</div>
        <div class="pipeline-arrow">›</div>
        <div class="pipeline-step">Bob's Qubit<br>(q2)</div>
    </div>
    """, unsafe_allow_html=True)

    teleport_qc = create_teleportation_circuit(state_option)
    with st.expander("🔌 View Qiskit Teleportation Quantum Circuit", expanded=True):
        st.code(str(teleport_qc), language="text")

    st.markdown("---")

    # --------------------------------------------------------
    # 3. ATTACK SIMULATION DETAILS
    # --------------------------------------------------------
    sec_color = "sec-num-red" if threat_detected else ("sec-num-amber" if is_invisible else "sec-num-green")
    section_title("3", "Attack Simulation Details", "Specific parameters and verification results for the selected scenario.", sec_color)

    if attack_option == "FORGERY":
        c1, c2, c3 = st.columns(3)
        with c1:
            st.markdown(f"**Original State:** `|{state_option}⟩`")
            st.markdown(f"**Received State:** `|{attack_res.get('received_state')}⟩`")
        with c2:
            st.markdown(f"**Signature Modified:** `{'YES' if attack_res.get('signature_modified') else 'NO'}`")
            st.markdown(f"**Threat Detected:** `{'YES' if forgery_threat else 'NO'}`")
        with c3:
            if forgery_threat:
                st.error("SIGNATURE STATUS: FORGED")
            else:
                st.success("SIGNATURE STATUS: VALID")

    elif attack_option == "IMPERSONATION":
        c1, c2, c3 = st.columns(3)
        with c1:
            st.markdown(f"**Expected Sender:** `{attack_res.get('expected_sender')}`")
            st.markdown(f"**Received Sender:** `{attack_res.get('received_sender')}`")
        with c2:
            st.markdown(f"**Identity Verification:** `{'PASSED' if attack_res.get('identity_verified') else 'FAILED'}`")
            st.markdown(f"**Threat Status:** `{'THREAT DETECTED' if identity_threat else 'NORMAL'}`")
        with c3:
            if identity_threat:
                st.error("SIGNATURE REJECTED (SENDER MISMATCH)")
            else:
                st.success("SIGNATURE VALID")

    elif attack_option == "REPLAY":
        c1, c2, c3, c4 = st.columns(4)
        with c1:
            st.markdown(f"**Message:** `{digital_message}`")
            st.markdown(f"**Session ID:** `{session_nonce}`")
        with c2:
            st.markdown(f"**First Use:** `{'YES' if attack_res.get('first_use') else 'NO'}`")
            st.markdown(f"**Previously Seen:** `{'YES' if attack_res.get('previously_seen') else 'NO'}`")
        with c3:
            st.markdown(f"**Replay Hash:** `{attack_res.get('replay_hash')[:16]}...`")
        with c4:
            if replay_threat:
                st.error("REPLAY DETECTED — REJECTED")
            else:
                st.success("VALID (FIRST USE)")

    elif attack_option == "CHANNEL":
        c1, c2, c3 = st.columns(3)
        with c1:
            st.markdown(f"**Original State:** `|{state_option}⟩`")
            st.markdown(f"**Manipulated State:** `|{attack_res.get('received_state')}⟩`")
        with c2:
            st.markdown(f"**Pauli Operation:** `Pauli-{channel_gate}`")
            st.markdown(f"**Measurement Basis:** `{basis}-Basis`")
        with c3:
            if is_invisible:
                st.warning("ATTACK NOT DETECTED (INVISIBLE IN BASIS)")
            elif channel_threat:
                st.error("CHANNEL MANIPULATION DETECTED")
            else:
                st.success("NORMAL")

    elif attack_option == "NONE":
        st.info("Genuine signature transmission. No malicious modification detected.")

    st.markdown("---")

    # --------------------------------------------------------
    # 4. MEASUREMENT ANALYSIS
    # --------------------------------------------------------
    section_title("4", "Quantum Measurement Analysis", "Observed Qiskit measurement distributions and shot counts.")

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("#### Original Signature Counts")
        st.json(orig_counts)
        st.bar_chart(orig_counts)

    with col2:
        st.markdown("#### Received Signature Counts")
        st.json(recv_counts)
        st.bar_chart(recv_counts)

    st.markdown("---")

    # --------------------------------------------------------
    # 5. STATISTICAL THREAT DETECTION
    # --------------------------------------------------------
    section_title("5", "Statistical Threat Detection", "Chi-Square statistic hypothesis test.", "sec-num-amber")

    m1, m2, m3, m4 = st.columns(4)
    with m1:
        st.metric("Total Shots", shots_val)
    with m2:
        st.metric("Error Rate", f"{err_rate * 100:.2f}%")
    with m3:
        st.metric("Chi-Square Statistic", f"{chi_val:.2f}")
    with m4:
        st.metric("Chi-Square Threshold", f"{threshold:.1f}")

    if stat_threat:
        st.error(f"Statistical Anomaly Detected! Chi-Square ({chi_val:.2f}) > Threshold ({threshold:.1f}).")
    else:
        st.success(f"Statistical Distribution Normal. Chi-Square ({chi_val:.2f}) ≤ Threshold ({threshold:.1f}).")

    st.markdown("---")

    # --------------------------------------------------------
    # 6. ATTACK ANALYSIS MATRIX
    # --------------------------------------------------------
    section_title("6", "Attack Analysis Matrix", "Theoretical mechanism and empirical detection method summary.")

    st.markdown("""
    | Attack Type | Mechanism | Detection Method | Result in Selected Test |
    | :--- | :--- | :--- | :--- |
    | **Forgery** | State replacement ($|0\\rangle \\leftrightarrow |1\\rangle$, $|+\\rangle \\leftrightarrow |-\\rangle$) | Statevector comparison / Chi-Square | {} |
    | **Impersonation** | Unauthorized sender identity | Session identity validation | {} |
    | **Replay** | RETRANSMISSION of recorded signature | SHA-256 session history lookup | {} |
    | **Channel Manipulation** | Quantum disturbance (Pauli-X/Z) | Chi-Square statistical measurement | {} |
    """.format(
        "FORGED" if attack_option=="FORGERY" else "VALID",
        "REJECTED" if attack_option=="IMPERSONATION" and identity_threat else "VALID",
        "REPLAY DETECTED" if attack_option=="REPLAY" and replay_threat else "VALID",
        "INVISIBLE IN BASIS" if attack_option=="CHANNEL" and is_invisible else ("DETECTED" if attack_option=="CHANNEL" and channel_threat else "NORMAL")
    ), unsafe_allow_html=True)

    explanation_txt = attack_simulator.get_attack_explanation(
        attack_option, attack_res, chi_val, threshold, threat_detected
    )
    st.markdown(f"""
    <div class="glass-card glass-card-accent-purple">
        <h4>🔬 Detailed Analysis Explanation</h4>
        <p>{explanation_txt}</p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")

    # --------------------------------------------------------
    # 7. SECURITY METRICS & CONTROLLED EVALUATION BENCHMARK
    # --------------------------------------------------------
    section_title("7", "Controlled Prototype Evaluation & Security Metrics", "", "sec-num-green")

    if st.button("▶️ Run Controlled Benchmark Evaluation", type="secondary"):
        benchmark_data = attack_simulator.run_controlled_evaluation(shots=shots_val)
        m = benchmark_data["metrics"]

        c1, c2, c3, c4 = st.columns(4)
        with c1:
            st.metric("Detection Rate / TPR", f"{m['TPR']:.1f}%")
        with c2:
            st.metric("False Negative Rate / FNR", f"{m['FNR']:.1f}%")
        with c3:
            st.metric("False Positive Rate / FPR", f"{m['FPR']:.1f}%")
        with c4:
            st.metric("Specificity / TNR", f"{m['TNR']:.1f}%")

        st.dataframe(benchmark_data["results"], use_container_width=True)

    st.markdown("""
    <div class="disclaimer-box">
        <b>Evaluation Label:</b> Controlled Prototype Evaluation.<br>
        This application is an <b>Educational / Research Prototype</b> for SIH 2026.
        Detection results depend on the selected quantum state, measurement basis, attack model, and statistical threshold.
    </div>
    """, unsafe_allow_html=True)


# ============================================================
# FOOTER
# ============================================================

st.markdown("""
<div class="footer-text">
    <b>SIH 2026</b> • Quantum-Inspired Cyber Threat Detection for Digital Signature Security
    <br>
    Built with Qiskit 2.x • Python • Streamlit
</div>
""", unsafe_allow_html=True)
