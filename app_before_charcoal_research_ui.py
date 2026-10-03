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
# PAGE CONFIG & PROFESSIONAL UNIVERSITY RESEARCH SYSTEM THEME
# ============================================================

st.set_page_config(
    page_title="Quantum Digital Signature Security Console",
    page_icon="⚛️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Professional University / Research Software CSS Engine (Light Neutral Palette)
st.markdown("""
<style>
:root {
    --bg-page: #F4F5F7;
    --bg-card: #FFFFFF;
    --border-color: #E1E4E8;
    --border-subtle: #ECEFF2;
    
    --text-primary: #20242A;
    --text-secondary: #626A73;
    --text-muted: #8A929C;
    
    --accent-purple: #6D4AFF;
    --accent-purple-light: #7A6FF0;
    --accent-purple-bg: #F0EBFF;
    --accent-purple-border: #D8CBFF;
    
    --success-green: #18864B;
    --success-bg: #F0FDF4;
    --success-border: #DCFCE7;
    
    --danger-red: #C43D4B;
    --danger-bg: #FEF2F2;
    --danger-border: #FEE2E2;
    
    --warning-amber: #B7791F;
    --warning-bg: #FFFBEB;
    --warning-border: #FEF3C7;
    
    --info-blue: #2563EB;
    --info-bg: #EFF6FF;
    --info-border: #DBEAFE;
}

/* Base App Setup */
.stApp {
    background-color: var(--bg-page) !important;
    color: var(--text-primary) !important;
    font-family: -apple-system, BlinkMacSystemFont, "Inter", "Segoe UI", Roboto, sans-serif !important;
}

.block-container {
    max-width: 1440px !important;
    padding-top: 1.2rem !important;
    padding-bottom: 2.5rem !important;
}

/* Sidebar Styling - Professional White Panel */
[data-testid="stSidebar"] {
    background-color: #FFFFFF !important;
    border-right: 1px solid var(--border-color) !important;
}

[data-testid="stSidebar"] * {
    color: var(--text-primary) !important;
}

[data-testid="stSidebar"] .stCaption {
    color: var(--text-secondary) !important;
}

/* Form Controls in Sidebar - Clean Enterprise Style */
[data-testid="stSidebar"] [data-testid="stTextInput"],
[data-testid="stSidebar"] [data-testid="stTextInput"] > div,
[data-testid="stSidebar"] [data-testid="stTextInput"] [data-baseweb="input"],
[data-testid="stSidebar"] [data-testid="stTextInput"] [data-baseweb="input"] > div,
[data-testid="stSidebar"] [data-testid="stTextInput"] input,
[data-testid="stSidebar"] input,
[data-testid="stSidebar"] textarea,
[data-testid="stSidebar"] [data-testid="stNumberInput"] input {
    background-color: #FFFFFF !important;
    background: #FFFFFF !important;
    color: #20242A !important;
    -webkit-text-fill-color: #20242A !important;
    border: 1px solid #D9DDE3 !important;
    border-radius: 8px !important;
    box-shadow: none !important;
    caret-color: #20242A !important;
    font-weight: 450 !important;
}

[data-testid="stSidebar"] [data-testid="stTextInput"] input::placeholder,
[data-testid="stSidebar"] input::placeholder,
[data-testid="stSidebar"] textarea::placeholder {
    color: #8A929C !important;
    -webkit-text-fill-color: #8A929C !important;
}

[data-testid="stSidebar"] [data-testid="stTextInput"] input:focus,
[data-testid="stSidebar"] [data-testid="stTextInput"] [data-baseweb="input"]:focus-within,
[data-testid="stSidebar"] input:focus {
    border-color: #6D4AFF !important;
    box-shadow: 0 0 0 2px rgba(109, 74, 255, 0.15) !important;
    outline: none !important;
}

/* Selectbox Dropdowns in Sidebar */
[data-testid="stSidebar"] [data-testid="stSelectbox"],
[data-testid="stSidebar"] [data-testid="stSelectbox"] [data-baseweb="select"],
[data-testid="stSidebar"] [data-testid="stSelectbox"] [data-baseweb="select"] > div,
[data-testid="stSidebar"] [data-testid="stSelectbox"] [data-baseweb="select"] div,
[data-testid="stSidebar"] [data-testid="stSelectbox"] [data-baseweb="select"] [data-baseweb="value-container"],
[data-testid="stSidebar"] [data-testid="stSelectbox"] [data-baseweb="select"] [data-baseweb="single-value"],
[data-testid="stSidebar"] [data-testid="stSelectbox"] [data-baseweb="select"] input {
    background-color: #FFFFFF !important;
    background: #FFFFFF !important;
    color: #20242A !important;
    -webkit-text-fill-color: #20242A !important;
}

[data-testid="stSidebar"] [data-testid="stSelectbox"] [data-baseweb="select"] > div {
    border: 1px solid #D9DDE3 !important;
    border-radius: 8px !important;
    background-color: #FFFFFF !important;
    background: #FFFFFF !important;
}

[data-testid="stSidebar"] [data-testid="stSelectbox"] [data-baseweb="select"]:hover > div {
    border-color: #6D4AFF !important;
}

[data-testid="stSidebar"] [data-testid="stSelectbox"] [data-baseweb="select"]:focus-within > div {
    border-color: #6D4AFF !important;
    box-shadow: 0 0 0 2px rgba(109, 74, 255, 0.15) !important;
}

[data-testid="stSidebar"] [data-testid="stSelectbox"] [data-baseweb="select"] span,
[data-testid="stSidebar"] [data-testid="stSelectbox"] [data-baseweb="select"] p,
[data-testid="stSidebar"] [data-testid="stSelectbox"] [data-baseweb="select"] div[role="button"] {
    color: #20242A !important;
    -webkit-text-fill-color: #20242A !important;
}

[data-testid="stSidebar"] [data-testid="stSelectbox"] [data-baseweb="select"] svg {
    color: #626A73 !important;
    fill: #626A73 !important;
}

/* BaseWeb Opened Dropdown Popup Menu Options */
div[data-baseweb="popover"],
div[data-baseweb="popover"] > div,
div[data-baseweb="menu"],
ul[data-baseweb="menu"],
div[role="listbox"],
ul[role="listbox"] {
    background-color: #FFFFFF !important;
    background: #FFFFFF !important;
    border: 1px solid #E1E4E8 !important;
    border-radius: 8px !important;
    box-shadow: 0 4px 16px rgba(20, 25, 30, 0.08) !important;
}

div[data-baseweb="popover"] li,
div[data-baseweb="menu"] li,
ul[data-baseweb="menu"] li,
li[role="option"] {
    background-color: #FFFFFF !important;
    background: #FFFFFF !important;
    color: #20242A !important;
    -webkit-text-fill-color: #20242A !important;
}

div[data-baseweb="popover"] li *,
div[data-baseweb="menu"] li *,
ul[data-baseweb="menu"] li *,
li[role="option"] * {
    color: #20242A !important;
    -webkit-text-fill-color: #20242A !important;
}

li[role="option"]:hover,
li[role="option"]:hover * {
    background-color: #F0EBFF !important;
    background: #F0EBFF !important;
    color: #6D4AFF !important;
    -webkit-text-fill-color: #6D4AFF !important;
}

li[role="option"][aria-selected="true"],
li[role="option"][aria-selected="true"] *,
div[data-baseweb="menu"] [aria-selected="true"] {
    background-color: #E5DCFF !important;
    background: #E5DCFF !important;
    color: #6D4AFF !important;
    -webkit-text-fill-color: #6D4AFF !important;
}

/* Sidebar Buttons */
[data-testid="stSidebar"] [data-testid="stButton"] button[kind="primary"],
[data-testid="stSidebar"] button[kind="primary"] {
    background-color: #6D4AFF !important;
    background: #6D4AFF !important;
    border: 1px solid #6D4AFF !important;
    border-radius: 8px !important;
    min-height: 42px !important;
    box-shadow: 0 2px 4px rgba(109, 74, 255, 0.2) !important;
    transition: background-color 0.15s ease !important;
}

[data-testid="stSidebar"] [data-testid="stButton"] button[kind="primary"] p,
[data-testid="stSidebar"] [data-testid="stButton"] button[kind="primary"] span {
    color: #FFFFFF !important;
    -webkit-text-fill-color: #FFFFFF !important;
    font-weight: 600 !important;
}

[data-testid="stSidebar"] [data-testid="stButton"] button[kind="primary"]:hover {
    background-color: #5B3CE0 !important;
    background: #5B3CE0 !important;
    border-color: #5B3CE0 !important;
}

[data-testid="stSidebar"] [data-testid="stButton"] button[kind="secondary"],
[data-testid="stSidebar"] [data-testid="stButton"] button:not([kind="primary"]) {
    background-color: #FFFFFF !important;
    background: #FFFFFF !important;
    border: 1px solid #D9DDE3 !important;
    border-radius: 8px !important;
    min-height: 38px !important;
    transition: background-color 0.15s ease !important;
}

[data-testid="stSidebar"] [data-testid="stButton"] button[kind="secondary"] p,
[data-testid="stSidebar"] [data-testid="stButton"] button[kind="secondary"] span {
    color: #20242A !important;
    -webkit-text-fill-color: #20242A !important;
    font-weight: 500 !important;
}

[data-testid="stSidebar"] [data-testid="stButton"] button[kind="secondary"]:hover {
    background-color: #F4F5F7 !important;
    background: #F4F5F7 !important;
    border-color: #C5CBD3 !important;
}

/* Page Header Card */
.research-header-card {
    background: #FFFFFF;
    border: 1px solid var(--border-color);
    border-radius: 12px;
    padding: 20px 24px;
    margin-bottom: 20px;
    box-shadow: 0 2px 8px rgba(20, 25, 30, 0.04);
}

.header-top-tag {
    display: inline-block;
    background: var(--accent-purple-bg);
    border: 1px solid var(--accent-purple-border);
    color: var(--accent-purple);
    border-radius: 999px;
    padding: 2px 10px;
    font-size: 11px;
    font-weight: 700;
    letter-spacing: 0.5px;
    margin-bottom: 8px;
}

.header-main-title {
    color: var(--text-primary);
    font-size: 26px;
    font-weight: 700;
    margin: 0 0 4px 0;
}

.header-sub-title {
    color: var(--text-secondary);
    font-size: 14px;
    margin-bottom: 14px;
}

.header-tags-row {
    display: flex;
    gap: 6px;
    flex-wrap: wrap;
}

.research-tag {
    background: #F8FAFC;
    border: 1px solid #E2E8F0;
    color: #475569;
    border-radius: 6px;
    padding: 3px 10px;
    font-size: 11px;
    font-weight: 600;
}

/* Section Header */
.sec-title-bar {
    display: flex;
    align-items: center;
    gap: 8px;
    color: var(--text-primary);
    font-size: 16px;
    font-weight: 600;
    margin: 16px 0 4px 0;
}

.sec-num-badge {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    width: 22px;
    height: 22px;
    border-radius: 6px;
    background: var(--accent-purple-bg);
    color: var(--accent-purple);
    font-size: 11px;
    font-weight: 700;
}

.sec-subtitle {
    color: var(--text-secondary);
    font-size: 13px;
    margin-bottom: 12px;
}

/* General White Cards */
.research-card {
    background: #FFFFFF;
    border: 1px solid var(--border-color);
    border-radius: 10px;
    padding: 16px;
    margin-bottom: 12px;
    box-shadow: 0 2px 6px rgba(20, 25, 30, 0.03);
}

/* Verification Result Banners */
.result-banner-valid {
    background: var(--success-bg);
    border: 1px solid var(--success-border);
    border-left: 4px solid var(--success-green);
    border-radius: 8px;
    padding: 16px 20px;
    margin-bottom: 16px;
    display: flex;
    justify-content: space-between;
    align-items: center;
}

.result-banner-threat {
    background: var(--danger-bg);
    border: 1px solid var(--danger-border);
    border-left: 4px solid var(--danger-red);
    border-radius: 8px;
    padding: 16px 20px;
    margin-bottom: 16px;
    display: flex;
    justify-content: space-between;
    align-items: center;
}

.result-banner-invisible {
    background: var(--warning-bg);
    border: 1px solid var(--warning-border);
    border-left: 4px solid var(--warning-amber);
    border-radius: 8px;
    padding: 16px 20px;
    margin-bottom: 16px;
    display: flex;
    justify-content: space-between;
    align-items: center;
}

.banner-title-group {
    display: flex;
    align-items: center;
    gap: 10px;
}

.banner-icon {
    font-size: 20px;
}

.banner-main-text {
    font-size: 16px;
    font-weight: 700;
    margin: 0;
}

.banner-main-text-valid { color: #166534; }
.banner-main-text-threat { color: #991B1B; }
.banner-main-text-amber { color: #92400E; }

.banner-sub-text {
    font-size: 13px;
    color: #475569;
    margin: 2px 0 0 0;
}

.threat-tag-right {
    text-align: right;
}

.threat-tag-lbl {
    font-size: 10px;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    color: #64748B;
}

.threat-tag-val-green { font-size: 14px; font-weight: 700; color: var(--success-green); }
.threat-tag-val-red { font-size: 14px; font-weight: 700; color: var(--danger-red); }
.threat-tag-val-amber { font-size: 14px; font-weight: 700; color: var(--warning-amber); }

/* Status Metric Cards Grid */
.status-box-clean {
    background: #FFFFFF;
    border: 1px solid var(--border-color);
    border-radius: 8px;
    padding: 10px 12px;
}

.status-box-lbl {
    font-size: 10px;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    color: var(--text-muted);
    margin-bottom: 2px;
}

.status-box-val {
    font-size: 13px;
    font-weight: 600;
    color: var(--text-primary);
    word-break: break-all;
}

/* Horizontal Flow Cards */
.flow-row {
    display: flex;
    align-items: center;
    gap: 8px;
    margin-bottom: 14px;
    overflow-x: auto;
}

.flow-box {
    flex: 1;
    min-width: 130px;
    background: #FFFFFF;
    border: 1px solid var(--border-color);
    border-radius: 8px;
    padding: 10px 12px;
}

.flow-box-lbl {
    font-size: 10px;
    color: var(--text-muted);
    margin-bottom: 2px;
}

.flow-box-val {
    font-size: 13px;
    font-weight: 600;
    color: var(--text-primary);
}

.flow-arrow-clean {
    color: var(--accent-purple);
    font-size: 14px;
    font-weight: bold;
}

/* Code & Terminal Container */
.code-box-clean {
    background: #F8FAFC;
    border: 1px solid #E2E8F0;
    border-radius: 6px;
    padding: 8px 10px;
    font-family: 'SFMono-Regular', Consolas, 'Liberation Mono', Menlo, monospace;
    color: #334155;
    font-size: 11px;
    word-break: break-all;
}

/* Right Column Panels */
.right-metrics-grid {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 8px;
    margin-top: 8px;
}

.metric-card-clean {
    background: #F8FAFC;
    border: 1px solid #E2E8F0;
    border-radius: 6px;
    padding: 10px;
}

.metric-card-lbl {
    font-size: 10px;
    text-transform: uppercase;
    letter-spacing: 0.4px;
    color: var(--text-muted);
    margin-bottom: 2px;
}

.metric-card-val {
    font-size: 16px;
    font-weight: 700;
    color: var(--text-primary);
}

.val-green { color: var(--success-green) !important; }
.val-red { color: var(--danger-red) !important; }
.val-blue { color: var(--info-blue) !important; }
.val-purple { color: var(--accent-purple) !important; }
.val-amber { color: var(--warning-amber) !important; }

/* Scenario Cards Grid */
.scenario-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(130px, 1fr));
    gap: 8px;
}

.scenario-card {
    border-radius: 8px;
    padding: 10px 12px;
}

.scenario-card-green { background: #F0FDF4; border: 1px solid #DCFCE7; border-left: 3px solid #18864B; }
.scenario-card-red { background: #FEF2F2; border: 1px solid #FEE2E2; border-left: 3px solid #C43D4B; }
.scenario-card-amber { background: #FFFBEB; border: 1px solid #FEF3C7; border-left: 3px solid #B7791F; }
.scenario-card-orange { background: #FFF7ED; border: 1px solid #FFEDD5; border-left: 3px solid #C2410C; }
.scenario-card-purple { background: #F5F3FF; border: 1px solid #DDD6FE; border-left: 3px solid #6D4AFF; }

.scenario-title {
    font-size: 12px;
    font-weight: 700;
    color: var(--text-primary);
}

.scenario-sub {
    font-size: 11px;
    color: var(--text-secondary);
}

/* Notice Box */
.notice-box-clean {
    background: #F8FAFC;
    border: 1px solid #E2E8F0;
    border-radius: 8px;
    padding: 12px 14px;
    color: #475569;
    font-size: 12px;
    line-height: 1.5;
}

.footer-clean {
    text-align: center;
    color: var(--text-muted);
    font-size: 12px;
    margin-top: 24px;
    padding-top: 14px;
    border-top: 1px solid var(--border-color);
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
# SIDEBAR CONFIGURATION (PROFESSIONAL WHITE PANEL)
# ============================================================

st.sidebar.markdown("### ⚛ Security Configuration")
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
    "Run Security Verification",
    use_container_width=True,
    type="primary"
)

if st.sidebar.button("Reset Replay History", use_container_width=True, type="secondary"):
    st.session_state.used_signatures = set()
    st.sidebar.success("Replay signature history cleared!")


# ============================================================
# PAGE HEADER (CLEAN RESEARCH CARD)
# ============================================================

st.markdown("""
<div class="research-header-card">
    <div class="header-top-tag">SIH 2026</div>
    <div class="header-main-title">Quantum Digital Signature Security</div>
    <div class="header-sub-title">
        Quantum-Inspired Cyber Threat Detection for Digital Signature Security
    </div>
    <div class="header-tags-row">
        <span class="research-tag">QDS-Inspired</span>
        <span class="research-tag">Qiskit 2.x</span>
        <span class="research-tag">3-Qubit Teleportation</span>
        <span class="research-tag">Chi-Square Detection</span>
        <span class="research-tag">4-Attack Evaluator</span>
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
    <div class="sec-title-bar">
        Security Verification Result
    </div>
    """, unsafe_allow_html=True)

    if is_invisible:
        st.markdown("""
        <div class="result-banner-invisible">
            <div class="banner-title-group">
                <div class="banner-icon">⚠️</div>
                <div>
                    <div class="banner-main-text banner-main-text-amber">ATTACK NOT DETECTED UNDER SELECTED BASIS</div>
                    <div class="banner-sub-text">State remains invariant under selected measurement basis.</div>
                </div>
            </div>
            <div class="threat-tag-right">
                <div class="threat-tag-lbl">Threat Level</div>
                <div class="threat-tag-val-amber">MODERATE</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    elif threat_detected:
        st.markdown(f"""
        <div class="result-banner-threat">
            <div class="banner-title-group">
                <div class="banner-icon">🚨</div>
                <div>
                    <div class="banner-main-text banner-main-text-threat">THREAT DETECTED — {attack_res.get('attack', attack_option).upper()}</div>
                    <div class="banner-sub-text">Security verification anomaly detected. Signature Status: REJECTED.</div>
                </div>
            </div>
            <div class="threat-tag-right">
                <div class="threat-tag-lbl">Threat Level</div>
                <div class="threat-tag-val-red">HIGH</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div class="result-banner-valid">
            <div class="banner-title-group">
                <div class="banner-icon">✓</div>
                <div>
                    <div class="banner-main-text banner-main-text-valid">SECURITY VERIFIED</div>
                    <div class="banner-sub-text">No attack detected. Signature is valid and consistent.</div>
                </div>
            </div>
            <div class="threat-tag-right">
                <div class="threat-tag-lbl">Threat Level</div>
                <div class="threat-tag-val-green">LOW</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    # 6 Status Cards Grid
    sc1, sc2, sc3, sc4, sc5, sc6 = st.columns(6)
    with sc1:
        st.markdown(f"""
        <div class="status-box-clean">
            <div class="status-box-lbl">Attack Scenario</div>
            <div class="status-box-val">{attack_res.get('attack', 'Genuine / No Attack')}</div>
        </div>
        """, unsafe_allow_html=True)
    with sc2:
        verdict_text = "Threat Detected" if threat_detected else ("Invisible" if is_invisible else "No Threat")
        st.markdown(f"""
        <div class="status-box-clean">
            <div class="status-box-lbl">Detection Verdict</div>
            <div class="status-box-val">{verdict_text}</div>
        </div>
        """, unsafe_allow_html=True)
    with sc3:
        status_text = "REJECTED" if threat_detected else ("ATTACK NOT DETECTED" if is_invisible else "VALID")
        st.markdown(f"""
        <div class="status-box-clean">
            <div class="status-box-lbl">Signature Status</div>
            <div class="status-box-val">{status_text}</div>
        </div>
        """, unsafe_allow_html=True)
    with sc4:
        st.markdown(f"""
        <div class="status-box-clean">
            <div class="status-box-lbl">Verification Basis</div>
            <div class="status-box-val">{basis}-Basis</div>
        </div>
        """, unsafe_allow_html=True)
    with sc5:
        st.markdown(f"""
        <div class="status-box-clean">
            <div class="status-box-lbl">Original State</div>
            <div class="status-box-val">|{state_option}⟩</div>
        </div>
        """, unsafe_allow_html=True)
    with sc6:
        recv_st = attack_res.get('received_state', state_option)
        st.markdown(f"""
        <div class="status-box-clean">
            <div class="status-box-lbl">Received State</div>
            <div class="status-box-val">|{recv_st}⟩</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # --------------------------------------------------------
    # SECTION 1: DIGITAL SIGNATURE GENERATION
    # --------------------------------------------------------
    st.markdown("""
    <div class="sec-title-bar">
        <span class="sec-num-badge">01</span> Digital Signature Generation
    </div>
    <div class="sec-subtitle">Quantum state preparation and signature generation using Qiskit.</div>
    """, unsafe_allow_html=True)

    st.markdown(f"""
    <div class="flow-row">
        <div class="flow-box">
            <div class="flow-box-lbl">Digital Message</div>
            <div class="flow-box-val">{digital_message}</div>
        </div>
        <div class="flow-arrow-clean">→</div>
        <div class="flow-box">
            <div class="flow-box-lbl">Quantum State</div>
            <div class="flow-box-val">|{state_option}⟩</div>
        </div>
        <div class="flow-arrow-clean">→</div>
        <div class="flow-box" style="flex:1.5;">
            <div class="flow-box-lbl">Quantum Statevector</div>
            <div class="code-box-clean">|{state_option}⟩ = {raw_array_text}</div>
        </div>
        <div class="flow-arrow-clean">→</div>
        <div class="flow-box">
            <div class="flow-box-lbl">Signature Generated</div>
            <div class="flow-box-val">Yes</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # --------------------------------------------------------
    # SECTION 2: QUANTUM TELEPORTATION LAYER
    # --------------------------------------------------------
    st.markdown("""
    <div class="sec-title-bar">
        <span class="sec-num-badge">02</span> Quantum Teleportation Layer
    </div>
    <div class="sec-subtitle">3-qubit teleportation circuit with coherent corrections.</div>
    """, unsafe_allow_html=True)

    t_col1, t_col2 = st.columns([1.8, 1.2])
    with t_col1:
        st.markdown(f"""
        <div class="flow-row">
            <div class="flow-box">
                <div class="flow-box-lbl">Unknown State</div>
                <div class="flow-box-val">|{state_option}⟩</div>
            </div>
            <div class="flow-arrow-clean">→</div>
            <div class="flow-box">
                <div class="flow-box-lbl">Bell Pair Prep</div>
                <div class="flow-box-val">|Φ+⟩</div>
            </div>
            <div class="flow-arrow-clean">→</div>
            <div class="flow-box">
                <div class="flow-box-lbl">Alice Operations</div>
                <div class="flow-box-val">(C<sub>Z</sub>, H)</div>
            </div>
            <div class="flow-arrow-clean">→</div>
            <div class="flow-box">
                <div class="flow-box-lbl">Coherent Corrections</div>
                <div class="flow-box-val">(C<sub>X</sub>, C<sub>Z</sub>)</div>
            </div>
            <div class="flow-arrow-clean">→</div>
            <div class="flow-box">
                <div class="flow-box-lbl">Bob's Qubit</div>
                <div class="flow-box-val">|ψ⟩</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    with t_col2:
        teleport_qc = create_teleportation_circuit(state_option)
        st.markdown("""
        <div class="research-card" style="padding: 12px;">
            <div class="status-box-lbl">QISKIT QUANTUM CIRCUIT</div>
            <pre style="margin:4px 0 0 0; font-size: 11px; color: #334155; font-family: monospace;">{}</pre>
        </div>
        """.format(str(teleport_qc)), unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # --------------------------------------------------------
    # SECTION 3: ATTACK SIMULATION
    # --------------------------------------------------------
    st.markdown("""
    <div class="sec-title-bar">
        <span class="sec-num-badge">03</span> Attack Simulation
    </div>
    <div class="sec-subtitle">Simulate different attack scenarios and analyze detection results.</div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="scenario-grid">
        <div class="scenario-card scenario-card-green">
            <div class="scenario-title">Genuine</div>
            <div class="scenario-sub">No Attack</div>
        </div>
        <div class="scenario-card scenario-card-red">
            <div class="scenario-title">Forgery</div>
            <div class="scenario-sub">Modify Signature</div>
        </div>
        <div class="scenario-card scenario-card-amber">
            <div class="scenario-title">Impersonation</div>
            <div class="scenario-sub">Fake Sender</div>
        </div>
        <div class="scenario-card scenario-card-orange">
            <div class="scenario-title">Replay</div>
            <div class="scenario-sub">Reuse Signature</div>
        </div>
        <div class="scenario-card scenario-card-purple">
            <div class="scenario-title">Channel Manipulation</div>
            <div class="scenario-sub">Pauli-X / Pauli-Z</div>
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
    decision_class = "val-red" if stat_threat else "val-green"

    st.markdown(f"""
    <div class="research-card">
        <div class="status-box-lbl">STATISTICAL ANALYSIS</div>
        <div class="sec-subtitle" style="margin-bottom:8px;">Measurement comparison and statistical tests.</div>
        <div class="right-metrics-grid">
            <div class="metric-card-clean">
                <div class="metric-card-lbl">Error Rate</div>
                <div class="metric-card-val">{err_rate * 100:.2f}%</div>
            </div>
            <div class="metric-card-clean">
                <div class="metric-card-lbl">Chi-Square</div>
                <div class="metric-card-val">{chi_val:.2f}</div>
            </div>
            <div class="metric-card-clean">
                <div class="metric-card-lbl">Threshold</div>
                <div class="metric-card-val">{threshold:.2f}</div>
            </div>
            <div class="metric-card-clean">
                <div class="metric-card-lbl">Decision</div>
                <div class="metric-card-val {decision_class}">{decision_str}</div>
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
    <div class="research-card">
        <div class="status-box-lbl">SECURITY METRICS</div>
        <div class="sec-subtitle" style="margin-bottom:8px;">Performance indicators (Controlled Evaluation)</div>
        <div class="right-metrics-grid">
            <div class="metric-card-clean">
                <div class="metric-card-lbl">Detection Rate / TPR</div>
                <div class="metric-card-val val-green">{m['TPR']:.2f}%</div>
            </div>
            <div class="metric-card-clean">
                <div class="metric-card-lbl">False Negative Rate / FNR</div>
                <div class="metric-card-val val-blue">{m['FNR']:.2f}%</div>
            </div>
            <div class="metric-card-clean">
                <div class="metric-card-lbl">False Positive Rate / FPR</div>
                <div class="metric-card-val val-amber">{m['FPR']:.2f}%</div>
            </div>
            <div class="metric-card-clean">
                <div class="metric-card-lbl">Specificity / TNR</div>
                <div class="metric-card-val val-purple">{m['TNR']:.2f}%</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # --------------------------------------------------------
    # PROJECT NOTICE CARD
    # --------------------------------------------------------
    st.markdown("""
    <div class="notice-box-clean">
        <div style="font-weight: 700; margin-bottom: 4px; color: #334155;">
            Project Notice
        </div>
        This is an Educational / Research Prototype for SIH 2026.
        Detection results depend on the selected quantum state, measurement basis, attack model, and statistical threshold.
    </div>
    """, unsafe_allow_html=True)


# ============================================================
# FOOTER
# ============================================================

st.markdown("""
<div class="footer-clean">
    <b>SIH 2026</b> • Quantum-Inspired Cyber Threat Detection for Digital Signature Security
    <br>
    Built with Qiskit 2.x • Python • Streamlit
</div>
""", unsafe_allow_html=True)
