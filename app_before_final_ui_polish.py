import streamlit as st
import numpy as np
import hashlib
import time
from qiskit import QuantumCircuit
from qiskit.quantum_info import Statevector
from qiskit.primitives import StatevectorSampler

from qds_attack_simulator import QDSAttackSimulator
from ui_theme import apply_claymorphism_theme
from quantum_background import render_quantum_background

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
# PAGE CONFIG & PREMIUM CLAYMORPHISM THEME INTEGRATION
# ============================================================

st.set_page_config(
    page_title="Quantum Digital Signature Security Console",
    page_icon="⚛️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Apply Reusable Claymorphism Theme & Animated Quantum Background
apply_claymorphism_theme()
render_quantum_background()


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
# SIDEBAR CONFIGURATION (SILVERY METALLIC / RECESSED CONTROLS)
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
# CLAYMORPHISM TOP HEADER BAR
# ============================================================

st.markdown("""
<div class="clay-header-bar">
    <div class="clay-header-left">
        <div class="quantum-icon-badge">⚛️</div>
        <div>
            <div class="clay-header-title">QUANTUM DIGITAL SIGNATURE</div>
            <div class="clay-header-subtitle">Quantum-Inspired Cyber Threat Detection</div>
        </div>
    </div>
    <div class="clay-header-right">
        <span class="status-online-pill">● SYSTEM ONLINE</span>
        <span class="clay-header-badge">QDS PROTOTYPE</span>
        <span class="clay-header-badge sih-badge">SIH 2026</span>
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
    # SECURITY VERIFICATION RESULT PANEL
    # --------------------------------------------------------
    st.markdown("""
    <div style="font-size: 15px; font-weight: 700; color: #25282D; margin: 12px 0 6px 0;">
        SECURITY VERIFICATION RESULT
    </div>
    """, unsafe_allow_html=True)

    if is_invisible:
        st.markdown("""
        <div class="clay-panel-invisible">
            <div style="display:flex; align-items:center; gap:10px;">
                <div style="font-size:20px;">⚠️</div>
                <div>
                    <div style="font-size:16px; font-weight:700; color:#B78332;">ATTACK NOT DETECTED UNDER SELECTED BASIS</div>
                    <div style="font-size:13px; color:#59616A;">State remains invariant under selected measurement basis.</div>
                </div>
            </div>
            <div style="text-align:right;">
                <div style="font-size:10px; uppercase; color:#7A828B;">Threat Level</div>
                <div style="font-size:14px; font-weight:700; color:#B78332;">MODERATE</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    elif threat_detected:
        st.markdown(f"""
        <div class="clay-panel-threat">
            <div style="display:flex; align-items:center; gap:10px;">
                <div style="font-size:20px;">🚨</div>
                <div>
                    <div style="font-size:16px; font-weight:700; color:#B84F5B;">THREAT DETECTED — {attack_res.get('attack', attack_option).upper()}</div>
                    <div style="font-size:13px; color:#59616A;">Security verification anomaly detected. Signature Status: REJECTED.</div>
                </div>
            </div>
            <div style="text-align:right;">
                <div style="font-size:10px; uppercase; color:#7A828B;">Threat Level</div>
                <div style="font-size:14px; font-weight:700; color:#B84F5B;">HIGH</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div class="clay-panel-valid">
            <div style="display:flex; align-items:center; gap:10px;">
                <div style="font-size:20px;">✓</div>
                <div>
                    <div style="font-size:16px; font-weight:700; color:#3E8F68;">SECURITY VERIFIED</div>
                    <div style="font-size:13px; color:#59616A;">No attack detected. Signature is valid and consistent.</div>
                </div>
            </div>
            <div style="text-align:right;">
                <div style="font-size:10px; uppercase; color:#7A828B;">Threat Level</div>
                <div style="font-size:14px; font-weight:700; color:#3E8F68;">LOW</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    # 6 Tactile Status Tiles Grid
    sc1, sc2, sc3, sc4, sc5, sc6 = st.columns(6)
    with sc1:
        st.markdown(f"""
        <div class="clay-tile-status">
            <div class="clay-tile-lbl">Attack Scenario</div>
            <div class="clay-tile-val" style="color:#B78332;">{attack_res.get('attack', 'Genuine / No Attack')}</div>
        </div>
        """, unsafe_allow_html=True)
    with sc2:
        verdict_text = "Threat Detected" if threat_detected else ("Invisible" if is_invisible else "No Threat")
        v_color = "#B84F5B" if threat_detected else "#3E8F68"
        st.markdown(f"""
        <div class="clay-tile-status">
            <div class="clay-tile-lbl">Detection Verdict</div>
            <div class="clay-tile-val" style="color:{v_color};">{verdict_text}</div>
        </div>
        """, unsafe_allow_html=True)
    with sc3:
        status_text = "REJECTED" if threat_detected else ("ATTACK NOT DETECTED" if is_invisible else "VALID")
        st.markdown(f"""
        <div class="clay-tile-status">
            <div class="clay-tile-lbl">Signature Status</div>
            <div class="clay-tile-val" style="color:#7656B3;">{status_text}</div>
        </div>
        """, unsafe_allow_html=True)
    with sc4:
        st.markdown(f"""
        <div class="clay-tile-status">
            <div class="clay-tile-lbl">Verification Basis</div>
            <div class="clay-tile-val" style="color:#9A82D1;">{basis}-Basis</div>
        </div>
        """, unsafe_allow_html=True)
    with sc5:
        st.markdown(f"""
        <div class="clay-tile-status">
            <div class="clay-tile-lbl">Original State</div>
            <div class="clay-tile-val" style="color:#7656B3;">|{state_option}⟩</div>
        </div>
        """, unsafe_allow_html=True)
    with sc6:
        recv_st = attack_res.get('received_state', state_option)
        st.markdown(f"""
        <div class="clay-tile-status">
            <div class="clay-tile-lbl">Received State</div>
            <div class="clay-tile-val" style="color:#7656B3;">|{recv_st}⟩</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # --------------------------------------------------------
    # SECTION 01: DIGITAL SIGNATURE GENERATION
    # --------------------------------------------------------
    st.markdown("""
    <div style="font-size: 15px; font-weight: 700; color: #25282D; margin: 12px 0 2px 0;">
        <span style="color:#7656B3;">01 /</span> DIGITAL SIGNATURE GENERATION
    </div>
    <div style="font-size: 13px; color: #59616A; margin-bottom: 12px;">Quantum state preparation and signature generation using Qiskit.</div>
    """, unsafe_allow_html=True)

    st.markdown(f"""
    <div class="clay-flow-row">
        <div class="clay-flow-box">
            <div style="font-size:10px; color:#7A828B;">Digital Message</div>
            <div style="font-size:13px; font-weight:700; color:#25282D;">{digital_message}</div>
        </div>
        <div class="clay-flow-arrow">→</div>
        <div class="clay-flow-box">
            <div style="font-size:10px; color:#7A828B;">Quantum State</div>
            <div style="font-size:13px; font-weight:700; color:#25282D;">|{state_option}⟩</div>
        </div>
        <div class="clay-flow-arrow">→</div>
        <div class="clay-flow-box" style="flex:1.5;">
            <div style="font-size:10px; color:#7A828B;">Quantum Statevector</div>
            <div class="clay-terminal-box">|{state_option}⟩ = {raw_array_text}</div>
        </div>
        <div class="clay-flow-arrow">→</div>
        <div class="clay-flow-box">
            <div style="font-size:10px; color:#7A828B;">Signature Generated</div>
            <div style="font-size:13px; font-weight:700; color:#25282D;">Yes</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # --------------------------------------------------------
    # SECTION 02: QUANTUM TELEPORTATION
    # --------------------------------------------------------
    st.markdown("""
    <div style="font-size: 15px; font-weight: 700; color: #25282D; margin: 12px 0 2px 0;">
        <span style="color:#7656B3;">02 /</span> QUANTUM TELEPORTATION
    </div>
    <div style="font-size: 13px; color: #59616A; margin-bottom: 12px;">3-qubit teleportation circuit with coherent corrections.</div>
    """, unsafe_allow_html=True)

    t_col1, t_col2 = st.columns([1.8, 1.2])
    with t_col1:
        st.markdown(f"""
        <div class="clay-flow-row">
            <div class="clay-flow-box">
                <div style="font-size:10px; color:#7A828B;">Unknown State</div>
                <div style="font-size:13px; font-weight:700; color:#25282D;">|{state_option}⟩</div>
            </div>
            <div class="clay-flow-arrow">→</div>
            <div class="clay-flow-box">
                <div style="font-size:10px; color:#7A828B;">Bell Pair Prep</div>
                <div style="font-size:13px; font-weight:700; color:#25282D;">|Φ+⟩</div>
            </div>
            <div class="clay-flow-arrow">→</div>
            <div class="clay-flow-box">
                <div style="font-size:10px; color:#7A828B;">Alice Operations</div>
                <div style="font-size:13px; font-weight:700; color:#25282D;">(C<sub>Z</sub>, H)</div>
            </div>
            <div class="clay-flow-arrow">→</div>
            <div class="clay-flow-box">
                <div style="font-size:10px; color:#7A828B;">Coherent Corrections</div>
                <div style="font-size:13px; font-weight:700; color:#25282D;">(C<sub>X</sub>, C<sub>Z</sub>)</div>
            </div>
            <div class="clay-flow-arrow">→</div>
            <div class="clay-flow-box">
                <div style="font-size:10px; color:#7A828B;">Bob's Qubit</div>
                <div style="font-size:13px; font-weight:700; color:#25282D;">|ψ⟩</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    with t_col2:
        teleport_qc = create_teleportation_circuit(state_option)
        st.markdown("""
        <div class="clay-card" style="padding: 12px;">
            <div class="clay-tile-lbl">QISKIT QUANTUM CIRCUIT DIAGRAM</div>
            <pre style="margin:4px 0 0 0; font-size: 11px; color: #553A8B; font-family: 'JetBrains Mono', monospace;">{}</pre>
        </div>
        """.format(str(teleport_qc)), unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # --------------------------------------------------------
    # SECTION 03: ATTACK SIMULATION
    # --------------------------------------------------------
    st.markdown("""
    <div style="font-size: 15px; font-weight: 700; color: #25282D; margin: 12px 0 2px 0;">
        <span style="color:#7656B3;">03 /</span> ATTACK SIMULATION
    </div>
    <div style="font-size: 13px; color: #59616A; margin-bottom: 12px;">Simulate different attack scenarios and analyze detection results.</div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="clay-scenario-grid">
        <div class="clay-scenario-tile tile-emerald">
            <div class="tile-title">Genuine</div>
            <div class="tile-sub">No Attack</div>
        </div>
        <div class="clay-scenario-tile tile-burgundy">
            <div class="tile-title">Forgery</div>
            <div class="tile-sub">Modify Signature</div>
        </div>
        <div class="clay-scenario-tile tile-amber">
            <div class="tile-title">Impersonation</div>
            <div class="tile-sub">Fake Sender</div>
        </div>
        <div class="scenario-tile tile-orange" style="border-radius:12px; padding:12px; background:linear-gradient(145deg, #F7EFE9, #EADCD3); border-left:4px solid #D07A38; box-shadow:4px 4px 10px rgba(120,125,132,0.18), -4px -4px 10px rgba(255,255,255,0.80);">
            <div class="tile-title">Replay</div>
            <div class="tile-sub">Reuse Signature</div>
        </div>
        <div class="clay-scenario-tile tile-violet">
            <div class="tile-title">Channel Manipulation</div>
            <div class="tile-sub">Pauli-X / Pauli-Z</div>
        </div>
    </div>
    """, unsafe_allow_html=True)


# ------------------------------------------------------------
# RIGHT COLUMN CLAYMOPHISM READOUTS & SECURITY METRICS
# ------------------------------------------------------------

with right_col:
    # --------------------------------------------------------
    # STATISTICAL ANALYSIS CARD
    # --------------------------------------------------------
    decision_str = "ALERT" if stat_threat else "NORMAL"
    decision_class = "val-red-text" if stat_threat else "val-emerald-text"

    st.markdown(f"""
    <div class="clay-card">
        <div class="clay-tile-lbl">STATISTICAL ANALYSIS</div>
        <div style="font-size: 12px; color: #59616A; margin-bottom: 8px;">Measurement comparison and statistical tests.</div>
        <div class="clay-readout-grid">
            <div class="clay-readout-box">
                <div class="clay-readout-lbl">ERROR RATE</div>
                <div class="clay-readout-val">{err_rate * 100:.2f}%</div>
            </div>
            <div class="clay-readout-box">
                <div class="clay-readout-lbl">CHI-SQUARE</div>
                <div class="clay-readout-val">{chi_val:.2f}</div>
            </div>
            <div class="clay-readout-box">
                <div class="clay-readout-lbl">THRESHOLD</div>
                <div class="clay-readout-val">{threshold:.2f}</div>
            </div>
            <div class="clay-readout-box">
                <div class="clay-readout-lbl">DECISION</div>
                <div class="clay-readout-val {decision_class}">{decision_str}</div>
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
    <div class="clay-card">
        <div class="clay-tile-lbl">SECURITY METRICS</div>
        <div style="font-size: 12px; color: #59616A; margin-bottom: 8px;">Performance indicators (Controlled Evaluation)</div>
        <div class="clay-readout-grid">
            <div class="clay-readout-box">
                <div class="clay-readout-lbl">Detection Rate / TPR</div>
                <div class="clay-readout-val val-emerald-text">{m['TPR']:.2f}%</div>
            </div>
            <div class="clay-readout-box">
                <div class="clay-readout-lbl">False Negative Rate / FNR</div>
                <div class="clay-readout-val" style="color:#7656B3;">{m['FNR']:.2f}%</div>
            </div>
            <div class="clay-readout-box">
                <div class="clay-readout-lbl">False Positive Rate / FPR</div>
                <div class="clay-readout-val val-amber-text">{m['FPR']:.2f}%</div>
            </div>
            <div class="clay-readout-box">
                <div class="clay-readout-lbl">Specificity / TNR</div>
                <div class="clay-readout-val val-violet-text">{m['TNR']:.2f}%</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # --------------------------------------------------------
    # RECESSED PROJECT NOTICE CARD
    # --------------------------------------------------------
    st.markdown("""
    <div class="clay-notice-box">
        <div style="font-weight: 700; margin-bottom: 4px; color: #25282D;">
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
<div class="footer-clay">
    <b>SIH 2026</b> • Quantum-Inspired Cyber Threat Detection for Digital Signature Security
    <br>
    Built with Qiskit 2.x • Python • Streamlit
</div>
""", unsafe_allow_html=True)
