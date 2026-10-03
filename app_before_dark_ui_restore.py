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
# PAGE CONFIG & COMMAND CENTER THEME INTEGRATION
# ============================================================

st.set_page_config(
    page_title="Quantum Digital Signature Security Console",
    page_icon="⚛️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Apply Command Center CSS & Animated Quantum Canvas Background
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
    job = sampler.run([(qc, None)], shots=shots)
    result = job.result()
    pub_result = result[0]
    data_dict = pub_result.data
    bitstring_counts = data_dict['c'].get_counts()

    counts = {0: 0, 1: 0}
    for k, v in bitstring_counts.items():
        val = int(k, 2) if isinstance(k, str) else int(k)
        counts[val] = counts.get(val, 0) + v

    return counts


def calculate_expected_distribution(statevector, basis):
    """Compute exact theoretical probability distribution in measurement basis."""
    data = statevector.data
    c0 = data[0]
    c1 = data[1]

    if basis == "Z":
        p0 = float(abs(c0)**2)
        p1 = float(abs(c1)**2)
    else:  # X basis
        plus_state = (c0 + c1) / np.sqrt(2)
        minus_state = (c0 - c1) / np.sqrt(2)
        p0 = float(abs(plus_state)**2)
        p1 = float(abs(minus_state)**2)

    total = p0 + p1
    if total > 0:
        p0 /= total
        p1 /= total
    else:
        p0, p1 = 0.5, 0.5

    return {0: p0, 1: p1}


def calculate_chi_square_stat(observed_counts, expected_probs, total_shots):
    """Calculate Chi-Square test statistic against expected distribution."""
    chi_square = 0.0
    for outcome in [0, 1]:
        exp_count = expected_probs[outcome] * total_shots
        obs_count = observed_counts.get(outcome, 0)

        if exp_count > 0:
            chi_square += ((obs_count - exp_count) ** 2) / exp_count
        elif obs_count > 0:
            chi_square += obs_count * 10.0

    return chi_square


def calculate_error_rate(original_counts, received_counts):
    """Calculate empirical error rate between original and received counts."""
    total_shots = sum(original_counts.values())
    if total_shots == 0:
        return 0.0

    mismatches = abs(original_counts.get(0, 0) - received_counts.get(0, 0)) + \
                 abs(original_counts.get(1, 0) - received_counts.get(1, 0))

    return min(1.0, mismatches / (2 * total_shots))


# ============================================================
# SIDEBAR CONTROLS (SECURITY CONFIGURATION)
# ============================================================

st.sidebar.markdown("""
<div style="margin-bottom: 16px;">
    <div style="font-size: 18px; font-weight: 800; color: #FFFFFF; display: flex; align-items: center; gap: 8px;">
        <span>⚛</span> Security Configuration
    </div>
    <div style="font-size: 12px; color: #9CA3AF; margin-top: 4px;">
        Configure quantum signature state and attack scenario.
    </div>
</div>
""", unsafe_allow_html=True)

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

st.sidebar.markdown("<br>", unsafe_allow_html=True)

run_verification = st.sidebar.button(
    "▶ Run Security Verification",
    use_container_width=True,
    type="primary"
)

if st.sidebar.button("↻ Reset Replay History", use_container_width=True, type="secondary"):
    st.session_state.used_signatures = set()
    st.sidebar.success("Replay signature history cleared!")


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
# MAIN DASHBOARD LAYOUT (CENTER ~60% | METRICS RIGHT ~20%)
# ============================================================

main_col, right_col = st.columns([3.1, 1.0])

# ------------------------------------------------------------
# MAIN VERIFICATION WORKSPACE (CENTER COLUMN)
# ------------------------------------------------------------

with main_col:
    # --------------------------------------------------------
    # TOP HERO HEADER PANEL
    # --------------------------------------------------------
    st.markdown("""
    <div class="cmd-hero">
        <div style="display:flex; align-items:center; gap:16px;">
            <div style="width:48px; height:48px; border-radius:14px; background:linear-gradient(135deg, #271B4D, #1A1333); border:1px solid #A855F7; display:flex; align-items:center; justify-content:center; font-size:24px;">🛡️</div>
            <div>
                <div style="font-size:11px; font-weight:800; color:#A855F7; letter-spacing:1px;">SIH 2026</div>
                <div style="font-size:24px; font-weight:800; color:#FFFFFF; margin:2px 0;">Quantum Digital Signature Security</div>
                <div style="font-size:13px; color:#A1A5B7;">Quantum-Inspired Cyber Threat Detection for Digital Signature Security</div>
                <div style="margin-top:10px;">
                    <span class="hero-badge-tag tag-violet">QDS-Inspired</span>
                    <span class="hero-badge-tag tag-blue">Qiskit 2.x</span>
                    <span class="hero-badge-tag tag-emerald">3-Qubit Teleportation</span>
                    <span class="hero-badge-tag tag-amber">Chi-Square Detection</span>
                    <span class="hero-badge-tag tag-magenta">4-Attack Evaluator</span>
                </div>
            </div>
        </div>
        <div>
            <svg width="90" height="90" viewBox="0 0 100 100">
                <circle cx="50" cy="50" r="8" fill="#A855F7" />
                <ellipse cx="50" cy="50" rx="36" ry="14" fill="none" stroke="#8B5CF6" stroke-width="1.5" transform="rotate(0 50 50)" opacity="0.7"/>
                <ellipse cx="50" cy="50" rx="36" ry="14" fill="none" stroke="#EC4899" stroke-width="1.5" transform="rotate(60 50 50)" opacity="0.7"/>
                <ellipse cx="50" cy="50" rx="36" ry="14" fill="none" stroke="#06B6D4" stroke-width="1.5" transform="rotate(120 50 50)" opacity="0.7"/>
            </svg>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # --------------------------------------------------------
    # SECURITY VERIFICATION RESULT PANEL
    # --------------------------------------------------------
    st.markdown("""
    <div style="font-size: 15px; font-weight: 700; color: #FFFFFF; margin: 12px 0 6px 0; display:flex; align-items:center; gap:8px;">
        <span style="color:#A855F7;">🛡️</span> Security Verification Result
    </div>
    """, unsafe_allow_html=True)

    if is_invisible:
        st.markdown("""
        <div class="cmd-panel-invisible">
            <div style="display:flex; align-items:center; gap:12px;">
                <div style="width:36px; height:36px; border-radius:50%; background:rgba(245,158,11,0.2); display:flex; align-items:center; justify-content:center; font-size:18px; color:#F59E0B;">⚠️</div>
                <div>
                    <div style="font-size:16px; font-weight:700; color:#F59E0B;">ATTACK NOT DETECTED UNDER SELECTED BASIS</div>
                    <div style="font-size:13px; color:#9CA3AF;">State remains invariant under selected measurement basis.</div>
                </div>
            </div>
            <div style="text-align:right;">
                <div style="font-size:10px; uppercase; color:#9CA3AF;">Threat Level</div>
                <div style="font-size:14px; font-weight:700; color:#F59E0B;">MODERATE</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    elif threat_detected:
        st.markdown(f"""
        <div class="cmd-panel-threat">
            <div style="display:flex; align-items:center; gap:12px;">
                <div style="width:36px; height:36px; border-radius:50%; background:rgba(239,68,68,0.2); display:flex; align-items:center; justify-content:center; font-size:18px; color:#EF4444;">🚨</div>
                <div>
                    <div style="font-size:16px; font-weight:700; color:#EF4444;">THREAT DETECTED — {attack_res.get('attack', attack_option).upper()}</div>
                    <div style="font-size:13px; color:#9CA3AF;">Security verification anomaly detected. Signature Status: REJECTED.</div>
                </div>
            </div>
            <div style="text-align:right;">
                <div style="font-size:10px; uppercase; color:#9CA3AF;">Threat Level</div>
                <div style="font-size:14px; font-weight:700; color:#EF4444;">HIGH</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div class="cmd-panel-valid">
            <div style="display:flex; align-items:center; gap:12px;">
                <div style="width:36px; height:36px; border-radius:50%; background:rgba(16,185,129,0.2); display:flex; align-items:center; justify-content:center; font-size:18px; color:#10B981;">✓</div>
                <div>
                    <div style="font-size:16px; font-weight:700; color:#10B981;">SECURITY VERIFIED</div>
                    <div style="font-size:13px; color:#9CA3AF;">No attack detected. Signature is valid and consistent.</div>
                </div>
            </div>
            <div style="text-align:right;">
                <div style="font-size:10px; uppercase; color:#9CA3AF;">Threat Level</div>
                <div style="font-size:14px; font-weight:700; color:#10B981;">LOW</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    # 6 Command Status Tiles Grid
    sc1, sc2, sc3, sc4, sc5, sc6 = st.columns(6)
    with sc1:
        st.markdown(f"""
        <div class="cmd-tile-status">
            <div class="cmd-tile-lbl">🛡️ ATTACK SCENARIO</div>
            <div class="cmd-tile-val" style="color:#F59E0B;">{attack_res.get('attack', 'Genuine / No Attack')}</div>
        </div>
        """, unsafe_allow_html=True)
    with sc2:
        verdict_text = "Threat Detected" if threat_detected else ("Invisible" if is_invisible else "No Threat")
        v_color = "#EF4444" if threat_detected else "#10B981"
        st.markdown(f"""
        <div class="cmd-tile-status">
            <div class="cmd-tile-lbl">📊 DETECTION VERDICT</div>
            <div class="cmd-tile-val" style="color:{v_color};">{verdict_text}</div>
        </div>
        """, unsafe_allow_html=True)
    with sc3:
        status_text = "REJECTED" if threat_detected else ("ATTACK NOT DETECTED" if is_invisible else "VALID")
        s_color = "#EF4444" if threat_detected else "#A855F7"
        st.markdown(f"""
        <div class="cmd-tile-status">
            <div class="cmd-tile-lbl">🔒 SIGNATURE STATUS</div>
            <div class="cmd-tile-val" style="color:{s_color};">{status_text}</div>
        </div>
        """, unsafe_allow_html=True)
    with sc4:
        st.markdown(f"""
        <div class="cmd-tile-status">
            <div class="cmd-tile-lbl">🔑 VERIFICATION BASIS</div>
            <div class="cmd-tile-val" style="color:#3B82F6;">{basis}-Basis</div>
        </div>
        """, unsafe_allow_html=True)
    with sc5:
        st.markdown(f"""
        <div class="cmd-tile-status">
            <div class="cmd-tile-lbl">⚛ ORIGINAL STATE</div>
            <div class="cmd-tile-val" style="color:#A855F7;">|{state_option}⟩</div>
        </div>
        """, unsafe_allow_html=True)
    with sc6:
        recv_st = attack_res.get('received_state', state_option)
        st.markdown(f"""
        <div class="cmd-tile-status">
            <div class="cmd-tile-lbl">⚛ RECEIVED STATE</div>
            <div class="cmd-tile-val" style="color:#A855F7;">|{recv_st}⟩</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # --------------------------------------------------------
    # SECTION 01: DIGITAL SIGNATURE GENERATION
    # --------------------------------------------------------
    st.markdown("""
    <div style="font-size: 15px; font-weight: 700; color: #FFFFFF; margin: 12px 0 2px 0; display:flex; align-items:center; gap:8px;">
        <span style="width:22px; height:22px; border-radius:50%; background:#A855F7; color:#FFF; display:inline-flex; align-items:center; justify-content:center; font-size:12px;">1</span>
        Digital Signature Generation
    </div>
    <div style="font-size: 13px; color: #9CA3AF; margin-bottom: 12px;">Quantum state preparation and signature generation using Qiskit.</div>
    """, unsafe_allow_html=True)

    st.markdown(f"""
    <div class="cmd-flow-row">
        <div class="cmd-flow-box">
            <div style="font-size:10px; color:#9CA3AF;">Digital Message</div>
            <div style="font-size:13px; font-weight:700; color:#F3F4F6;">{digital_message}</div>
        </div>
        <div class="cmd-flow-arrow">→</div>
        <div class="cmd-flow-box">
            <div style="font-size:10px; color:#9CA3AF;">Quantum State</div>
            <div style="font-size:13px; font-weight:700; color:#A855F7;">|{state_option}⟩</div>
        </div>
        <div class="cmd-flow-arrow">→</div>
        <div class="cmd-flow-box" style="flex:1.5;">
            <div style="font-size:10px; color:#9CA3AF;">Quantum Statevector</div>
            <div class="cmd-terminal-box">|{state_option}⟩ = {raw_array_text}</div>
        </div>
        <div class="cmd-flow-arrow">→</div>
        <div class="cmd-flow-box">
            <div style="font-size:10px; color:#9CA3AF;">Signature Generated</div>
            <div style="font-size:13px; font-weight:700; color:#10B981;">✓ Yes</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # --------------------------------------------------------
    # SECTION 02: QUANTUM TELEPORTATION LAYER
    # --------------------------------------------------------
    st.markdown("""
    <div style="font-size: 15px; font-weight: 700; color: #FFFFFF; margin: 12px 0 2px 0; display:flex; align-items:center; gap:8px;">
        <span style="width:22px; height:22px; border-radius:50%; background:#A855F7; color:#FFF; display:inline-flex; align-items:center; justify-content:center; font-size:12px;">2</span>
        Quantum Teleportation Layer
    </div>
    <div style="font-size: 13px; color: #9CA3AF; margin-bottom: 12px;">3-qubit teleportation circuit with coherent corrections.</div>
    """, unsafe_allow_html=True)

    t_col1, t_col2 = st.columns([1.8, 1.2])
    with t_col1:
        st.markdown(f"""
        <div class="cmd-flow-row">
            <div class="cmd-flow-box">
                <div style="font-size:10px; color:#9CA3AF;">Unknown State</div>
                <div style="font-size:13px; font-weight:700; color:#F3F4F6;">|{state_option}⟩</div>
            </div>
            <div class="cmd-flow-arrow">→</div>
            <div class="cmd-flow-box">
                <div style="font-size:10px; color:#9CA3AF;">Bell Pair Prep</div>
                <div style="font-size:13px; font-weight:700; color:#3B82F6;">|Φ+⟩</div>
            </div>
            <div class="cmd-flow-arrow">→</div>
            <div class="cmd-flow-box">
                <div style="font-size:10px; color:#9CA3AF;">Alice Operations</div>
                <div style="font-size:13px; font-weight:700; color:#10B981;">(C<sub>Z</sub>, H)</div>
            </div>
            <div class="cmd-flow-arrow">→</div>
            <div class="cmd-flow-box">
                <div style="font-size:10px; color:#9CA3AF;">Coherent Corrections</div>
                <div style="font-size:13px; font-weight:700; color:#F59E0B;">(C<sub>X</sub>, C<sub>Z</sub>)</div>
            </div>
            <div class="cmd-flow-arrow">→</div>
            <div class="cmd-flow-box">
                <div style="font-size:10px; color:#9CA3AF;">Bob's Qubit</div>
                <div style="font-size:13px; font-weight:700; color:#A855F7;">|ψ⟩</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    with t_col2:
        teleport_qc = create_teleportation_circuit(state_option)
        st.markdown("""
        <div class="cmd-card" style="padding: 14px;">
            <div class="cmd-tile-lbl">⚙ QISKIT QUANTUM CIRCUIT</div>
            <pre style="margin:4px 0 0 0; font-size: 11px; color: #C4B5FD; font-family: 'JetBrains Mono', monospace; background:transparent;">{}</pre>
        </div>
        """.format(str(teleport_qc)), unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # --------------------------------------------------------
    # SECTION 03: ATTACK SIMULATION
    # --------------------------------------------------------
    st.markdown("""
    <div style="font-size: 15px; font-weight: 700; color: #FFFFFF; margin: 12px 0 2px 0; display:flex; align-items:center; gap:8px;">
        <span style="width:22px; height:22px; border-radius:50%; background:#A855F7; color:#FFF; display:inline-flex; align-items:center; justify-content:center; font-size:12px;">3</span>
        Attack Simulation
    </div>
    <div style="font-size: 13px; color: #9CA3AF; margin-bottom: 12px;">Simulate different attack scenarios and analyze detection results.</div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="cmd-scenario-grid">
        <div class="cmd-scenario-tile tile-genuine">
            <div style="font-size: 13px; font-weight: 700; color: #10B981;">🛡️ Genuine</div>
            <div style="font-size: 11px; color: #9CA3AF;">No Attack</div>
        </div>
        <div class="cmd-scenario-tile tile-forgery">
            <div style="font-size: 13px; font-weight: 700; color: #EF4444;">📜 Forgery</div>
            <div style="font-size: 11px; color: #9CA3AF;">Modify Signature</div>
        </div>
        <div class="cmd-scenario-tile tile-impersonation">
            <div style="font-size: 13px; font-weight: 700; color: #F59E0B;">👤 Impersonation</div>
            <div style="font-size: 11px; color: #9CA3AF;">Fake Sender</div>
        </div>
        <div class="cmd-scenario-tile tile-replay">
            <div style="font-size: 13px; font-weight: 700; color: #F97316;">🔄 Replay</div>
            <div style="font-size: 11px; color: #9CA3AF;">Reuse Signature</div>
        </div>
        <div class="cmd-scenario-tile tile-channel">
            <div style="font-size: 13px; font-weight: 700; color: #8B5CF6;">⚡ Channel Manipulation</div>
            <div style="font-size: 11px; color: #9CA3AF;">Pauli-X / Pauli-Z</div>
        </div>
    </div>
    """, unsafe_allow_html=True)


# ------------------------------------------------------------
# RIGHT COLUMN (STATISTICAL ANALYSIS, SECURITY METRICS, NOTICE)
# ------------------------------------------------------------

with right_col:
    # --------------------------------------------------------
    # STATISTICAL ANALYSIS CARD
    # --------------------------------------------------------
    decision_str = "THREAT" if stat_threat else "NORMAL"
    decision_class = "val-red" if stat_threat else "val-emerald"

    st.markdown(f"""
    <div class="cmd-card">
        <div style="display:flex; align-items:center; gap:8px; margin-bottom:4px;">
            <span style="font-size:16px; color:#A855F7;">📊</span>
            <div style="font-size: 14px; font-weight: 700; color: #FFFFFF;">Statistical Analysis</div>
        </div>
        <div style="font-size: 11px; color: #9CA3AF; margin-bottom: 12px;">Measurement comparison and statistical tests.</div>
        <div class="cmd-readout-grid">
            <div class="cmd-readout-box">
                <div class="cmd-readout-lbl">Error Rate</div>
                <div class="cmd-readout-val val-emerald">{err_rate * 100:.2f}%</div>
            </div>
            <div class="cmd-readout-box">
                <div class="cmd-readout-lbl">Chi-Square</div>
                <div class="cmd-readout-val val-cyan">{chi_val:.2f}</div>
            </div>
            <div class="cmd-readout-box">
                <div class="cmd-readout-lbl">Threshold</div>
                <div class="cmd-readout-val">{threshold:.2f}</div>
            </div>
            <div class="cmd-readout-box">
                <div class="cmd-readout-lbl">Decision</div>
                <div class="cmd-readout-val {decision_class}">{decision_str}</div>
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
    <div class="cmd-card">
        <div style="display:flex; align-items:center; gap:8px; margin-bottom:4px;">
            <span style="font-size:16px; color:#A855F7;">📈</span>
            <div style="font-size: 14px; font-weight: 700; color: #FFFFFF;">Security Metrics</div>
        </div>
        <div style="font-size: 11px; color: #9CA3AF; margin-bottom: 12px;">Performance indicators (Controlled Evaluation)</div>
        <div class="cmd-readout-grid">
            <div class="cmd-readout-box">
                <div class="cmd-readout-lbl">Detection Rate / TPR</div>
                <div class="cmd-readout-val val-emerald">{m['TPR']:.2f}%</div>
            </div>
            <div class="cmd-readout-box">
                <div class="cmd-readout-lbl">False Negative Rate / FNR</div>
                <div class="cmd-readout-val val-cyan">{m['FNR']:.2f}%</div>
            </div>
            <div class="cmd-readout-box">
                <div class="cmd-readout-lbl">False Positive Rate / FPR</div>
                <div class="cmd-readout-val val-amber">{m['FPR']:.2f}%</div>
            </div>
            <div class="cmd-readout-box">
                <div class="cmd-readout-lbl">Specificity / TNR</div>
                <div class="cmd-readout-val val-violet">{m['TNR']:.2f}%</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # --------------------------------------------------------
    # PROJECT NOTICE CARD
    # --------------------------------------------------------
    st.markdown("""
    <div class="cmd-card" style="padding:14px; border-color:rgba(6,182,212,0.3);">
        <div style="display:flex; align-items:center; gap:8px; margin-bottom:6px;">
            <span style="font-size:16px; color:#06B6D4;">ℹ️</span>
            <div style="font-size: 12px; font-weight: 700; color: #06B6D4;">Project Notice</div>
        </div>
        <div style="font-size: 11px; color: #9CA3AF; line-height: 1.4;">
            This is an Educational / Research Prototype for SIH 2026. Detection results depend on the selected quantum state, measurement basis, attack model, and statistical threshold.
        </div>
    </div>
    """, unsafe_allow_html=True)
