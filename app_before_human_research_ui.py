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
    --bg-gradient: radial-gradient(circle at 15% 20%, rgba(139, 92, 246, 0.15), transparent 45%),
                    radial-gradient(circle at 85% 75%, rgba(6, 182, 212, 0.10), transparent 45%),
                    radial-gradient(circle at 50% 50%, rgba(11, 16, 32, 0.95), #05070D);
                    
    --glass-bg: rgba(255, 255, 255, 0.04);
    --glass-surface: rgba(17, 21, 28, 0.65);
    --glass-border: rgba(255, 255, 255, 0.10);
    --glass-border-purple: rgba(139, 92, 246, 0.35);
    
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
    max-width: 1520px !important;
    padding-top: 1.0rem !important;
    padding-bottom: 2.0rem !important;
}

/* Sidebar Styling - Frosted Glass Panel */
[data-testid="stSidebar"] {
    background: rgba(8, 11, 20, 0.85) !important;
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
[data-testid="stSidebar"] [data-testid="stButton"] button[kind="primary"],
[data-testid="stSidebar"] button[kind="primary"] {
    background: linear-gradient(135deg, rgba(139, 92, 246, 0.90) 0%, rgba(109, 40, 217, 0.95) 100%) !important;
    backdrop-filter: blur(12px) !important;
    border: 1px solid rgba(167, 139, 250, 0.4) !important;
    box-shadow: 0 4px 20px rgba(139, 92, 246, 0.4) !important;
    border-radius: 12px !important;
    min-height: 48px !important;
    transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1) !important;
}

[data-testid="stSidebar"] [data-testid="stButton"] button[kind="primary"] p,
[data-testid="stSidebar"] [data-testid="stButton"] button[kind="primary"] span {
    color: #FFFFFF !important;
    -webkit-text-fill-color: #FFFFFF !important;
    font-weight: 800 !important;
    letter-spacing: 0.3px !important;
}

[data-testid="stSidebar"] [data-testid="stButton"] button[kind="primary"]:hover {
    background: linear-gradient(135deg, rgba(167, 139, 250, 0.95) 0%, rgba(124, 58, 237, 1) 100%) !important;
    box-shadow: 0 6px 24px rgba(139, 92, 246, 0.6) !important;
    transform: translateY(-1px) !important;
}

[data-testid="stSidebar"] [data-testid="stButton"] button[kind="secondary"],
[data-testid="stSidebar"] [data-testid="stButton"] button:not([kind="primary"]) {
    background: rgba(23, 27, 34, 0.65) !important;
    backdrop-filter: blur(12px) !important;
    border: 1px solid rgba(255, 255, 255, 0.12) !important;
    border-radius: 12px !important;
    min-height: 42px !important;
    transition: all 0.2s ease-in-out !important;
}

[data-testid="stSidebar"] [data-testid="stButton"] button[kind="secondary"] p,
[data-testid="stSidebar"] [data-testid="stButton"] button[kind="secondary"] span {
    color: #CBD5E1 !important;
    -webkit-text-fill-color: #CBD5E1 !important;
    font-weight: 600 !important;
}

/* Glass Hero Card */
.glass-hero {
    background: rgba(17, 21, 28, 0.65);
    backdrop-filter: blur(20px);
    -webkit-backdrop-filter: blur(20px);
    border: 1px solid rgba(255, 255, 255, 0.10);
    border-radius: 20px;
    padding: 24px 32px;
    margin-bottom: 20px;
    position: relative;
    box-shadow: 0 14px 40px rgba(0, 0, 0, 0.45);
    overflow: hidden;
    display: flex;
    justify-content: space-between;
    align-items: center;
}

.hero-content {
    max-width: 800px;
}

.hero-badge-top {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    background: rgba(139, 92, 246, 0.18);
    border: 1px solid rgba(139, 92, 246, 0.35);
    border-radius: 999px;
    padding: 4px 12px;
    color: #C4B5FD;
    font-size: 11px;
    font-weight: 800;
    letter-spacing: 1.5px;
    text-transform: uppercase;
    margin-bottom: 8px;
}

.hero-title {
    color: #F5F7FA;
    font-size: clamp(24px, 2.8vw, 36px);
    font-weight: 900;
    line-height: 1.15;
    margin: 0 0 6px 0;
}

