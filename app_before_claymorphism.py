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
# PAGE CONFIG & DARK CHARCOAL + WARM VIOLET RESEARCH PALETTE
# ============================================================

st.set_page_config(
    page_title="Quantum Digital Signature Security Console",
    page_icon="⚛️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Dark Charcoal + Warm Violet Scientific Research System (STRICT ZERO-BLUE POLICY)
st.markdown("""
<style>
:root {
    --bg-page: #111111;
    --bg-secondary: #181818;
    --bg-card: #1E1D1F;
    --bg-card-elevated: #242225;
    
    --border-color: #39343B;
    --border-subtle: #2C282F;
    
    --text-primary: #F4F1F5;
    --text-secondary: #B6AFBA;
    --text-muted: #817985;
    
    --accent-violet: #9B6DFF;
    --accent-purple: #C26AFF;
    --accent-magenta: #D05AA8;
    --accent-burgundy: #8F465C;
    
    --success-emerald: #4FAF7B;
    --success-bg: #18241D;
    --success-border: #233B2B;
    
    --danger-red: #C65A68;
    --danger-bg: #281A1D;
    --danger-border: #422429;
    
    --warning-amber: #C99A4A;
    --warning-bg: #262016;
    --warning-border: #423621;
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

/* Sidebar Styling - Dark Charcoal Panel */
[data-testid="stSidebar"] {
    background-color: #121212 !important;
    border-right: 1px solid var(--border-color) !important;
}

[data-testid="stSidebar"] * {
    color: var(--text-primary) !important;
}

[data-testid="stSidebar"] .stCaption {
    color: var(--text-secondary) !important;
}

/* Form Controls in Sidebar - Elevated Dark Charcoal */
[data-testid="stSidebar"] [data-testid="stTextInput"],
[data-testid="stSidebar"] [data-testid="stTextInput"] > div,
[data-testid="stSidebar"] [data-testid="stTextInput"] [data-baseweb="input"],
[data-testid="stSidebar"] [data-testid="stTextInput"] [data-baseweb="input"] > div,
[data-testid="stSidebar"] [data-testid="stTextInput"] input,
[data-testid="stSidebar"] input,
[data-testid="stSidebar"] textarea,
[data-testid="stSidebar"] [data-testid="stNumberInput"] input {
    background-color: #1E1D1F !important;
    background: #1E1D1F !important;
    color: #F4F1F5 !important;
    -webkit-text-fill-color: #F4F1F5 !important;
    border: 1px solid #39343B !important;
    border-radius: 8px !important;
    box-shadow: none !important;
    caret-color: #F4F1F5 !important;
    font-weight: 450 !important;
}

[data-testid="stSidebar"] [data-testid="stTextInput"] input::placeholder,
[data-testid="stSidebar"] input::placeholder,
[data-testid="stSidebar"] textarea::placeholder {
    color: #817985 !important;
    -webkit-text-fill-color: #817985 !important;
}

[data-testid="stSidebar"] [data-testid="stTextInput"] input:focus,
[data-testid="stSidebar"] [data-testid="stTextInput"] [data-baseweb="input"]:focus-within,
[data-testid="stSidebar"] input:focus {
    border-color: #9B6DFF !important;
    box-shadow: 0 0 0 2px rgba(155, 109, 255, 0.2) !important;
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
    background-color: #1E1D1F !important;
    background: #1E1D1F !important;
    color: #F4F1F5 !important;
    -webkit-text-fill-color: #F4F1F5 !important;
}

[data-testid="stSidebar"] [data-testid="stSelectbox"] [data-baseweb="select"] > div {
    border: 1px solid #39343B !important;
    border-radius: 8px !important;
    background-color: #1E1D1F !important;
    background: #1E1D1F !important;
}

[data-testid="stSidebar"] [data-testid="stSelectbox"] [data-baseweb="select"]:hover > div {
    border-color: #9B6DFF !important;
}

[data-testid="stSidebar"] [data-testid="stSelectbox"] [data-baseweb="select"]:focus-within > div {
    border-color: #9B6DFF !important;
    box-shadow: 0 0 0 2px rgba(155, 109, 255, 0.2) !important;
}

[data-testid="stSidebar"] [data-testid="stSelectbox"] [data-baseweb="select"] span,
[data-testid="stSidebar"] [data-testid="stSelectbox"] [data-baseweb="select"] p,
[data-testid="stSidebar"] [data-testid="stSelectbox"] [data-baseweb="select"] div[role="button"] {
    color: #F4F1F5 !important;
    -webkit-text-fill-color: #F4F1F5 !important;
}

[data-testid="stSidebar"] [data-testid="stSelectbox"] [data-baseweb="select"] svg {
    color: #B6AFBA !important;
    fill: #B6AFBA !important;
}

/* BaseWeb Opened Dropdown Popup Menu Options */
div[data-baseweb="popover"],
div[data-baseweb="popover"] > div,
div[data-baseweb="menu"],
ul[data-baseweb="menu"],
div[role="listbox"],
ul[role="listbox"] {
    background-color: #1E1D1F !important;
    background: #1E1D1F !important;
    border: 1px solid #39343B !important;
    border-radius: 8px !important;
    box-shadow: 0 6px 20px rgba(0, 0, 0, 0.5) !important;
}

div[data-baseweb="popover"] li,
div[data-baseweb="menu"] li,
ul[data-baseweb="menu"] li,
li[role="option"] {
    background-color: #1E1D1F !important;
    background: #1E1D1F !important;
    color: #F4F1F5 !important;
    -webkit-text-fill-color: #F4F1F5 !important;
}

div[data-baseweb="popover"] li *,
div[data-baseweb="menu"] li *,
ul[data-baseweb="menu"] li *,
li[role="option"] * {
    color: #F4F1F5 !important;
    -webkit-text-fill-color: #F4F1F5 !important;
}

li[role="option"]:hover,
li[role="option"]:hover * {
    background-color: #2C233D !important;
    background: #2C233D !important;
    color: #9B6DFF !important;
    -webkit-text-fill-color: #9B6DFF !important;
}

li[role="option"][aria-selected="true"],
li[role="option"][aria-selected="true"] *,
div[data-baseweb="menu"] [aria-selected="true"] {
    background-color: #392A54 !important;
    background: #392A54 !important;
    color: #9B6DFF !important;
    -webkit-text-fill-color: #9B6DFF !important;
}

/* Sidebar Buttons */
[data-testid="stSidebar"] [data-testid="stButton"] button[kind="primary"],
[data-testid="stSidebar"] button[kind="primary"] {
    background-color: #8F5CF6 !important;
    background: #8F5CF6 !important;
    border: 1px solid #8F5CF6 !important;
    border-radius: 8px !important;
    min-height: 42px !important;
    transition: background-color 0.15s ease !important;
}

[data-testid="stSidebar"] [data-testid="stButton"] button[kind="primary"] p,
[data-testid="stSidebar"] [data-testid="stButton"] button[kind="primary"] span {
    color: #FFFFFF !important;
    -webkit-text-fill-color: #FFFFFF !important;
    font-weight: 600 !important;
}

[data-testid="stSidebar"] [data-testid="stButton"] button[kind="primary"]:hover {
    background-color: #7C3AED !important;
    background: #7C3AED !important;
    border-color: #7C3AED !important;
}

[data-testid="stSidebar"] [data-testid="stButton"] button[kind="secondary"],
[data-testid="stSidebar"] [data-testid="stButton"] button:not([kind="primary"]) {
    background-color: #181818 !important;
    background: #181818 !important;
    border: 1px solid #39343B !important;
    border-radius: 8px !important;
    min-height: 38px !important;
    transition: background-color 0.15s ease !important;
}

[data-testid="stSidebar"] [data-testid="stButton"] button[kind="secondary"] p,
[data-testid="stSidebar"] [data-testid="stButton"] button[kind="secondary"] span {
    color: #B6AFBA !important;
    -webkit-text-fill-color: #B6AFBA !important;
    font-weight: 500 !important;
}

[data-testid="stSidebar"] [data-testid="stButton"] button[kind="secondary"]:hover {
    background-color: #242225 !important;
    background: #242225 !important;
    border-color: #524B57 !important;
}

/* Page Header Technical Card */
.tech-header-card {
    background: #1E1D1F;
    border: 1px solid var(--border-color);
    border-radius: 10px;
    padding: 20px 24px;
    margin-bottom: 20px;
    box-shadow: 0 2px 8px rgba(0,0,0,0.18);
}

.tech-eyebrow {
    color: var(--accent-violet);
    font-size: 11px;
    font-weight: 700;
    letter-spacing: 1px;
    text-transform: uppercase;
    margin-bottom: 6px;
}

.tech-main-title {
    color: var(--text-primary);
    font-size: 26px;
    font-weight: 700;
    margin: 0 0 4px 0;
}

.tech-sub-title {
    color: var(--text-secondary);
    font-size: 14px;
    margin-bottom: 14px;
}

.tech-labels-row {
    display: flex;
    gap: 8px;
    flex-wrap: wrap;
}

.tech-label-tag {
    background: #242225;
    border: 1px solid #39343B;
    color: #B6AFBA;
    border-radius: 6px;
    padding: 4px 12px;
    font-size: 11px;
    font-weight: 600;
}

/* Technical Section Header */
.tech-sec-title {
    display: flex;
    align-items: center;
    gap: 8px;
    color: var(--text-primary);
    font-size: 15px;
    font-weight: 700;
    letter-spacing: 0.5px;
    margin: 18px 0 4px 0;
}

.tech-sec-prefix {
    color: var(--accent-violet);
    font-weight: 800;
}

.tech-sec-subtitle {
    color: var(--text-secondary);
    font-size: 13px;
    margin-bottom: 12px;
}

/* Solid Technical Cards */
.tech-card {
    background: #1E1D1F;
    border: 1px solid var(--border-color);
    border-radius: 10px;
    padding: 16px;
    margin-bottom: 12px;
    box-shadow: 0 2px 6px rgba(0,0,0,0.15);
}

/* Security Verification Panels */
.verification-panel-valid {
    background: var(--success-bg);
    border: 1px solid var(--success-border);
    border-left: 4px solid var(--success-emerald);
    border-radius: 8px;
    padding: 16px 20px;
    margin-bottom: 16px;
    display: flex;
    justify-content: space-between;
    align-items: center;
}

.verification-panel-threat {
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

.verification-panel-invisible {
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

.ver-title-group {
    display: flex;
    align-items: center;
    gap: 10px;
}

.ver-icon {
    font-size: 20px;
}

.ver-main-title {
    font-size: 16px;
    font-weight: 700;
    margin: 0;
}

.ver-title-green { color: var(--success-emerald); }
.ver-title-red { color: #F87171; }
.ver-title-amber { color: #FBBF24; }

.ver-sub-text {
    font-size: 13px;
    color: var(--text-secondary);
    margin: 2px 0 0 0;
}

.ver-level-right {
    text-align: right;
}

.ver-level-label {
    font-size: 10px;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    color: var(--text-muted);
}

.ver-level-green { font-size: 14px; font-weight: 700; color: var(--success-emerald); }
.ver-level-red { font-size: 14px; font-weight: 700; color: var(--danger-red); }
.ver-level-amber { font-size: 14px; font-weight: 700; color: var(--warning-amber); }

/* Structured Information Grid Cards */
.info-box-tech {
    background: #1E1D1F;
    border: 1px solid var(--border-color);
    border-radius: 8px;
    padding: 10px 12px;
}

.info-box-lbl {
    font-size: 10px;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    color: var(--text-muted);
    margin-bottom: 2px;
}

.info-box-val {
    font-size: 13px;
    font-weight: 600;
    color: var(--text-primary);
    word-break: break-all;
}

.val-amber-indicator { color: var(--warning-amber); }
.val-emerald-indicator { color: var(--success-emerald); }
.val-violet-indicator { color: var(--accent-violet); }
.val-purple-indicator { color: var(--accent-purple); }
.val-magenta-indicator { color: var(--accent-magenta); }

/* Timeline Process Modules */
.timeline-row {
    display: flex;
    align-items: center;
    gap: 8px;
    margin-bottom: 14px;
    overflow-x: auto;
}

.timeline-module {
    flex: 1;
    min-width: 130px;
    background: #1E1D1F;
    border: 1px solid var(--border-color);
    border-radius: 8px;
    padding: 10px 12px;
}

.timeline-module-lbl {
    font-size: 10px;
    color: var(--text-muted);
    margin-bottom: 2px;
}

.timeline-module-val {
    font-size: 13px;
    font-weight: 600;
    color: var(--text-primary);
}

.timeline-arrow {
    color: var(--accent-violet);
    font-size: 14px;
    font-weight: bold;
}

/* Technical Terminal Box */
.terminal-box-tech {
    background: #181818;
    border: 1px solid var(--border-color);
    border-radius: 6px;
    padding: 8px 10px;
    font-family: 'JetBrains Mono', Consolas, 'SFMono-Regular', monospace;
    color: var(--accent-purple);
    font-size: 11px;
    word-break: break-all;
}

/* Right-Side Analytical Readout Cards */
.readout-grid {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 8px;
    margin-top: 8px;
}

.readout-box {
    background: #181818;
    border: 1px solid var(--border-color);
    border-radius: 6px;
    padding: 10px;
}

.readout-lbl {
    font-size: 10px;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    color: var(--text-muted);
    margin-bottom: 2px;
}

.readout-val {
    font-size: 16px;
    font-weight: 700;
    color: var(--text-primary);
}

.val-green-text { color: var(--success-emerald) !important; }
.val-red-text { color: var(--danger-red) !important; }

/* Attack Scenario Modules */
.scenario-grid-tech {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(130px, 1fr));
    gap: 8px;
}

.scenario-module {
    border-radius: 8px;
    padding: 10px 12px;
}

.sc-emerald { background: #18241D; border: 1px solid #233B2B; border-left: 3px solid #4FAF7B; }
.sc-burgundy { background: #281A1D; border: 1px solid #422429; border-left: 3px solid #C65A68; }
.sc-amber { background: #262016; border: 1px solid #423621; border-left: 3px solid #C99A4A; }
.sc-orange { background: #281F1A; border: 1px solid #443026; border-left: 3px solid #D07A38; }
.sc-violet { background: #211B2B; border: 1px solid #382A4A; border-left: 3px solid #9B6DFF; }

.sc-title {
    font-size: 12px;
    font-weight: 700;
    color: var(--text-primary);
}

.sc-sub {
    font-size: 11px;
    color: var(--text-secondary);
}

/* Notice Box */
.notice-box-tech {
    background: #181818;
    border: 1px solid var(--border-color);
    border-left: 3px solid var(--warning-amber);
    border-radius: 8px;
    padding: 12px 14px;
    color: var(--text-secondary);
    font-size: 12px;
    line-height: 1.5;
}

.footer-tech {
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
# SIDEBAR CONFIGURATION (DARK CHARCOAL PANEL)
# ============================================================

st.sidebar.markdown("### ⚛ QUANTUM SECURITY")
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
# TECHNICAL PAGE HEADER
# ============================================================

st.markdown("""
<div class="tech-header-card">
    <div class="tech-eyebrow">SIH 2026 / QUANTUM SECURITY RESEARCH</div>
    <div class="tech-main-title">Quantum Digital Signature Security</div>
    <div class="tech-sub-title">
        Quantum-Inspired Cyber Threat Detection for Digital Signature Security
    </div>
    <div class="tech-labels-row">
        <span class="tech-label-tag">QDS-Inspired</span>
        <span class="tech-label-tag">Qiskit 2.x</span>
        <span class="tech-label-tag">3-Qubit Teleportation</span>
        <span class="tech-label-tag">Chi-Square Detection</span>
        <span class="tech-label-tag">4-Attack Evaluator</span>
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
# THREE-ZONE DASHBOARD LAYOUT (MAIN LEFT ~75% | METRICS RIGHT ~25%)
# ============================================================

main_col, right_col = st.columns([3.1, 1.0])

# ------------------------------------------------------------
# MAIN VERIFICATION WORKSPACE (LEFT)
# ------------------------------------------------------------

with main_col:
    # --------------------------------------------------------
    # SECURITY VERIFICATION PANEL
    # --------------------------------------------------------
    st.markdown("""
    <div class="tech-sec-title">
        SECURITY VERIFICATION RESULT
    </div>
    """, unsafe_allow_html=True)

    if is_invisible:
        st.markdown("""
        <div class="verification-panel-invisible">
            <div class="ver-title-group">
                <div class="ver-icon">⚠️</div>
                <div>
                    <div class="ver-main-title ver-title-amber">ATTACK NOT DETECTED UNDER SELECTED BASIS</div>
                    <div class="ver-sub-text">State remains invariant under selected measurement basis.</div>
                </div>
            </div>
            <div class="ver-level-right">
                <div class="ver-level-label">Threat Level</div>
                <div class="ver-level-amber">MODERATE</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    elif threat_detected:
        st.markdown(f"""
        <div class="verification-panel-threat">
            <div class="ver-title-group">
                <div class="ver-icon">🚨</div>
                <div>
                    <div class="ver-main-title ver-title-red">THREAT DETECTED — {attack_res.get('attack', attack_option).upper()}</div>
                    <div class="ver-sub-text">Security verification anomaly detected. Signature Status: REJECTED.</div>
                </div>
            </div>
            <div class="ver-level-right">
                <div class="ver-level-label">Threat Level</div>
                <div class="ver-level-red">HIGH</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div class="verification-panel-valid">
            <div class="ver-title-group">
                <div class="ver-icon">✓</div>
                <div>
                    <div class="ver-main-title ver-title-green">SECURITY VERIFIED</div>
                    <div class="ver-sub-text">No attack detected. Signature is valid and consistent.</div>
                </div>
            </div>
            <div class="ver-level-right">
                <div class="ver-level-label">Threat Level</div>
                <div class="ver-level-green">LOW</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    # Structured Information Grid (6 Status Cards with Selective Accents)
    sc1, sc2, sc3, sc4, sc5, sc6 = st.columns(6)
    with sc1:
        st.markdown(f"""
        <div class="info-box-tech">
            <div class="info-box-lbl">Attack Scenario</div>
            <div class="info-box-val val-amber-indicator">{attack_res.get('attack', 'Genuine / No Attack')}</div>
        </div>
        """, unsafe_allow_html=True)
    with sc2:
        verdict_text = "Threat Detected" if threat_detected else ("Invisible" if is_invisible else "No Threat")
        v_class = "val-red-text" if threat_detected else "val-emerald-indicator"
        st.markdown(f"""
        <div class="info-box-tech">
            <div class="info-box-lbl">Detection Verdict</div>
            <div class="info-box-val {v_class}">{verdict_text}</div>
        </div>
        """, unsafe_allow_html=True)
    with sc3:
        status_text = "REJECTED" if threat_detected else ("ATTACK NOT DETECTED" if is_invisible else "VALID")
        st.markdown(f"""
        <div class="info-box-tech">
            <div class="info-box-lbl">Signature Status</div>
            <div class="info-box-val val-violet-indicator">{status_text}</div>
        </div>
        """, unsafe_allow_html=True)
    with sc4:
        st.markdown(f"""
        <div class="info-box-tech">
            <div class="info-box-lbl">Verification Basis</div>
            <div class="info-box-val val-purple-indicator">{basis}-Basis</div>
        </div>
        """, unsafe_allow_html=True)
    with sc5:
        st.markdown(f"""
        <div class="info-box-tech">
            <div class="info-box-lbl">Original State</div>
            <div class="info-box-val val-magenta-indicator">|{state_option}⟩</div>
        </div>
        """, unsafe_allow_html=True)
    with sc6:
        recv_st = attack_res.get('received_state', state_option)
        st.markdown(f"""
        <div class="info-box-tech">
            <div class="info-box-lbl">Received State</div>
            <div class="info-box-val val-magenta-indicator">|{recv_st}⟩</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # --------------------------------------------------------
    # SECTION 01: DIGITAL SIGNATURE GENERATION
    # --------------------------------------------------------
    st.markdown("""
    <div class="tech-sec-title">
        <span class="tech-sec-prefix">01 /</span> DIGITAL SIGNATURE GENERATION
    </div>
    <div class="tech-sec-subtitle">Quantum state preparation and signature generation using Qiskit.</div>
    """, unsafe_allow_html=True)

    st.markdown(f"""
    <div class="timeline-row">
        <div class="timeline-module">
            <div class="timeline-module-lbl">Digital Message</div>
            <div class="timeline-module-val">{digital_message}</div>
        </div>
        <div class="timeline-arrow">→</div>
        <div class="timeline-module">
            <div class="timeline-module-lbl">Quantum State</div>
            <div class="timeline-module-val">|{state_option}⟩</div>
        </div>
        <div class="timeline-arrow">→</div>
        <div class="timeline-module" style="flex:1.5;">
            <div class="timeline-module-lbl">Quantum Statevector</div>
            <div class="terminal-box-tech">|{state_option}⟩ = {raw_array_text}</div>
        </div>
        <div class="timeline-arrow">→</div>
        <div class="timeline-module">
            <div class="timeline-module-lbl">Signature Generated</div>
            <div class="timeline-module-val">Yes</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # --------------------------------------------------------
    # SECTION 02: QUANTUM TELEPORTATION
    # --------------------------------------------------------
    st.markdown("""
    <div class="tech-sec-title">
        <span class="tech-sec-prefix">02 /</span> QUANTUM TELEPORTATION
    </div>
    <div class="tech-sec-subtitle">3-qubit teleportation circuit with coherent corrections.</div>
    """, unsafe_allow_html=True)

    t_col1, t_col2 = st.columns([1.8, 1.2])
    with t_col1:
        st.markdown(f"""
        <div class="timeline-row">
            <div class="timeline-module">
                <div class="timeline-module-lbl">Unknown State</div>
                <div class="timeline-module-val">|{state_option}⟩</div>
            </div>
            <div class="timeline-arrow">→</div>
            <div class="timeline-module">
                <div class="timeline-module-lbl">Bell Pair Prep</div>
                <div class="timeline-module-val">|Φ+⟩</div>
            </div>
            <div class="timeline-arrow">→</div>
            <div class="timeline-module">
                <div class="timeline-module-lbl">Alice Operations</div>
                <div class="timeline-module-val">(C<sub>Z</sub>, H)</div>
            </div>
            <div class="timeline-arrow">→</div>
            <div class="timeline-module">
                <div class="timeline-module-lbl">Coherent Corrections</div>
                <div class="timeline-module-val">(C<sub>X</sub>, C<sub>Z</sub>)</div>
            </div>
            <div class="timeline-arrow">→</div>
            <div class="timeline-module">
                <div class="timeline-module-lbl">Bob's Qubit</div>
                <div class="timeline-module-val">|ψ⟩</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    with t_col2:
        teleport_qc = create_teleportation_circuit(state_option)
        st.markdown("""
        <div class="tech-card" style="padding: 12px;">
            <div class="info-box-lbl">QISKIT QUANTUM CIRCUIT DIAGRAM</div>
            <pre style="margin:4px 0 0 0; font-size: 11px; color: #C26AFF; font-family: 'JetBrains Mono', monospace;">{}</pre>
        </div>
        """.format(str(teleport_qc)), unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # --------------------------------------------------------
    # SECTION 03: ATTACK SIMULATION
    # --------------------------------------------------------
    st.markdown("""
    <div class="tech-sec-title">
        <span class="tech-sec-prefix">03 /</span> ATTACK SIMULATION
    </div>
    <div class="tech-sec-subtitle">Simulate different attack scenarios and analyze detection results.</div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="scenario-grid-tech">
        <div class="scenario-module sc-emerald">
            <div class="sc-title">Genuine</div>
            <div class="sc-sub">No Attack</div>
        </div>
        <div class="scenario-module sc-burgundy">
            <div class="sc-title">Forgery</div>
            <div class="sc-sub">Modify Signature</div>
        </div>
        <div class="scenario-module sc-amber">
            <div class="sc-title">Impersonation</div>
            <div class="sc-sub">Fake Sender</div>
        </div>
        <div class="scenario-module sc-orange">
            <div class="sc-title">Replay</div>
            <div class="sc-sub">Reuse Signature</div>
        </div>
        <div class="scenario-module sc-violet">
            <div class="sc-title">Channel Manipulation</div>
            <div class="sc-sub">Pauli-X / Pauli-Z</div>
        </div>
    </div>
    """, unsafe_allow_html=True)


# ------------------------------------------------------------
# RIGHT COLUMN TECHNICAL ANALYTICAL READOUTS
# ------------------------------------------------------------

with right_col:
    # --------------------------------------------------------
    # STATISTICAL ANALYSIS CARD
    # --------------------------------------------------------
    decision_str = "ALERT" if stat_threat else "NORMAL"
    decision_class = "val-red-text" if stat_threat else "val-green-text"

    st.markdown(f"""
    <div class="tech-card">
        <div class="info-box-lbl">STATISTICAL ANALYSIS</div>
        <div class="tech-sec-subtitle" style="margin-bottom:8px;">Measurement comparison and statistical tests.</div>
        <div class="readout-grid">
            <div class="readout-box">
                <div class="readout-lbl">ERROR RATE</div>
                <div class="readout-val">{err_rate * 100:.2f}%</div>
            </div>
            <div class="readout-box">
                <div class="readout-lbl">CHI-SQUARE</div>
                <div class="readout-val">{chi_val:.2f}</div>
            </div>
            <div class="readout-box">
                <div class="readout-lbl">THRESHOLD</div>
                <div class="readout-val">{threshold:.2f}</div>
            </div>
            <div class="readout-box">
                <div class="readout-lbl">DECISION</div>
                <div class="readout-val {decision_class}">{decision_str}</div>
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
    <div class="tech-card">
        <div class="info-box-lbl">SECURITY METRICS</div>
        <div class="tech-sec-subtitle" style="margin-bottom:8px;">Performance indicators (Controlled Evaluation)</div>
        <div class="readout-grid">
            <div class="readout-box">
                <div class="readout-lbl">Detection Rate / TPR</div>
                <div class="readout-val val-green-text">{m['TPR']:.2f}%</div>
            </div>
            <div class="readout-box">
                <div class="readout-lbl">False Negative Rate / FNR</div>
                <div class="readout-val" style="color: #C26AFF;">{m['FNR']:.2f}%</div>
            </div>
            <div class="readout-box">
                <div class="readout-lbl">False Positive Rate / FPR</div>
                <div class="readout-val" style="color: #C99A4A;">{m['FPR']:.2f}%</div>
            </div>
            <div class="readout-box">
                <div class="readout-lbl">Specificity / TNR</div>
                <div class="readout-val" style="color: #9B6DFF;">{m['TNR']:.2f}%</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # --------------------------------------------------------
    # PROJECT NOTICE CARD
    # --------------------------------------------------------
    st.markdown("""
    <div class="notice-box-tech">
        <div style="font-weight: 700; margin-bottom: 4px; color: #F4F1F5;">
            PROJECT NOTICE
        </div>
        This is an Educational / Research Prototype for SIH 2026.
        Detection results depend on the selected quantum state, measurement basis, attack model, and statistical threshold.
    </div>
    """, unsafe_allow_html=True)


# ============================================================
# FOOTER
# ============================================================

st.markdown("""
<div class="footer-tech">
    <b>SIH 2026</b> • Quantum-Inspired Cyber Threat Detection for Digital Signature Security
    <br>
    Built with Qiskit 2.x • Python • Streamlit
</div>
""", unsafe_allow_html=True)