.hero-subtitle {
    color: var(--text-secondary);
    font-size: 14px;
    margin-bottom: 16px;
}

.hero-badges-row {
    display: flex;
    gap: 8px;
    flex-wrap: wrap;
}

.glass-badge {
    display: inline-block;
    padding: 4px 12px;
    border-radius: 999px;
    font-size: 11px;
    font-weight: 700;
    backdrop-filter: blur(8px);
}

.badge-purple { background: rgba(139, 92, 246, 0.15); border: 1px solid rgba(139, 92, 246, 0.35); color: #C4B5FD; }
.badge-blue { background: rgba(59, 130, 246, 0.15); border: 1px solid rgba(59, 130, 246, 0.35); color: #93C5FD; }
.badge-cyan { background: rgba(6, 182, 212, 0.15); border: 1px solid rgba(6, 182, 212, 0.35); color: #67E8F9; }
.badge-amber { background: rgba(245, 158, 11, 0.15); border: 1px solid rgba(245, 158, 11, 0.35); color: #FCD34D; }
.badge-red { background: rgba(239, 68, 68, 0.15); border: 1px solid rgba(239, 68, 68, 0.35); color: #FCA5A5; }

/* Futuristic Quantum Graphic */
.hero-quantum-graphic {
    display: flex;
    align-items: center;
    justify-content: center;
    position: relative;
    padding-right: 15px;
}

/* Glass Section Container & Title */
.section-header-banner {
    display: flex;
    align-items: center;
    gap: 10px;
    color: #F5F7FA;
    font-size: 18px;
    font-weight: 800;
    margin: 18px 0 4px 0;
}

.sec-badge-num {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    width: 26px;
    height: 26px;
    border-radius: 8px;
    background: rgba(139, 92, 246, 0.2);
    border: 1px solid rgba(139, 92, 246, 0.4);
    color: #C4B5FD;
    font-size: 12px;
    font-weight: 800;
}

.section-subtext {
    color: var(--text-secondary);
    font-size: 13px;
    margin-bottom: 14px;
}

/* Glass Cards */
.glass-card {
    background: rgba(17, 21, 28, 0.60);
    backdrop-filter: blur(18px);
    -webkit-backdrop-filter: blur(18px);
    border: 1px solid rgba(255, 255, 255, 0.09);
    border-radius: 16px;
    padding: 18px;
    margin-bottom: 14px;
    box-shadow: 0 8px 30px rgba(0, 0, 0, 0.35);
}

/* Verification Result Banners */
.result-banner-safe {
    padding: 18px 22px;
    border-radius: 14px;
    background: linear-gradient(135deg, rgba(34, 197, 94, 0.12), rgba(10, 38, 26, 0.85));
    backdrop-filter: blur(18px);
    border: 1px solid rgba(34, 197, 94, 0.45);
    box-shadow: 0 8px 32px rgba(34, 197, 94, 0.15);
    margin-bottom: 16px;
    display: flex;
    justify-content: space-between;
    align-items: center;
}

.result-banner-threat {
    padding: 18px 22px;
    border-radius: 14px;
    background: linear-gradient(135deg, rgba(239, 68, 68, 0.14), rgba(48, 14, 19, 0.85));
    backdrop-filter: blur(18px);
    border: 1px solid rgba(239, 68, 68, 0.45);
    box-shadow: 0 8px 32px rgba(239, 68, 68, 0.15);
    margin-bottom: 16px;
    display: flex;
    justify-content: space-between;
    align-items: center;
}

.result-banner-invisible {
    padding: 18px 22px;
    border-radius: 14px;
    background: linear-gradient(135deg, rgba(245, 158, 11, 0.12), rgba(42, 30, 10, 0.85));
    backdrop-filter: blur(18px);
    border: 1px solid rgba(245, 158, 11, 0.45);
    box-shadow: 0 8px 32px rgba(245, 158, 11, 0.15);
    margin-bottom: 16px;
    display: flex;
    justify-content: space-between;
    align-items: center;
}

.res-title-group {
    display: flex;
    align-items: center;
    gap: 12px;
}

.res-icon-circle {
    width: 38px;
    height: 38px;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 18px;
}

.res-icon-green { background: rgba(34, 197, 94, 0.25); color: #4ADE80; }
.res-icon-red { background: rgba(239, 68, 68, 0.25); color: #F87171; }
.res-icon-amber { background: rgba(245, 158, 11, 0.25); color: #FBBF24; }

.res-main-title {
    font-size: 18px;
    font-weight: 900;
    color: #F5F7FA;
    margin: 0;
}

.res-sub-text {
    font-size: 13px;
    color: var(--text-secondary);
    margin: 2px 0 0 0;
}

.threat-level-badge {
    text-align: right;
}

.threat-level-label {
    font-size: 10px;
    text-transform: uppercase;
    letter-spacing: 0.8px;
    color: var(--text-muted);
}

.threat-level-val-green { font-size: 16px; font-weight: 900; color: #4ADE80; }
.threat-level-val-red { font-size: 16px; font-weight: 900; color: #F87171; }
.threat-level-val-amber { font-size: 16px; font-weight: 900; color: #FBBF24; }

/* Status Cards Grid */
.status-card-box {
    background: rgba(17, 21, 28, 0.60);
    backdrop-filter: blur(14px);
    border: 1px solid rgba(255, 255, 255, 0.08);
    border-radius: 12px;
    padding: 12px 14px;
    text-align: left;
}

.status-card-label {
    font-size: 10px;
    text-transform: uppercase;
    letter-spacing: 0.6px;
    color: #94A3B8;
    margin-bottom: 4px;
    display: flex;
    align-items: center;
    gap: 6px;
}

.status-card-val {
    font-size: 15px;
    font-weight: 800;
    color: #F5F7FA;
    word-break: break-all;
}

/* Horizontal Flow Cards */
.flow-container {
    display: flex;
    align-items: center;
    gap: 8px;
    margin-bottom: 16px;
    overflow-x: auto;
}

.flow-card {
    flex: 1;
    min-width: 140px;
    background: rgba(17, 21, 28, 0.65);
    backdrop-filter: blur(14px);
    border: 1px solid rgba(255, 255, 255, 0.09);
    border-radius: 12px;
    padding: 12px;
    display: flex;
    align-items: center;
    gap: 10px;
}

.flow-icon {
    font-size: 18px;
    color: #C4B5FD;
}

.flow-label {
    font-size: 11px;
    color: #94A3B8;
}

.flow-val {
    font-size: 13px;
    font-weight: 700;
    color: #F5F7FA;
}

.flow-arrow {
    color: #8B5CF6;
    font-size: 16px;
    font-weight: bold;
}

/* Code & Terminal Box */
.terminal-code-box {
    background: rgba(9, 13, 20, 0.85);
    border: 1px solid rgba(255, 255, 255, 0.1);
    border-radius: 10px;
    padding: 10px 12px;
    font-family: 'SFMono-Regular', Consolas, 'Liberation Mono', Menlo, monospace;
    color: #C4B5FD;
    font-size: 12px;
    word-break: break-all;
}

/* Metric Small Cards Grid */
.right-metric-grid {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 10px;
    margin-top: 10px;
}

.metric-small-card {
    background: rgba(17, 21, 28, 0.60);
    backdrop-filter: blur(14px);
    border: 1px solid rgba(255, 255, 255, 0.08);
    border-radius: 12px;
    padding: 12px;
}

.metric-small-label {
    font-size: 10px;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    color: #94A3B8;
    margin-bottom: 4px;
}

.metric-small-val {
    font-size: 18px;
    font-weight: 800;
    color: #F5F7FA;
}

.metric-val-green { color: #4ADE80 !important; }
.metric-val-blue { color: #60A5FA !important; }
.metric-val-amber { color: #FBBF24 !important; }
.metric-val-purple { color: #C4B5FD !important; }
.metric-val-red { color: #F87171 !important; }

/* Attack Cards Grid */
.attack-cards-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(130px, 1fr));
    gap: 10px;
}

.attack-card {
    background: rgba(17, 21, 28, 0.65);
    backdrop-filter: blur(14px);
    border: 1px solid rgba(255, 255, 255, 0.09);
    border-radius: 12px;
    padding: 12px;
    display: flex;
    align-items: center;
    gap: 10px;
}

.attack-card-green { border-left: 3px solid #22C55E; }
.attack-card-red { border-left: 3px solid #EF4444; }
.attack-card-amber { border-left: 3px solid #F59E0B; }
.attack-card-yellow { border-left: 3px solid #EAB308; }
.attack-card-purple { border-left: 3px solid #8B5CF6; }

.attack-card-title {
    font-size: 13px;
    font-weight: 800;
    color: #F5F7FA;
}

.attack-card-desc {
    font-size: 11px;
    color: #94A3B8;
}

/* Notice Box */
.notice-glass-box {
    background: rgba(6, 182, 212, 0.06);
    border: 1px solid rgba(6, 182, 212, 0.25);
    border-radius: 12px;
    padding: 14px;
    color: #A5F3FC;
    font-size: 12px;
    line-height: 1.5;
}

.footer-text {
    text-align: center;
    color: var(--text-muted);
    font-size: 12px;
    margin-top: 30px;
    padding-top: 16px;
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
# SIDEBAR CONFIGURATION (FROSTED GLASS PANEL)
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
    format_func=lambda x: f"⚛  |{x}⟩"
)

attack_option = st.sidebar.selectbox(
    "Attack Simulation",
    ["NONE", "FORGERY", "IMPERSONATION", "REPLAY", "CHANNEL"],
    format_func=lambda x: {
        "NONE": "🛡  Genuine / No Attack",
        "FORGERY": "🔑  Forgery Attack",
        "IMPERSONATION": "👤  Impersonation Attack",
        "REPLAY": "🔄  Replay Attack",
        "CHANNEL": "⚡  Channel Manipulation"
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
    "▶  Run Security Verification",
    use_container_width=True,
    type="primary"
)

if st.sidebar.button("🔄  Reset Replay History", use_container_width=True, type="secondary"):
    st.session_state.used_signatures = set()
    st.sidebar.success("Replay signature history cleared!")


# ============================================================
# HERO HEADER BANNER (REFERENCE MATCHING GLASS CARD)
# ============================================================

st.markdown("""
<div class="glass-hero">
    <div class="hero-content">
        <div class="hero-badge-top">🛡️ SIH 2026</div>
        <div class="hero-title">Quantum Digital Signature Security</div>
        <div class="hero-subtitle">
            Quantum-Inspired Cyber Threat Detection for Digital Signature Security
        </div>
        <div class="hero-badges-row">
            <span class="glass-badge badge-purple">⚛️ QDS-Inspired</span>
            <span class="glass-badge badge-blue">⚡ Qiskit 2.x</span>
            <span class="glass-badge badge-cyan">🔗 3-Qubit Teleportation</span>
            <span class="glass-badge badge-amber">📊 Chi-Square Detection</span>
            <span class="glass-badge badge-red">🛡️ 4-Attack Evaluator</span>
        </div>
    </div>
    <div class="hero-quantum-graphic">
        <svg width="120" height="120" viewBox="0 0 100 100" fill="none" xmlns="http://www.w3.org/2000/svg">
            <circle cx="50" cy="50" r="10" fill="url(#atom-grad)" filter="drop-shadow(0 0 10px #8B5CF6)"/>
            <ellipse cx="50" cy="50" rx="38" ry="14" stroke="#8B5CF6" stroke-width="1.5" stroke-dasharray="3 3" transform="rotate(30 50 50)"/>
            <ellipse cx="50" cy="50" rx="38" ry="14" stroke="#06B6D4" stroke-width="1.5" stroke-dasharray="3 3" transform="rotate(-30 50 50)"/>
            <ellipse cx="50" cy="50" rx="38" ry="14" stroke="#A78BFA" stroke-width="1.5" transform="rotate(90 50 50)"/>
            <circle cx="82" cy="32" r="3" fill="#06B6D4"/>
            <circle cx="18" cy="68" r="3" fill="#8B5CF6"/>
            <defs>
                <radialGradient id="atom-grad" cx="0" cy="0" r="1" gradientUnits="userSpaceOnUse" gradientTransform="translate(50 50) scale(12)">
                    <stop stop-color="#C4B5FD"/>
                    <stop offset="1" stop-color="#7C3AED"/>
                </radialGradient>
            </defs>
        </svg>
    </div>
</div>
""", unsafe_allow_html=True)


# Execute Calculations (Live or Default Parameters)
original_sv = get_quantum_statevector(state_option)
basis = get_basis_for_state(state_option)
ket_text, raw_array_text = format_statevector_str(original_sv)

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

is_invisible = attack_res.get("invisible", False)


# ============================================================
# TWO-COLUMN DASHBOARD LAYOUT (MAIN LEFT ~75% | METRICS RIGHT ~25%)
# ============================================================

main_col, right_col = st.columns([3.1, 1.0])

# ------------------------------------------------------------
# MAIN COLUMN CONTENT (LEFT)
# ------------------------------------------------------------

with main_col:
    # --------------------------------------------------------
    # SECURITY VERIFICATION RESULT PANEL
    # --------------------------------------------------------
    st.markdown("""
    <div class="section-header-banner">
        🛡️ Security Verification Result
    </div>
    """, unsafe_allow_html=True)

    if is_invisible:
        st.markdown("""
        <div class="result-banner-invisible">
            <div class="res-title-group">
                <div class="res-icon-circle res-icon-amber">⚠️</div>
                <div>
                    <div class="res-main-title">ATTACK NOT DETECTED UNDER SELECTED BASIS</div>
                    <div class="res-sub-text">State remains invariant under selected measurement basis.</div>
                </div>
            </div>
            <div class="threat-level-badge">
                <div class="threat-level-label">Threat Level</div>
                <div class="threat-level-val-amber">MODERATE</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    elif threat_detected:
        st.markdown(f"""
        <div class="result-banner-threat">
            <div class="res-title-group">
                <div class="res-icon-circle res-icon-red">🚨</div>
                <div>
                    <div class="res-main-title">THREAT DETECTED — {attack_res.get('attack', attack_option).upper()}</div>
                    <div class="res-sub-text">Security verification anomaly detected. Signature Status: REJECTED.</div>
                </div>
            </div>
            <div class="threat-level-badge">
                <div class="threat-level-label">Threat Level</div>
                <div class="threat-level-val-red">HIGH</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div class="result-banner-safe">
            <div class="res-title-group">
                <div class="res-icon-circle res-icon-green">✓</div>
                <div>
                    <div class="res-main-title">SECURITY VERIFIED</div>
                    <div class="res-sub-text">No attack detected. Signature is valid and consistent.</div>
                </div>
            </div>
            <div class="threat-level-badge">
                <div class="threat-level-label">Threat Level</div>
                <div class="threat-level-val-green">LOW</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    # 6 Status Cards Grid (Reference Layout)
    sc1, sc2, sc3, sc4, sc5, sc6 = st.columns(6)
    with sc1:
        st.markdown(f"""
        <div class="status-card-box">
            <div class="status-card-label">🛡 ATTACK SCENARIO</div>
            <div class="status-card-val">{attack_res.get('attack', 'Genuine / No Attack')}</div>
        </div>
        """, unsafe_allow_html=True)
    with sc2:
        verdict_text = "Threat Detected" if threat_detected else ("Invisible" if is_invisible else "No Threat")
        st.markdown(f"""
        <div class="status-card-box">
            <div class="status-card-label">📊 DETECTION VERDICT</div>
            <div class="status-card-val">{verdict_text}</div>
        </div>
        """, unsafe_allow_html=True)
    with sc3:
        status_text = "REJECTED" if threat_detected else ("ATTACK NOT DETECTED" if is_invisible else "VALID")
        st.markdown(f"""
        <div class="status-card-box">
            <div class="status-card-label">🔑 SIGNATURE STATUS</div>
            <div class="status-card-val">{status_text}</div>
        </div>
        """, unsafe_allow_html=True)
    with sc4:
        st.markdown(f"""
        <div class="status-card-box">
            <div class="status-card-label">⚡ VERIFICATION BASIS</div>
            <div class="status-card-val">{basis}-Basis</div>
        </div>
        """, unsafe_allow_html=True)
    with sc5:
        st.markdown(f"""
        <div class="status-card-box">
            <div class="status-card-label">⚛ ORIGINAL STATE</div>
            <div class="status-card-val">|{state_option}⟩</div>
        </div>
        """, unsafe_allow_html=True)
    with sc6:
        recv_st = attack_res.get('received_state', state_option)
        st.markdown(f"""
        <div class="status-card-box">
            <div class="status-card-label">⚛ RECEIVED STATE</div>
            <div class="status-card-val">|{recv_st}⟩</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # --------------------------------------------------------
    # SECTION 1: DIGITAL SIGNATURE GENERATION
    # --------------------------------------------------------
    st.markdown("""
    <div class="section-header-banner">
        <span class="sec-badge-num">1</span> Digital Signature Generation
    </div>
    <div class="section-subtext">Quantum state preparation and signature generation using Qiskit.</div>
    """, unsafe_allow_html=True)

    st.markdown(f"""
    <div class="flow-container">
        <div class="flow-card">
            <div class="flow-icon">📜</div>
            <div>
                <div class="flow-label">Digital Message</div>
                <div class="flow-val">{digital_message}</div>
            </div>
        </div>
        <div class="flow-arrow">→</div>
        <div class="flow-card">
            <div class="flow-icon">⚛️</div>
            <div>
                <div class="flow-label">Quantum State</div>
                <div class="flow-val">|{state_option}⟩</div>
            </div>
        </div>
        <div class="flow-arrow">→</div>
        <div class="flow-card" style="flex:1.5;">
            <div class="flow-icon">💻</div>
            <div>
                <div class="flow-label">Quantum Statevector</div>
                <div class="terminal-code-box">|{state_option}⟩ = {raw_array_text}</div>
            </div>
        </div>
        <div class="flow-arrow">→</div>
        <div class="flow-card">
            <div class="flow-icon">✓</div>
            <div>
                <div class="flow-label">Signature Generated</div>
                <div class="flow-val">Yes</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # --------------------------------------------------------
    # SECTION 2: QUANTUM TELEPORTATION LAYER
    # --------------------------------------------------------
    st.markdown("""
    <div class="section-header-banner">
        <span class="sec-badge-num">2</span> Quantum Teleportation Layer
    </div>
    <div class="section-subtext">3-qubit teleportation circuit with coherent corrections.</div>
    """, unsafe_allow_html=True)

    t_col1, t_col2 = st.columns([1.8, 1.2])
    with t_col1:
        st.markdown(f"""
        <div class="flow-container">
            <div class="flow-card">
                <div>
                    <div class="flow-label">Unknown State</div>
                    <div class="flow-val">|{state_option}⟩</div>
                </div>
            </div>
            <div class="flow-arrow">→</div>
            <div class="flow-card">
                <div>
                    <div class="flow-label">Bell Pair Prep</div>
                    <div class="flow-val">|Φ+⟩</div>
                </div>
            </div>
            <div class="flow-arrow">→</div>
            <div class="flow-card">
                <div>
                    <div class="flow-label">Alice Operations</div>
                    <div class="flow-val">(C<sub>Z</sub>, H)</div>
                </div>
            </div>
            <div class="flow-arrow">→</div>
            <div class="flow-card">
                <div>
                    <div class="flow-label">Coherent Corrections</div>
                    <div class="flow-val">(C<sub>X</sub>, C<sub>Z</sub>)</div>
                </div>
            </div>
            <div class="flow-arrow">→</div>
            <div class="flow-card">
                <div>
                    <div class="flow-label">Bob's Qubit</div>
                    <div class="flow-val">|ψ⟩</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    with t_col2:
        teleport_qc = create_teleportation_circuit(state_option)
        st.markdown("""
        <div class="glass-card" style="padding: 12px;">
            <div class="status-card-label">📊 QISKIT QUANTUM CIRCUIT</div>
            <pre style="margin:0; font-size: 11px; color: #C4B5FD; font-family: monospace;">{}</pre>
        </div>
        """.format(str(teleport_qc)), unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # --------------------------------------------------------
    # SECTION 3: ATTACK SIMULATION
    # --------------------------------------------------------
    st.markdown("""
    <div class="section-header-banner">
        <span class="sec-badge-num">3</span> Attack Simulation
    </div>
    <div class="section-subtext">Simulate different attack scenarios and analyze detection results.</div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="attack-cards-grid">
        <div class="attack-card attack-card-green">
            <div style="font-size: 20px;">🛡️</div>
            <div>
                <div class="attack-card-title">Genuine</div>
                <div class="attack-card-desc">No Attack</div>
            </div>
        </div>
        <div class="attack-card attack-card-red">
            <div style="font-size: 20px;">🔑</div>
            <div>
                <div class="attack-card-title">Forgery</div>
                <div class="attack-card-desc">Modify Signature</div>
            </div>
        </div>
        <div class="attack-card attack-card-amber">
            <div style="font-size: 20px;">👤</div>
            <div>
                <div class="attack-card-title">Impersonation</div>
                <div class="attack-card-desc">Fake Sender</div>
            </div>
        </div>
        <div class="attack-card attack-card-yellow">
            <div style="font-size: 20px;">🔄</div>
            <div>
                <div class="attack-card-title">Replay</div>
                <div class="attack-card-desc">Reuse Signature</div>
            </div>
        </div>
        <div class="attack-card attack-card-purple">
            <div style="font-size: 20px;">⚡</div>
            <div>
                <div class="attack-card-title">Channel Manipulation</div>
                <div class="attack-card-desc">Pauli-X / Pauli-Z</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)


# ------------------------------------------------------------
# RIGHT COLUMN CONTENT (STATISTICAL ANALYSIS & SECURITY METRICS)
# ------------------------------------------------------------

with right_col:
    # --------------------------------------------------------
    # STATISTICAL ANALYSIS CARD
    # --------------------------------------------------------
    decision_str = "ALERT" if stat_threat else "NORMAL"
    decision_class = "metric-val-red" if stat_threat else "metric-val-green"

    st.markdown(f"""
    <div class="glass-card">
        <div class="status-card-label">📊 STATISTICAL ANALYSIS</div>
        <div class="section-subtext" style="margin-bottom:8px;">Measurement comparison and statistical tests.</div>
        <div class="right-metric-grid">
            <div class="metric-small-card">
                <div class="metric-small-label">Error Rate</div>
                <div class="metric-small-val">{err_rate * 100:.2f}%</div>
            </div>
            <div class="metric-small-card">
                <div class="metric-small-label">Chi-Square</div>
                <div class="metric-small-val">{chi_val:.2f}</div>
            </div>
            <div class="metric-small-card">
                <div class="metric-small-label">Threshold</div>
                <div class="metric-small-val">{threshold:.2f}</div>
            </div>
            <div class="metric-small-card">
                <div class="metric-small-label">Decision</div>
                <div class="metric-small-val {decision_class}">{decision_str}</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # --------------------------------------------------------
    # SECURITY METRICS CARD (CONTROLLED EVALUATION)
    # --------------------------------------------------------
    benchmark_data = attack_simulator.run_controlled_evaluation(shots=shots_val)
    m = benchmark_data["metrics"]

    st.markdown(f"""
    <div class="glass-card">
        <div class="status-card-label">📈 SECURITY METRICS</div>
        <div class="section-subtext" style="margin-bottom:8px;">Performance indicators (Controlled Evaluation)</div>
        <div class="right-metric-grid">
            <div class="metric-small-card">
                <div class="metric-small-label">Detection Rate / TPR</div>
                <div class="metric-small-val metric-val-green">{m['TPR']:.2f}%</div>
            </div>
            <div class="metric-small-card">
                <div class="metric-small-label">False Negative Rate / FNR</div>
                <div class="metric-small-val metric-val-blue">{m['FNR']:.2f}%</div>
            </div>
            <div class="metric-small-card">
                <div class="metric-small-label">False Positive Rate / FPR</div>
                <div class="metric-small-val metric-val-amber">{m['FPR']:.2f}%</div>
            </div>
            <div class="metric-small-card">
                <div class="metric-small-label">Specificity / TNR</div>
                <div class="metric-small-val metric-val-purple">{m['TNR']:.2f}%</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # --------------------------------------------------------
    # PROJECT NOTICE CARD
    # --------------------------------------------------------
    st.markdown("""
    <div class="notice-glass-box">
        <div style="font-weight: 800; margin-bottom: 4px; display: flex; align-items: center; gap: 6px;">
            ℹ️ Project Notice
        </div>
        This is an Educational / Research Prototype for SIH 2026.
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
