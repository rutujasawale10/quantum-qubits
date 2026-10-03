import sys
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

def clean_html(html_str):
    """Strip outer HTML linebreaks to prevent Markdown codeblocks while preserving <pre> circuit diagrams."""
    parts = html_str.split("<pre")
    if len(parts) > 1:
        res = ["".join(line.strip() for line in parts[0].splitlines() if line.strip())]
        for p in parts[1:]:
            pre_content, rest = p.split("</pre>", 1)
            clean_rest = "".join(line.strip() for line in rest.splitlines() if line.strip())
            res.append("<pre" + pre_content + "</pre>" + clean_rest)
        return "".join(res)
    return "".join(line.strip() for line in html_str.splitlines() if line.strip())

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

st.sidebar.markdown(clean_html("""
    <div style="margin-bottom: 18px;">
        <div style="font-size: 18px; font-weight: 800; color: #FFFFFF; display: flex; align-items: center; gap: 8px;">
            <span style="color: #A855F7; font-size: 20px;">⚛</span> Security Configuration
        </div>
        <div style="font-size: 12px; color: #9CA3AF; margin-top: 4px; line-height: 1.3;">
            Configure quantum signature state and attack scenario.
        </div>
    </div>
"""), unsafe_allow_html=True)

demo_preset = st.sidebar.selectbox(
    "⚡ FINAL SIH DEMO PRESETS",
    [
        "Custom Configuration",
        "A. Legitimate Communication (NONE -> VALID)",
        "B. Forgery Attack (FORGERY -> THREAT)",
        "C. Impersonation Attack (IMPERSONATION -> THREAT)",
        "D. Replay Attack (REPLAY -> THREAT)",
        "E. Channel Manipulation (CHANNEL -> THREAT)",
        "F. Unauthorized Verification (UNAUTHORIZED -> BLOCKED)"
    ]
)

# Preset Default Mappings
preset_state_idx = 0
preset_attack_idx = 0
preset_verifier_idx = 0
preset_rec_sender = "Attacker"

if demo_preset == "A. Legitimate Communication (NONE -> VALID)":
    preset_state_idx = 0  # |0>
    preset_attack_idx = 0  # NONE
    preset_verifier_idx = 0  # Bob
elif demo_preset == "B. Forgery Attack (FORGERY -> THREAT)":
    preset_state_idx = 0  # |0>
    preset_attack_idx = 1  # FORGERY
    preset_verifier_idx = 0  # Bob
elif demo_preset == "C. Impersonation Attack (IMPERSONATION -> THREAT)":
    preset_state_idx = 0  # |0>
    preset_attack_idx = 2  # IMPERSONATION
    preset_verifier_idx = 0  # Bob
    preset_rec_sender = "Attacker"
elif demo_preset == "D. Replay Attack (REPLAY -> THREAT)":
    preset_state_idx = 0  # |0>
    preset_attack_idx = 3  # REPLAY
    preset_verifier_idx = 0  # Bob
elif demo_preset == "E. Channel Manipulation (CHANNEL -> THREAT)":
    preset_state_idx = 2  # |+>
    preset_attack_idx = 4  # CHANNEL
    preset_verifier_idx = 0  # Bob
elif demo_preset == "F. Unauthorized Verification (UNAUTHORIZED -> BLOCKED)":
    preset_state_idx = 0  # |0>
    preset_attack_idx = 0  # NONE
    preset_verifier_idx = 1  # Eve

digital_message = st.sidebar.text_input(
    "Digital Message",
    value="SIH Quantum Digital Signature"
)

state_option = st.sidebar.selectbox(
    "Quantum Signature State",
    ["0", "1", "+", "-"],
    index=preset_state_idx,
    format_func=lambda x: f"|{x}⟩"
)

attack_option = st.sidebar.selectbox(
    "Attack Simulation",
    ["NONE", "FORGERY", "IMPERSONATION", "REPLAY", "CHANNEL"],
    index=preset_attack_idx,
    format_func=lambda x: {
        "NONE": "Genuine / No Attack",
        "FORGERY": "Forgery Attack",
        "IMPERSONATION": "Impersonation Attack",
        "REPLAY": "Replay Attack",
        "CHANNEL": "Channel Manipulation"
    }.get(x, x)
)

# Direct Inline CSS & Native JS DOM Styling for Sidebar Selectboxes
st.sidebar.markdown(clean_html("""
<style>
html body section[data-testid="stSidebar"] div[data-testid="stSelectbox"] *,
html body section[data-testid="stSidebar"] div[data-testid="stSelectbox"] input,
html body section[data-testid="stSidebar"] div[data-testid="stSelectbox"] div,
html body section[data-testid="stSidebar"] div[data-testid="stSelectbox"] button,
html body section[data-testid="stSidebar"] div[data-testid="stSelectbox"] [role="combobox"],
html body section[data-testid="stSidebar"] [data-baseweb="select"],
html body section[data-testid="stSidebar"] [data-baseweb="select"] *,
html body section[data-testid="stSidebar"] [data-baseweb="select"] > div,
html body section[data-testid="stSidebar"] [data-baseweb="select"] > div *,
html body section[data-testid="stSidebar"] .st-emotion-cache-zfrvrb,
html body section[data-testid="stSidebar"] .e1fp86qc1,
html body section[data-testid="stSidebar"] .e1fp86qc2 {
    background-color: #11182E !important;
    background: #11182E !important;
    color: #FFFFFF !important;
    -webkit-text-fill-color: #FFFFFF !important;
}
html body section[data-testid="stSidebar"] div[data-testid="stSelectbox"] label,
html body section[data-testid="stSidebar"] div[data-testid="stSelectbox"] label * {
    background-color: transparent !important;
    background: transparent !important;
    color: #E5E7EB !important;
}
html body section[data-testid="stSidebar"] div[data-testid="stSelectbox"] svg,
html body section[data-testid="stSidebar"] div[data-testid="stSelectbox"] path {
    fill: #C4B5FD !important;
    color: #C4B5FD !important;
}
</style>
<img src="data:image/gif;base64,R0lGODlhAQABAIAAAAAAAP///yH5BAEAAAAALAAAAAABAAEAAAIBRAA7" onload="
(function(){
    function fix() {
        const selects = document.querySelectorAll('[data-testid=\\'stSidebar\\'] [data-testid=\\'stSelectbox\\']');
        selects.forEach(sb => {
            const els = sb.querySelectorAll('div, input, button, span, [data-baseweb=\\'select\\']');
            els.forEach(el => {
                if (el.tagName.toLowerCase() === 'label' || el.closest('label')) return;
                if (el.tagName.toLowerCase() === 'svg' || el.tagName.toLowerCase() === 'path') {
                    el.style.setProperty('fill', '#C4B5FD', 'important');
                    el.style.setProperty('color', '#C4B5FD', 'important');
                    return;
                }
                el.style.setProperty('background-color', '#11182E', 'important');
                el.style.setProperty('background', '#11182E', 'important');
                el.style.setProperty('color', '#FFFFFF', 'important');
                el.style.setProperty('-webkit-text-fill-color', '#FFFFFF', 'important');
            });
            const outer = sb.querySelector('[data-baseweb=\\'select\\'] > div') || sb.querySelector('div');
            if (outer) {
                outer.style.setProperty('border', '1px solid rgba(139, 92, 246, 0.45)', 'important');
                outer.style.setProperty('border-radius', '10px', 'important');
            }
        });
    }
    fix();
    if(!window.__qds_sb_timer) window.__qds_sb_timer = setInterval(fix, 100);
})();
">
"""), unsafe_allow_html=True)

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

verifier_option = st.sidebar.selectbox(
    "Verifier Identity / Access Level",
    ["Bob (Authorized Receiver)", "Eve (Unauthorized Entity)"],
    index=preset_verifier_idx
)
actual_verifier = "Bob" if "Bob" in verifier_option else "Eve"

shots_val = st.sidebar.slider(
    "Measurement Shots",
    min_value=100,
    max_value=2000,
    value=1000,
    step=100
)

error_threshold_pct = st.sidebar.slider(
    "Statistical Error Threshold (%)",
    min_value=0.0,
    max_value=50.0,
    value=10.0,
    step=1.0,
    format="%.1f%%"
)

chi_threshold_val = st.sidebar.number_input(
    "Chi-Square Limit (χ²)",
    min_value=1.0,
    max_value=30.0,
    value=10.0,
    step=0.5
)

st.sidebar.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)

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

threshold = chi_threshold_val
stat_threat = (chi_val > threshold)

threat_detected = (
    stat_threat or identity_threat or replay_threat or forgery_threat or channel_threat
)

is_invisible = attack_res.get("invisible", False)

# Forgery Probability Analysis Calculation
forgery_prob_data = attack_simulator.calculate_forgery_probability(
    attack_option,
    state_option,
    attack_res.get("received_state", state_option),
    recv_counts,
    shots_val,
    identity_threat=identity_threat,
    replay_threat=replay_threat
)

state_wise_forgery_results = attack_simulator.evaluate_all_states_forgery(
    attack_option,
    shots=shots_val,
    channel_gate=channel_gate if attack_option == "CHANNEL" else "Z",
    measure_func=measure_state_in_basis,
    statevector_func=get_quantum_statevector,
    identity_threat=identity_threat,
    replay_threat=replay_threat
)

# Statistical Threshold Engine Calculation
threshold_engine_data = attack_simulator.evaluate_statistical_threshold(
    attack_option,
    err_rate,
    forgery_prob_data,
    chi_val,
    error_threshold_pct=error_threshold_pct,
    chi_threshold=chi_threshold_val,
    identity_threat=identity_threat,
    replay_threat=replay_threat
)

state_wise_threshold_results = attack_simulator.evaluate_state_wise_thresholds(
    state_wise_forgery_results,
    error_threshold_pct=error_threshold_pct
)

# Task #3: Pauli Eigenstate & Projective Measurement Module Calculations
projective_meas_data = attack_simulator.projective_measurement(
    state_option,
    basis,
    shots=shots_val,
    statevector_func=get_quantum_statevector,
    measure_func=measure_state_in_basis
)

all_eigenstate_projective_results = attack_simulator.evaluate_all_eigenstates_projective(
    shots=shots_val,
    statevector_func=get_quantum_statevector,
    measure_func=measure_state_in_basis
)

# Task #4: Verification Accuracy & Attack-wise Performance Analysis Module Calculations
attack_wise_performance_data = attack_simulator.evaluate_attack_performance(shots=shots_val)
controlled_8state_data = attack_simulator.run_controlled_8state_evaluation(shots=shots_val)






# ============================================================
# MAIN DASHBOARD LAYOUT (CENTER ~75% | METRICS RIGHT ~25%)
# ============================================================

main_col, right_col = st.columns([3.1, 1.0])

# ------------------------------------------------------------
# MAIN VERIFICATION WORKSPACE (CENTER COLUMN)
# ------------------------------------------------------------

with main_col:
    # --------------------------------------------------------
    # TOP HERO HEADER PANEL
    # --------------------------------------------------------
    st.markdown(clean_html("""
        <div class="cmd-hero">
            <div style="display:flex; align-items:center; gap:18px;">
                <div style="width:52px; height:52px; border-radius:14px; background:linear-gradient(135deg, #2D1B54, #1B1336); border:1px solid #A855F7; display:flex; align-items:center; justify-content:center; font-size:26px; box-shadow:0 0 15px rgba(168,85,247,0.3);">🛡️</div>
                <div>
                    <div style="font-size:11px; font-weight:800; color:#A855F7; letter-spacing:1.5px; text-transform:uppercase;">SIH 2026</div>
                    <div style="font-size:24px; font-weight:800; color:#FFFFFF; margin:2px 0; letter-spacing:-0.5px;">Quantum Digital Signature Security</div>
                    <div style="font-size:13px; color:#9CA3AF;">Quantum-Inspired Cyber Threat Detection for Digital Signature Security</div>
                    <div style="margin-top:10px; display:flex; flex-wrap:wrap; gap:4px;">
                        <span class="hero-badge-tag tag-violet">QDS-Inspired</span>
                        <span class="hero-badge-tag tag-blue">Qiskit 2.x</span>
                        <span class="hero-badge-tag tag-emerald">3-Qubit Teleportation</span>
                        <span class="hero-badge-tag tag-amber">Chi-Square Detection</span>
                        <span class="hero-badge-tag tag-magenta">4-Attack Evaluator</span>
                    </div>
                </div>
            </div>
            <div>
                <svg width="95" height="95" viewBox="0 0 100 100">
                    <defs>
                        <radialGradient id="heroAtomGlow" cx="50%" cy="50%" r="50%">
                            <stop offset="0%" stop-color="#C4B5FD" stop-opacity="1" />
                            <stop offset="60%" stop-color="#A855F7" stop-opacity="0.8" />
                            <stop offset="100%" stop-color="#7C3AED" stop-opacity="0" />
                        </radialGradient>
                        <linearGradient id="heroOrbit1" x1="0%" y1="0%" x2="100%" y2="100%">
                            <stop offset="0%" stop-color="#A855F7" />
                            <stop offset="100%" stop-color="#EC4899" />
                        </linearGradient>
                        <linearGradient id="heroOrbit2" x1="0%" y1="0%" x2="100%" y2="100%">
                            <stop offset="0%" stop-color="#06B6D4" />
                            <stop offset="100%" stop-color="#3B82F6" />
                        </linearGradient>
                    </defs>
                    <circle cx="50" cy="50" r="14" fill="url(#heroAtomGlow)" />
                    <circle cx="50" cy="50" r="5" fill="#FFFFFF" />
                    <ellipse cx="50" cy="50" rx="42" ry="15" fill="none" stroke="url(#heroOrbit1)" stroke-width="1.8" transform="rotate(0 50 50)" opacity="0.85"/>
                    <ellipse cx="50" cy="50" rx="42" ry="15" fill="none" stroke="url(#heroOrbit2)" stroke-width="1.8" transform="rotate(60 50 50)" opacity="0.85"/>
                    <ellipse cx="50" cy="50" rx="42" ry="15" fill="none" stroke="#A855F7" stroke-width="1.8" transform="rotate(120 50 50)" opacity="0.85"/>
                    <circle cx="92" cy="50" r="3.5" fill="#EC4899" />
                    <circle cx="29" cy="86" r="3.5" fill="#06B6D4" />
                    <circle cx="29" cy="14" r="3.5" fill="#A855F7" />
                </svg>
            </div>
        </div>
    """), unsafe_allow_html=True)

    # --------------------------------------------------------
    # SECURITY VERIFICATION RESULT PANEL
    # --------------------------------------------------------
    if is_invisible:
        banner_html = clean_html("""
            <div class="cmd-panel-invisible">
                <div style="display:flex; align-items:center; gap:14px;">
                    <div style="width:38px; height:38px; border-radius:50%; background:rgba(245,158,11,0.2); display:flex; align-items:center; justify-content:center; font-size:20px; color:#F59E0B;">⚠️</div>
                    <div>
                        <div style="font-size:16px; font-weight:700; color:#F59E0B;">ATTACK NOT DETECTED UNDER SELECTED BASIS</div>
                        <div style="font-size:13px; color:#9CA3AF;">State remains invariant under selected measurement basis.</div>
                    </div>
                </div>
                <div style="text-align:right;">
                    <div style="font-size:10px; text-transform:uppercase; color:#9CA3AF; font-weight:600;">Threat Level</div>
                    <div style="font-size:14px; font-weight:700; color:#F59E0B;">MODERATE</div>
                </div>
            </div>
        """)
    elif threat_detected:
        banner_html = clean_html(f"""
            <div class="cmd-panel-threat">
                <div style="display:flex; align-items:center; gap:14px;">
                    <div style="width:38px; height:38px; border-radius:50%; background:rgba(239,68,68,0.2); display:flex; align-items:center; justify-content:center; font-size:20px; color:#EF4444;">🚨</div>
                    <div>
                        <div style="font-size:16px; font-weight:700; color:#EF4444;">SECURITY THREAT DETECTED — {attack_res.get('attack', attack_option).upper()}</div>
                        <div style="font-size:13px; color:#9CA3AF;">Security verification anomaly detected. Signature Status: REJECTED.</div>
                    </div>
                </div>
                <div style="text-align:right;">
                    <div style="font-size:10px; text-transform:uppercase; color:#9CA3AF; font-weight:600;">Threat Level</div>
                    <div style="font-size:14px; font-weight:700; color:#EF4444;">HIGH</div>
                </div>
            </div>
        """)
    else:
        banner_html = clean_html("""
            <div class="cmd-panel-valid">
                <div style="display:flex; align-items:center; gap:14px;">
                    <div style="width:38px; height:38px; border-radius:50%; background:rgba(16,185,129,0.2); display:flex; align-items:center; justify-content:center; font-size:20px; color:#10B981;">✓</div>
                    <div>
                        <div style="font-size:16px; font-weight:700; color:#10B981;">SECURITY VERIFIED</div>
                        <div style="font-size:13px; color:#9CA3AF;">No attack detected. Signature is valid and consistent.</div>
                    </div>
                </div>
                <div style="text-align:right;">
                    <div style="font-size:10px; text-transform:uppercase; color:#9CA3AF; font-weight:600;">Threat Level</div>
                    <div style="font-size:14px; font-weight:700; color:#10B981;">LOW</div>
                </div>
            </div>
        """)

    verdict_text = "Threat Detected" if threat_detected else ("Invisible" if is_invisible else "No Threat")
    v_color = "#EF4444" if threat_detected else "#10B981"
    status_text = "REJECTED" if threat_detected else ("ATTACK NOT DETECTED" if is_invisible else "VALID")
    s_color = "#EF4444" if threat_detected else "#A855F7"
    recv_st = attack_res.get('received_state', state_option)

    st.markdown(clean_html(f"""
        <div class="cmd-card">
            <div style="font-size: 15px; font-weight: 700; color: #FFFFFF; margin-bottom: 14px; display:flex; align-items:center; gap:8px;">
                <span style="color:#A855F7; font-size:18px;">🛡️</span> Security Verification Result
            </div>
            {banner_html}
            <div class="cmd-tile-grid">
                <div class="cmd-tile-status">
                    <div class="cmd-tile-lbl">🛡️ ATTACK SCENARIO</div>
                    <div class="cmd-tile-val" style="color:#F59E0B;">{attack_res.get('attack', 'Genuine / No Attack')}</div>
                </div>
                <div class="cmd-tile-status">
                    <div class="cmd-tile-lbl">📊 DETECTION VERDICT</div>
                    <div class="cmd-tile-val" style="color:{v_color};">{verdict_text}</div>
                </div>
                <div class="cmd-tile-status">
                    <div class="cmd-tile-lbl">🔒 SIGNATURE STATUS</div>
                    <div class="cmd-tile-val" style="color:{s_color};">{status_text}</div>
                </div>
                <div class="cmd-tile-status">
                    <div class="cmd-tile-lbl">🔑 VERIFICATION BASIS</div>
                    <div class="cmd-tile-val" style="color:#3B82F6;">{basis}-Basis</div>
                </div>
                <div class="cmd-tile-status">
                    <div class="cmd-tile-lbl">⚛ ORIGINAL STATE</div>
                    <div class="cmd-tile-val" style="color:#A855F7;">|{state_option}⟩</div>
                </div>
                <div class="cmd-tile-status">
                    <div class="cmd-tile-lbl">⚛ RECEIVED STATE</div>
                    <div class="cmd-tile-val" style="color:#A855F7;">|{recv_st}⟩</div>
                </div>
            </div>
        </div>
    """), unsafe_allow_html=True)

    # --------------------------------------------------------
    # SECTION 01: DIGITAL SIGNATURE GENERATION
    # --------------------------------------------------------
    st.markdown(clean_html(f"""
        <div class="cmd-card">
            <div style="font-size: 15px; font-weight: 700; color: #FFFFFF; margin-bottom: 2px; display:flex; align-items:center; gap:8px;">
                <span style="width:24px; height:24px; border-radius:50%; background:#A855F7; color:#FFF; display:inline-flex; align-items:center; justify-content:center; font-size:12px; font-weight:800;">1</span>
                Digital Signature Generation
            </div>
            <div style="font-size: 13px; color: #9CA3AF; margin-bottom: 16px;">Quantum state preparation and signature generation using Qiskit.</div>
            <div class="cmd-flow-row">
                <div class="cmd-flow-box">
                    <div style="font-size:10px; color:#9CA3AF; text-transform:uppercase; font-weight:600;">💬 Digital Message</div>
                    <div style="font-size:13px; font-weight:700; color:#F3F4F6; margin-top:2px;">{digital_message}</div>
                </div>
                <div class="cmd-flow-arrow">→</div>
                <div class="cmd-flow-box">
                    <div style="font-size:10px; color:#9CA3AF; text-transform:uppercase; font-weight:600;">⚛ Quantum State</div>
                    <div style="font-size:13px; font-weight:700; color:#A855F7; margin-top:2px;">|{state_option}⟩</div>
                </div>
                <div class="cmd-flow-arrow">→</div>
                <div class="cmd-flow-box" style="flex:1.5;">
                    <div style="font-size:10px; color:#9CA3AF; text-transform:uppercase; font-weight:600;"></> Quantum Statevector</div>
                    <div class="cmd-terminal-box" style="margin-top:4px;">EDT {raw_array_text}</div>
                </div>
                <div class="cmd-flow-arrow">→</div>
                <div class="cmd-flow-box">
                    <div style="font-size:10px; color:#9CA3AF; text-transform:uppercase; font-weight:600;">✓ Signature Generated</div>
                    <div style="font-size:13px; font-weight:700; color:#10B981; margin-top:2px;">Yes</div>
                </div>
            </div>
        </div>
    """), unsafe_allow_html=True)

    # --------------------------------------------------------
    # SECTION 02: QUANTUM TELEPORTATION LAYER
    # --------------------------------------------------------
    teleport_qc = create_teleportation_circuit(state_option)
    st.markdown(clean_html(f"""
        <div class="cmd-card">
            <div style="font-size: 15px; font-weight: 700; color: #FFFFFF; margin-bottom: 2px; display:flex; align-items:center; gap:8px;">
                <span style="width:24px; height:24px; border-radius:50%; background:#A855F7; color:#FFF; display:inline-flex; align-items:center; justify-content:center; font-size:12px; font-weight:800;">2</span>
                Quantum Teleportation Layer
            </div>
            <div style="font-size: 13px; color: #9CA3AF; margin-bottom: 16px;">3-qubit teleportation circuit with coherent corrections.</div>
            
            <div style="display:flex; gap:16px; align-items:stretch; flex-wrap:wrap;">
                <div style="flex:1.8; min-width:320px;">
                    <div class="cmd-flow-row" style="flex-wrap:wrap; gap:8px;">
                        <div class="cmd-flow-box">
                            <div style="font-size:10px; color:#9CA3AF; font-weight:600;">Unknown State</div>
                            <div style="font-size:13px; font-weight:700; color:#F3F4F6; margin-top:2px;">|ψ⟩</div>
                        </div>
                        <div class="cmd-flow-arrow">→</div>
                        <div class="cmd-flow-box">
                            <div style="font-size:10px; color:#9CA3AF; font-weight:600;">Bell Pair Prep</div>
                            <div style="font-size:13px; font-weight:700; color:#3B82F6; margin-top:2px;">|Φ+⟩</div>
                        </div>
                        <div class="cmd-flow-arrow">→</div>
                        <div class="cmd-flow-box">
                            <div style="font-size:10px; color:#9CA3AF; font-weight:600;">Alice Operations</div>
                            <div style="font-size:13px; font-weight:700; color:#10B981; margin-top:2px;">(C<sub>Z</sub>, H)</div>
                        </div>
                        <div class="cmd-flow-arrow">→</div>
                        <div class="cmd-flow-box">
                            <div style="font-size:10px; color:#9CA3AF; font-weight:600;">Coherent Corrections</div>
                            <div style="font-size:13px; font-weight:700; color:#F59E0B; margin-top:2px;">(C<sub>X</sub>, C<sub>Z</sub>)</div>
                        </div>
                        <div class="cmd-flow-arrow">→</div>
                        <div class="cmd-flow-box">
                            <div style="font-size:10px; color:#9CA3AF; font-weight:600;">Bob's Qubit</div>
                            <div style="font-size:13px; font-weight:700; color:#A855F7; margin-top:2px;">|ψ⟩</div>
                        </div>
                    </div>
                </div>
                
                <div style="flex:1.2; min-width:260px;">
                    <div style="background-color: #0B0F1F; border: 1px solid rgba(139, 92, 246, 0.25); border-radius: 12px; padding: 12px 14px; height:100%;">
                        <div style="font-size: 10px; font-weight: 700; color: #9CA3AF; text-transform: uppercase; letter-spacing: 0.5px; display:flex; align-items:center; gap:6px;">
                            <span>⚙</span> Qiskit Quantum Circuit
                        </div>
                        <pre style="margin:8px 0 0 0; font-size: 11px; color: #C4B5FD; font-family: 'JetBrains Mono', monospace; background:transparent; overflow-x:auto;">{str(teleport_qc)}</pre>
                    </div>
                </div>
            </div>
        </div>
    """), unsafe_allow_html=True)

    # --------------------------------------------------------
    # SECTION 03: ATTACK SIMULATION
    # --------------------------------------------------------
    st.markdown(clean_html("""
        <div class="cmd-card">
            <div style="font-size: 15px; font-weight: 700; color: #FFFFFF; margin-bottom: 2px; display:flex; align-items:center; gap:8px;">
                <span style="width:24px; height:24px; border-radius:50%; background:#A855F7; color:#FFF; display:inline-flex; align-items:center; justify-content:center; font-size:12px; font-weight:800;">3</span>
                Attack Simulation
            </div>
            <div style="font-size: 13px; color: #9CA3AF; margin-bottom: 16px;">Simulate different attack scenarios and analyze detection results.</div>
            
            <div class="cmd-scenario-grid">
                <div class="cmd-scenario-tile tile-genuine">
                    <div style="font-size: 13px; font-weight: 700; color: #10B981; display:flex; align-items:center; gap:6px;">🛡️ Genuine</div>
                    <div style="font-size: 11px; color: #9CA3AF; margin-top:4px;">No Attack</div>
                </div>
                <div class="cmd-scenario-tile tile-forgery">
                    <div style="font-size: 13px; font-weight: 700; color: #EF4444; display:flex; align-items:center; gap:6px;">📜 Forgery</div>
                    <div style="font-size: 11px; color: #9CA3AF; margin-top:4px;">Modify Signature</div>
                </div>
                <div class="cmd-scenario-tile tile-impersonation">
                    <div style="font-size: 13px; font-weight: 700; color: #F59E0B; display:flex; align-items:center; gap:6px;">👤 Impersonation</div>
                    <div style="font-size: 11px; color: #9CA3AF; margin-top:4px;">Fake Sender</div>
                </div>
                <div class="cmd-scenario-tile tile-replay">
                    <div style="font-size: 13px; font-weight: 700; color: #F97316; display:flex; align-items:center; gap:6px;">🔄 Replay</div>
                    <div style="font-size: 11px; color: #9CA3AF; margin-top:4px;">Reuse Signature</div>
                </div>
                <div class="cmd-scenario-tile tile-channel">
                    <div style="font-size: 13px; font-weight: 700; color: #8B5CF6; display:flex; align-items:center; gap:6px;">⚡ Channel Manipulation</div>
                    <div style="font-size: 11px; color: #9CA3AF; margin-top:4px;">Pauli-X / Pauli-Z</div>
                </div>
            </div>
        </div>
    """), unsafe_allow_html=True)

    # --------------------------------------------------------
    # SECTION 04: FORGERY PROBABILITY ANALYSIS
    # --------------------------------------------------------
    prob_str = forgery_prob_data["estimated_prob_str"]
    decision_val = forgery_prob_data["status"]

    if decision_val in ["FORGED", "REJECTED (SENDER MISMATCH)", "REPLAY DETECTED"]:
        status_color = "#EF4444"
        status_icon = "⚠"
        prob_color = "#EF4444"
    elif "VALID" in decision_val:
        status_color = "#10B981"
        status_icon = "✓"
        prob_color = "#10B981" if not prob_str.startswith("N/A") else "#06B6D4"
    else:
        status_color = "#F59E0B"
        status_icon = "⚠️"
        prob_color = "#F59E0B"

    # Build State-Wise Table Rows HTML
    table_rows_html = ""
    for r in state_wise_forgery_results:
        r_st = r["status"]
        r_color = "#EF4444" if ("FORGED" in r_st or "REJECTED" in r_st or "REPLAY" in r_st) else "#10B981"
        r_icon = "⚠" if ("FORGED" in r_st or "REJECTED" in r_st or "REPLAY" in r_st) else "✓"

        table_rows_html += f"""
            <tr style="border-bottom: 1px solid rgba(139, 92, 246, 0.15); color: #E5E7EB;">
                <td style="padding: 8px; font-weight: 700; color: #A855F7;">{r['state']}</td>
                <td style="padding: 8px; font-weight: 700; color: #C4B5FD;">{r['received_state']}</td>
                <td style="padding: 8px; color: #3B82F6;">{r['basis']}</td>
                <td style="padding: 8px; font-family: 'JetBrains Mono', monospace;">{r['total_shots']}</td>
                <td style="padding: 8px; font-family: 'JetBrains Mono', monospace;">{r['mismatches']}</td>
                <td style="padding: 8px; font-weight: 700; color: {r_color};">{r['forgery_prob']}</td>
                <td style="padding: 8px; font-weight: 700; color: {r_color};">{r_icon} {r['status']}</td>
            </tr>
        """

    st.markdown(clean_html(f"""
        <div class="cmd-card">
            <div style="font-size: 15px; font-weight: 700; color: #FFFFFF; margin-bottom: 2px; display:flex; align-items:center; gap:8px;">
                <span style="width:24px; height:24px; border-radius:50%; background:#A855F7; color:#FFF; display:inline-flex; align-items:center; justify-content:center; font-size:12px; font-weight:800;">4</span>
                Forgery Probability Analysis
            </div>
            <div style="font-size: 13px; color: #9CA3AF; margin-bottom: 16px;">
                Simulation-based probability evaluation from measurement data. (Prototype Simulation)
            </div>

            <div class="cmd-tile-grid" style="grid-template-columns: repeat(6, 1fr); margin-bottom: 16px;">
                <div class="cmd-tile-status">
                    <div class="cmd-tile-lbl">⚛ ORIGINAL STATE</div>
                    <div class="cmd-tile-val" style="color:#A855F7;">|{state_option}⟩</div>
                </div>
                <div class="cmd-tile-status">
                    <div class="cmd-tile-lbl">⚛ RECEIVED STATE</div>
                    <div class="cmd-tile-val" style="color:#A855F7;">|{attack_res.get('received_state', state_option)}⟩</div>
                </div>
                <div class="cmd-tile-status">
                    <div class="cmd-tile-lbl">📊 MEASUREMENTS</div>
                    <div class="cmd-tile-val" style="color:#3B82F6;">{forgery_prob_data['total_shots']}</div>
                </div>
                <div class="cmd-tile-status">
                    <div class="cmd-tile-lbl">⚠️ MISMATCHES</div>
                    <div class="cmd-tile-val" style="color:{'#EF4444' if (isinstance(forgery_prob_data['mismatches'], int) and forgery_prob_data['mismatches'] > 0) else '#10B981'};">{forgery_prob_data['mismatches']}</div>
                </div>
                <div class="cmd-tile-status">
                    <div class="cmd-tile-lbl">🎯 FORGERY PROBABILITY</div>
                    <div class="cmd-tile-val" style="color:{prob_color}; font-size:12px;">{prob_str}</div>
                </div>
                <div class="cmd-tile-status">
                    <div class="cmd-tile-lbl">🔒 DECISION</div>
                    <div class="cmd-tile-val" style="color:{status_color};">{status_icon} {decision_val}</div>
                </div>
            </div>

            <div style="background: #0B0F1F; border: 1px solid rgba(139, 92, 246, 0.25); border-radius: 12px; padding: 14px 16px;">
                <div style="font-size: 12px; font-weight: 700; color: #C4B5FD; text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 10px; display:flex; align-items:center; gap:6px;">
                    <span>🔬</span> State-Wise Forgery Comparison Matrix ({attack_option} Scenario)
                </div>
                <div style="overflow-x:auto;">
                    <table style="width: 100%; border-collapse: collapse; font-size: 12px; text-align: left;">
                        <thead>
                            <tr style="border-bottom: 1px solid rgba(139, 92, 246, 0.3); color: #9CA3AF;">
                                <th style="padding: 6px 8px;">State</th>
                                <th style="padding: 6px 8px;">Received State</th>
                                <th style="padding: 6px 8px;">Basis</th>
                                <th style="padding: 6px 8px;">Shots</th>
                                <th style="padding: 6px 8px;">Mismatches</th>
                                <th style="padding: 6px 8px;">Estimated Forgery Probability</th>
                                <th style="padding: 6px 8px;">Status</th>
                            </tr>
                        </thead>
                        <tbody>
                            {table_rows_html}
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
    """), unsafe_allow_html=True)

    # --------------------------------------------------------
    # SECTION 05: STATISTICAL THRESHOLD ENGINE
    # --------------------------------------------------------
    th_is_threat = threshold_engine_data["is_threat"]
    th_status_color = "#EF4444" if th_is_threat else "#10B981"
    th_status_icon = "⚠" if th_is_threat else "✓"
    margin_val = threshold_engine_data["margin_pct"]
    margin_color = "#EF4444" if margin_val > 0 else "#10B981"
    margin_sign = "+" if margin_val > 0 else ""

    th_table_rows_html = ""
    for r in state_wise_threshold_results:
        is_abv = (r["verdict"] == "THREAT")
        r_col = "#EF4444" if is_abv else "#10B981"
        r_icn = "⚠" if is_abv else "✓"

        th_table_rows_html += f"""
            <tr style="border-bottom: 1px solid rgba(139, 92, 246, 0.15); color: #E5E7EB;">
                <td style="padding: 8px; font-weight: 700; color: #A855F7;">{r['state']}</td>
                <td style="padding: 8px; font-weight: 700; color: #C4B5FD;">{r['received_state']}</td>
                <td style="padding: 8px; color: #3B82F6;">{r['basis']}</td>
                <td style="padding: 8px; font-family: 'JetBrains Mono', monospace;">{r['total_shots']}</td>
                <td style="padding: 8px; font-weight: 700; color: {r_col};">{r['forgery_prob']}</td>
                <td style="padding: 8px; font-family: 'JetBrains Mono', monospace; color: #F59E0B;">{r['error_threshold_pct']}</td>
                <td style="padding: 8px; font-weight: 700; color: {r_col};">{r['threshold_evaluation']}</td>
                <td style="padding: 8px; font-weight: 700; color: {r_col};">{r_icn} {r['verdict']}</td>
            </tr>
        """

    st.markdown(clean_html(f"""
        <div class="cmd-card">
            <div style="font-size: 15px; font-weight: 700; color: #FFFFFF; margin-bottom: 2px; display:flex; align-items:center; gap:8px;">
                <span style="width:24px; height:24px; border-radius:50%; background:#A855F7; color:#FFF; display:inline-flex; align-items:center; justify-content:center; font-size:12px; font-weight:800;">5</span>
                Statistical Threshold Engine
            </div>
            <div style="font-size: 13px; color: #9CA3AF; margin-bottom: 16px;">
                Threat identification by comparing measurement mismatch rates against configurable critical thresholds.
            </div>

            <div style="background: linear-gradient(135deg, rgba(21, 29, 56, 0.9) 0%, rgba(15, 22, 41, 0.9) 100%); border: 1px solid rgba(139, 92, 246, 0.3); border-radius: 14px; padding: 14px 18px; margin-bottom: 16px;">
                <div style="font-size: 11px; font-weight: 700; color: #C4B5FD; text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 8px;">
                    ⚡ Statistical Threshold Core Flow
                </div>
                <div class="cmd-flow-row" style="flex-wrap: wrap; gap: 8px;">
                    <div class="cmd-flow-box">
                        <div style="font-size:10px; color:#9CA3AF; font-weight:600;">Observed Error Rate</div>
                        <div style="font-size:13px; font-weight:700; color:#06B6D4; margin-top:2px;">{threshold_engine_data['observed_error_pct']:.2f}%</div>
                    </div>
                    <div class="cmd-flow-arrow">→</div>
                    <div class="cmd-flow-box">
                        <div style="font-size:10px; color:#9CA3AF; font-weight:600;">Configured Threshold</div>
                        <div style="font-size:13px; font-weight:700; color:#F59E0B; margin-top:2px;">{threshold_engine_data['error_threshold_pct']:.2f}%</div>
                    </div>
                    <div class="cmd-flow-arrow">→</div>
                    <div class="cmd-flow-box">
                        <div style="font-size:10px; color:#9CA3AF; font-weight:600;">Threshold Margin</div>
                        <div style="font-size:13px; font-weight:700; color:{margin_color}; margin-top:2px;">{margin_sign}{abs(threshold_engine_data['margin_pct']):.2f}%</div>
                    </div>
                    <div class="cmd-flow-arrow">→</div>
                    <div class="cmd-flow-box" style="flex: 1.2;">
                        <div style="font-size:10px; color:#9CA3AF; font-weight:600;">Classification Verdict</div>
                        <div style="font-size:13px; font-weight:800; color:{th_status_color}; margin-top:2px;">{th_status_icon} {threshold_engine_data['verdict_label']}</div>
                    </div>
                </div>
            </div>

            <div class="cmd-tile-grid" style="grid-template-columns: repeat(4, 1fr); margin-bottom: 16px;">
                <div class="cmd-tile-status">
                    <div class="cmd-tile-lbl">📊 ERROR vs THRESHOLD</div>
                    <div class="cmd-tile-val" style="color:{th_status_color};">{threshold_engine_data['observed_error_pct']:.2f}% / {threshold_engine_data['error_threshold_pct']:.2f}%</div>
                </div>
                <div class="cmd-tile-status">
                    <div class="cmd-tile-lbl">📐 CHI-SQUARE vs LIMIT</div>
                    <div class="cmd-tile-val" style="color:#06B6D4;">{threshold_engine_data['chi_square_val']:.2f} / {threshold_engine_data['chi_threshold']:.2f}</div>
                </div>
                <div class="cmd-tile-status">
                    <div class="cmd-tile-lbl">🎯 THREAT MARGIN</div>
                    <div class="cmd-tile-val" style="color:{margin_color};">{margin_sign}{abs(threshold_engine_data['margin_pct']):.2f}%</div>
                </div>
                <div class="cmd-tile-status">
                    <div class="cmd-tile-lbl">🔒 ENGINE VERDICT</div>
                    <div class="cmd-tile-val" style="color:{th_status_color};">{th_status_icon} {threshold_engine_data['verdict']}</div>
                </div>
            </div>

            <div style="background: #0B0F1F; border: 1px solid rgba(139, 92, 246, 0.25); border-radius: 12px; padding: 14px 16px;">
                <div style="font-size: 12px; font-weight: 700; color: #C4B5FD; text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 10px; display:flex; align-items:center; gap:6px;">
                    <span>📈</span> State-Wise Threshold Evaluation Matrix ({attack_option} Scenario)
                </div>
                <div style="overflow-x:auto;">
                    <table style="width: 100%; border-collapse: collapse; font-size: 12px; text-align: left;">
                        <thead>
                            <tr style="border-bottom: 1px solid rgba(139, 92, 246, 0.3); color: #9CA3AF;">
                                <th style="padding: 6px 8px;">State</th>
                                <th style="padding: 6px 8px;">Received</th>
                                <th style="padding: 6px 8px;">Basis</th>
                                <th style="padding: 6px 8px;">Shots</th>
                                <th style="padding: 6px 8px;">Forgery / Error Rate</th>
                                <th style="padding: 6px 8px;">Threshold Limit</th>
                                <th style="padding: 6px 8px;">Threshold Evaluation</th>
                                <th style="padding: 6px 8px;">Verdict</th>
                            </tr>
                        </thead>
                        <tbody>
                            {th_table_rows_html}
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
    """), unsafe_allow_html=True)

    # --------------------------------------------------------
    # SECTION 06: PAULI EIGENSTATE & PROJECTIVE MEASUREMENT
    # --------------------------------------------------------
    pm_state = projective_meas_data["state"]
    pm_basis = projective_meas_data["basis_label"]
    pm_nat = projective_meas_data["natural_basis"]
    pm_is_nat = projective_meas_data["is_natural"]
    pm_exp = projective_meas_data["expected_result"]
    pm_theo = projective_meas_data["theoretical_probs"]
    pm_meas_p = projective_meas_data["measured_probs"]
    pm_counts = projective_meas_data["measured_counts"]

    theo_str = ", ".join([f"P({k})={v:.2f}" for k, v in pm_theo.items()])
    meas_str = ", ".join([f"P({k})={v:.4f}" for k, v in pm_meas_p.items()])

    nat_badge_color = "#10B981" if pm_is_nat else "#F59E0B"
    nat_badge_text = "NATURAL BASIS (DETERMINISTIC)" if pm_is_nat else "SUPERPOSITION BASIS (PROBABILISTIC 50/50)"

    # Build Eigenstate Matrix Table Rows
    pm_table_rows_html = ""
    for r in all_eigenstate_projective_results:
        r_nat = "YES (Deterministic)" if r["is_natural"] else "NO (50/50 Superposition)"
        r_nat_col = "#10B981" if r["is_natural"] else "#F59E0B"
        r_theo = ", ".join([f"P({k})={v:.2f}" for k, v in r["theoretical_probs"].items()])
        r_meas = ", ".join([f"P({k})={v:.2f}" for k, v in r["measured_probs"].items()])

        pm_table_rows_html += f"""
            <tr style="border-bottom: 1px solid rgba(139, 92, 246, 0.15); color: #E5E7EB;">
                <td style="padding: 8px; font-weight: 700; color: #A855F7;">{r['state']}</td>
                <td style="padding: 8px; color: #3B82F6;">{r['basis_label']}</td>
                <td style="padding: 8px; font-weight: 700; color: {r_nat_col};">{r_nat}</td>
                <td style="padding: 8px; font-weight: 700; color: #F59E0B;">{r['expected_result']}</td>
                <td style="padding: 8px; font-family: 'JetBrains Mono', monospace; color: #C4B5FD;">{r_theo}</td>
                <td style="padding: 8px; font-family: 'JetBrains Mono', monospace; color: #06B6D4;">{r_meas}</td>
                <td style="padding: 8px; font-family: 'JetBrains Mono', monospace;">0: {r['measured_counts']['0']} | 1: {r['measured_counts']['1']}</td>
            </tr>
        """

    st.markdown(clean_html(f"""
        <div class="cmd-card">
            <div style="font-size: 15px; font-weight: 700; color: #FFFFFF; margin-bottom: 2px; display:flex; align-items:center; gap:8px;">
                <span style="width:24px; height:24px; border-radius:50%; background:#A855F7; color:#FFF; display:inline-flex; align-items:center; justify-content:center; font-size:12px; font-weight:800;">6</span>
                Pauli Eigenstate & Projective Measurement Module
            </div>
            <div style="font-size: 13px; color: #9CA3AF; margin-bottom: 16px;">
                Projective measurement simulation of Pauli eigenstates in Z and X bases. (Educational / Prototype Simulation)
            </div>

            <div style="background: linear-gradient(135deg, rgba(21, 29, 56, 0.9) 0%, rgba(15, 22, 41, 0.9) 100%); border: 1px solid rgba(139, 92, 246, 0.3); border-radius: 14px; padding: 14px 18px; margin-bottom: 16px;">
                <div style="font-size: 11px; font-weight: 700; color: #C4B5FD; text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 8px;">
                    ⚡ Measurement Execution Flow
                </div>
                <div class="cmd-flow-row" style="flex-wrap: wrap; gap: 6px;">
                    <div class="cmd-flow-box">
                        <div style="font-size:9px; color:#9CA3AF; font-weight:600;">Quantum State</div>
                        <div style="font-size:12px; font-weight:700; color:#A855F7; margin-top:2px;">{pm_state}</div>
                    </div>
                    <div class="cmd-flow-arrow">→</div>
                    <div class="cmd-flow-box">
                        <div style="font-size:9px; color:#9CA3AF; font-weight:600;">Pauli Eigenstate</div>
                        <div style="font-size:12px; font-weight:700; color:#EC4899; margin-top:2px;">Pauli-{pm_nat}</div>
                    </div>
                    <div class="cmd-flow-arrow">→</div>
                    <div class="cmd-flow-box">
                        <div style="font-size:9px; color:#9CA3AF; font-weight:600;">Measurement Basis</div>
                        <div style="font-size:12px; font-weight:700; color:#3B82F6; margin-top:2px;">{pm_basis}</div>
                    </div>
                    <div class="cmd-flow-arrow">→</div>
                    <div class="cmd-flow-box">
                        <div style="font-size:9px; color:#9CA3AF; font-weight:600;">Projective Measurement</div>
                        <div style="font-size:12px; font-weight:700; color:#F59E0B; margin-top:2px;">P<sub>{basis}</sub></div>
                    </div>
                    <div class="cmd-flow-arrow">→</div>
                    <div class="cmd-flow-box">
                        <div style="font-size:9px; color:#9CA3AF; font-weight:600;">Measurement Counts</div>
                        <div style="font-size:12px; font-weight:700; color:#06B6D4; margin-top:2px;">{pm_counts['0']} / {pm_counts['1']}</div>
                    </div>
                    <div class="cmd-flow-arrow">→</div>
                    <div class="cmd-flow-box">
                        <div style="font-size:9px; color:#9CA3AF; font-weight:600;">Statistical Analysis</div>
                        <div style="font-size:12px; font-weight:700; color:#10B981; margin-top:2px;">Validated</div>
                    </div>
                </div>
            </div>

            <div class="cmd-tile-grid" style="grid-template-columns: repeat(6, 1fr); margin-bottom: 16px;">
                <div class="cmd-tile-status">
                    <div class="cmd-tile-lbl">⚛ SELECTED STATE</div>
                    <div class="cmd-tile-val" style="color:#A855F7;">{pm_state}</div>
                </div>
                <div class="cmd-tile-status">
                    <div class="cmd-tile-lbl">🔑 MEASUREMENT BASIS</div>
                    <div class="cmd-tile-val" style="color:#3B82F6;">{pm_basis}</div>
                </div>
                <div class="cmd-tile-status">
                    <div class="cmd-tile-lbl">🎯 EXPECTED RESULT</div>
                    <div class="cmd-tile-val" style="color:#F59E0B;">{pm_exp}</div>
                </div>
                <div class="cmd-tile-status">
                    <div class="cmd-tile-lbl">📐 THEORETICAL PROB.</div>
                    <div class="cmd-tile-val" style="color:#C4B5FD; font-size:11px;">{theo_str}</div>
                </div>
                <div class="cmd-tile-status">
                    <div class="cmd-tile-lbl">📊 MEASURED PROB.</div>
                    <div class="cmd-tile-val" style="color:#06B6D4; font-size:11px;">{meas_str}</div>
                </div>
                <div class="cmd-tile-status">
                    <div class="cmd-tile-lbl">🔒 BASIS REGIME</div>
                    <div class="cmd-tile-val" style="color:{nat_badge_color}; font-size:10px;">{nat_badge_text}</div>
                </div>
            </div>

            <div style="background: #0B0F1F; border: 1px solid rgba(139, 92, 246, 0.25); border-radius: 12px; padding: 14px 16px;">
                <div style="font-size: 12px; font-weight: 700; color: #C4B5FD; text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 10px; display:flex; align-items:center; gap:6px;">
                    <span>🔬</span> Full Pauli Eigenstate & Projective Measurement Matrix (All States & Bases)
                </div>
                <div style="overflow-x:auto;">
                    <table style="width: 100%; border-collapse: collapse; font-size: 12px; text-align: left;">
                        <thead>
                            <tr style="border-bottom: 1px solid rgba(139, 92, 246, 0.3); color: #9CA3AF;">
                                <th style="padding: 6px 8px;">State</th>
                                <th style="padding: 6px 8px;">Basis</th>
                                <th style="padding: 6px 8px;">Natural Basis Match</th>
                                <th style="padding: 6px 8px;">Expected Result</th>
                                <th style="padding: 6px 8px;">Theoretical Probability</th>
                                <th style="padding: 6px 8px;">Measured Probability</th>
                                <th style="padding: 6px 8px;">Shot Counts</th>
                            </tr>
                        </thead>
                        <tbody>
                            {pm_table_rows_html}
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
    """), unsafe_allow_html=True)

    # --------------------------------------------------------
    # SECTION 07: VERIFICATION ACCURACY & ATTACK PERFORMANCE MODULE
    # --------------------------------------------------------
    attack_perf_data = attack_simulator.evaluate_attack_performance(shots=shots_val)
    ctrl_eval_data = attack_simulator.run_controlled_8state_evaluation(shots=shots_val)

    overall_metrics = attack_perf_data["overall"]
    attack_wise_results = attack_perf_data["attack_wise"]
    ctrl_eval_results = ctrl_eval_data["results"]

    # Build Attack-Wise Performance Matrix Table Rows
    attack_wise_rows_html = ""
    for aw in attack_wise_results:
        tpr_str = aw["tpr_str"]
        if tpr_str.startswith("N/A"):
            aw_tpr_col = "#64748B"
        else:
            try:
                aw_tpr_col = "#10B981" if float(tpr_str.replace("%","")) >= 80.0 else "#F59E0B"
            except (ValueError, TypeError):
                aw_tpr_col = "#64748B"

        fnr_str = aw["fnr_str"]
        if fnr_str.startswith("N/A"):
            aw_fnr_col = "#64748B"
        else:
            try:
                aw_fnr_col = "#EF4444" if float(fnr_str.replace("%","")) > 10.0 else "#10B981"
            except (ValueError, TypeError):
                aw_fnr_col = "#64748B"
        attack_wise_rows_html += f"""
            <tr style="border-bottom: 1px solid rgba(139, 92, 246, 0.15); color: #E5E7EB;">
                <td style="padding: 8px; font-weight: 700; color: #3B82F6;">{aw['label']} ({aw['attack']})</td>
                <td style="padding: 8px; font-family: 'JetBrains Mono', monospace;">{aw['total_cases']}</td>
                <td style="padding: 8px; font-weight: 700; color: #10B981;">{aw['detected_threats']}</td>
                <td style="padding: 8px; font-weight: 700; color: #EF4444;">{aw['missed_threats']}</td>
                <td style="padding: 8px; font-weight: 700; color: #F59E0B;">{aw['false_alarms']}</td>
                <td style="padding: 8px; font-weight: 700; color: {aw_tpr_col};">{aw['tpr_str']}</td>
                <td style="padding: 8px; font-weight: 700; color: {aw_fnr_col};">{aw['fnr_str']}</td>
                <td style="padding: 8px; color: #9CA3AF;">{aw['fpr_str']}</td>
                <td style="padding: 8px; color: #A855F7;">{aw['tnr_str']}</td>
            </tr>
        """

    # Build Controlled 8-State Evaluation Table Rows
    ctrl_rows_html = ""
    for cr in ctrl_eval_results:
        if cr["verdict_class"] == "THREAT":
            v_col = "#10B981"
        elif cr["verdict_class"] == "NORMAL":
            v_col = "#3B82F6"
        elif cr["verdict_class"] == "FALSE ALARM":
            v_col = "#F59E0B"
        else:
            v_col = "#EF4444"

        exp_col = "#EF4444" if cr["expected_threat"] == "YES" else "#10B981"
        det_col = "#10B981" if cr["detected"] == "YES" else "#9CA3AF"

        ctrl_rows_html += f"""
            <tr style="border-bottom: 1px solid rgba(139, 92, 246, 0.15); color: #E5E7EB;">
                <td style="padding: 8px; font-weight: 700; color: #C4B5FD;">{cr['label']}</td>
                <td style="padding: 8px; font-family: 'JetBrains Mono', monospace; color: #A855F7;">{cr['state']}</td>
                <td style="padding: 8px; font-family: 'JetBrains Mono', monospace; color: #EC4899;">{cr['received']}</td>
                <td style="padding: 8px; color: #3B82F6;">{cr['basis']}</td>
                <td style="padding: 8px; font-weight: 600;">{cr['attack']}</td>
                <td style="padding: 8px; font-weight: 700; color: {exp_col};">{cr['expected_threat']}</td>
                <td style="padding: 8px; font-weight: 700; color: {det_col};">{cr['detected']}</td>
                <td style="padding: 8px; font-weight: 700; color: {v_col};">{cr['verdict']}</td>
            </tr>
        """

    st.markdown(clean_html(f"""
        <div class="cmd-card">
            <div style="font-size: 15px; font-weight: 700; color: #FFFFFF; margin-bottom: 2px; display:flex; align-items:center; gap:8px;">
                <span style="width:24px; height:24px; border-radius:50%; background:#10B981; color:#FFF; display:inline-flex; align-items:center; justify-content:center; font-size:12px; font-weight:800;">7</span>
                Verification Accuracy & Attack-wise Performance Analysis
            </div>
            <div style="font-size: 13px; color: #9CA3AF; margin-bottom: 16px;">
                Empirical evaluation of detection performance across attacks, confusion matrix metrics (TPR, FNR, FPR, TNR), and controlled 8-state prototype benchmarks. (Controlled Test / Prototype Evaluation)
            </div>

            <!-- Verification Flow -->
            <div style="background: linear-gradient(135deg, rgba(21, 29, 56, 0.9) 0%, rgba(15, 22, 41, 0.9) 100%); border: 1px solid rgba(16, 185, 129, 0.3); border-radius: 14px; padding: 14px 18px; margin-bottom: 16px;">
                <div style="font-size: 11px; font-weight: 700; color: #A7F3D0; text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 8px;">
                    🛡️ End-to-End Threat Verification & Performance Evaluation Pipeline
                </div>
                <div class="cmd-flow-row" style="flex-wrap: wrap; gap: 6px;">
                    <div class="cmd-flow-box">
                        <div style="font-size:9px; color:#9CA3AF; font-weight:600;">Input State / Attack</div>
                        <div style="font-size:11px; font-weight:700; color:#A855F7; margin-top:2px;">Attack Simulator</div>
                    </div>
                    <div class="cmd-flow-arrow">→</div>
                    <div class="cmd-flow-box">
                        <div style="font-size:9px; color:#9CA3AF; font-weight:600;">Verification Stage 1</div>
                        <div style="font-size:11px; font-weight:700; color:#3B82F6; margin-top:2px;">Signature & Identity</div>
                    </div>
                    <div class="cmd-flow-arrow">→</div>
                    <div class="cmd-flow-box">
                        <div style="font-size:9px; color:#9CA3AF; font-weight:600;">Verification Stage 2</div>
                        <div style="font-size:11px; font-weight:700; color:#F59E0B; margin-top:2px;">Measurement & Deviation</div>
                    </div>
                    <div class="cmd-flow-arrow">→</div>
                    <div class="cmd-flow-box">
                        <div style="font-size:9px; color:#9CA3AF; font-weight:600;">Verification Stage 3</div>
                        <div style="font-size:11px; font-weight:700; color:#EC4899; margin-top:2px;">Threshold Engine</div>
                    </div>
                    <div class="cmd-flow-arrow">→</div>
                    <div class="cmd-flow-box">
                        <div style="font-size:9px; color:#9CA3AF; font-weight:600;">Verdict Classification</div>
                        <div style="font-size:11px; font-weight:700; color:#10B981; margin-top:2px;">Detected / Missed</div>
                    </div>
                    <div class="cmd-flow-arrow">→</div>
                    <div class="cmd-flow-box">
                        <div style="font-size:9px; color:#9CA3AF; font-weight:600;">Performance Matrix</div>
                        <div style="font-size:11px; font-weight:700; color:#06B6D4; margin-top:2px;">TPR / FNR / FPR / TNR</div>
                    </div>
                </div>
            </div>

            <!-- Readouts Grid 1: Raw Confusion Matrix -->
            <div style="font-size: 11px; font-weight: 700; color: #9CA3AF; text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 6px;">
                📊 Raw Confusion Matrix Readout
            </div>
            <div class="cmd-readout-grid" style="margin-bottom: 16px;">
                <div class="cmd-readout-box">
                    <div class="cmd-readout-lbl">True Positives (TP)</div>
                    <div class="cmd-readout-val val-emerald">{overall_metrics['TP']}</div>
                </div>
                <div class="cmd-readout-box">
                    <div class="cmd-readout-lbl">True Negatives (TN)</div>
                    <div class="cmd-readout-val val-cyan">{overall_metrics['TN']}</div>
                </div>
                <div class="cmd-readout-box">
                    <div class="cmd-readout-lbl">False Positives (FP)</div>
                    <div class="cmd-readout-val val-amber">{overall_metrics['FP']}</div>
                </div>
                <div class="cmd-readout-box">
                    <div class="cmd-readout-lbl">False Negatives (FN)</div>
                    <div class="cmd-readout-val val-red">{overall_metrics['FN']}</div>
                </div>
            </div>

            <!-- Readouts Grid 2: Detection Performance Metrics -->
            <div style="font-size: 11px; font-weight: 700; color: #9CA3AF; text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 6px;">
                🎯 System Detection Performance Metrics
            </div>
            <div class="cmd-readout-grid" style="margin-bottom: 16px;">
                <div class="cmd-readout-box">
                    <div class="cmd-readout-lbl">Detection Rate / TPR</div>
                    <div class="cmd-readout-val val-emerald">{overall_metrics['TPR_str']}</div>
                </div>
                <div class="cmd-readout-box">
                    <div class="cmd-readout-lbl">False Negative Rate / FNR</div>
                    <div class="cmd-readout-val val-red">{overall_metrics['FNR_str']}</div>
                </div>
                <div class="cmd-readout-box">
                    <div class="cmd-readout-lbl">False Positive Rate / FPR</div>
                    <div class="cmd-readout-val val-amber">{overall_metrics['FPR_str']}</div>
                </div>
                <div class="cmd-readout-box">
                    <div class="cmd-readout-lbl">Specificity / TNR</div>
                    <div class="cmd-readout-val val-violet">{overall_metrics['TNR_str']}</div>
                </div>
            </div>

            <!-- Attack-Wise Performance Table -->
            <div style="background: #0B0F1F; border: 1px solid rgba(16, 185, 129, 0.25); border-radius: 12px; padding: 14px 16px; margin-bottom: 16px;">
                <div style="font-size: 12px; font-weight: 700; color: #A7F3D0; text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 10px; display:flex; align-items:center; gap:6px;">
                    <span>⚔️</span> Attack-Wise Detection Performance Matrix
                </div>
                <div style="overflow-x:auto;">
                    <table style="width: 100%; border-collapse: collapse; font-size: 12px; text-align: left;">
                        <thead>
                            <tr style="border-bottom: 1px solid rgba(16, 185, 129, 0.3); color: #9CA3AF;">
                                <th style="padding: 6px 8px;">Attack Scenario</th>
                                <th style="padding: 6px 8px;">Cases</th>
                                <th style="padding: 6px 8px;">Detected</th>
                                <th style="padding: 6px 8px;">Missed</th>
                                <th style="padding: 6px 8px;">False Alarms</th>
                                <th style="padding: 6px 8px;">Detection Rate / TPR</th>
                                <th style="padding: 6px 8px;">FNR</th>
                                <th style="padding: 6px 8px;">FPR</th>
                                <th style="padding: 6px 8px;">TNR</th>
                            </tr>
                        </thead>
                        <tbody>
                            {attack_wise_rows_html}
                        </tbody>
                    </table>
                </div>
            </div>

            <!-- Controlled 8-State Evaluation Table -->
            <div style="background: #0B0F1F; border: 1px solid rgba(139, 92, 246, 0.25); border-radius: 12px; padding: 14px 16px;">
                <div style="font-size: 12px; font-weight: 700; color: #C4B5FD; text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 10px; display:flex; align-items:center; gap:6px;">
                    <span>🧪</span> Controlled Prototype Evaluation Benchmark Matrix (8 Test Cases)
                </div>
                <div style="overflow-x:auto;">
                    <table style="width: 100%; border-collapse: collapse; font-size: 12px; text-align: left;">
                        <thead>
                            <tr style="border-bottom: 1px solid rgba(139, 92, 246, 0.3); color: #9CA3AF;">
                                <th style="padding: 6px 8px;">Test Case</th>
                                <th style="padding: 6px 8px;">Transmitted</th>
                                <th style="padding: 6px 8px;">Received</th>
                                <th style="padding: 6px 8px;">Basis</th>
                                <th style="padding: 6px 8px;">Attack Type</th>
                                <th style="padding: 6px 8px;">Expected Threat</th>
                                <th style="padding: 6px 8px;">Detected</th>
                                <th style="padding: 6px 8px;">Verdict Classification</th>
                            </tr>
                        </thead>
                        <tbody>
                            {ctrl_rows_html}
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
    """), unsafe_allow_html=True)

    # --------------------------------------------------------
    # SECTION 08: NOISE & ROBUSTNESS ANALYSIS MODULE
    # --------------------------------------------------------
    noise_eval_data = attack_simulator.evaluate_noise_vs_attack_matrix(
        noise_levels=[0.0, 0.01, 0.02, 0.05, 0.10],
        shots=shots_val,
        threshold=error_threshold_pct / 100.0
    )

    noise_matrix = noise_eval_data["matrix"]
    noise_summary = noise_eval_data["summary"]

    # Selected Noise Test Case (Default: 2% Noise on Legitimate Communication)
    sel_noise_item = noise_matrix[2]  # NONE with 2% noise
    for nm in noise_matrix:
        if nm["attack"] == attack_option and abs(nm["noise_level"] - 0.02) < 0.001:
            sel_noise_item = nm
            break

    # Build Noise Matrix Table Rows
    noise_table_rows_html = ""
    for nr in noise_matrix:
        cond_col = "#10B981" if nr["attack"] == "NONE" else "#3B82F6"
        v_col = "#EF4444" if nr["is_threat"] else "#10B981"

        if nr["is_correct"]:
            res_col = "#10B981"
            res_icon = "✓"
        elif "False Alarm" in nr["classification_result"]:
            res_col = "#F59E0B"
            res_icon = "⚠️"
        else:
            res_col = "#EF4444"
            res_icon = "❌"

        noise_table_rows_html += f"""
            <tr style="border-bottom: 1px solid rgba(139, 92, 246, 0.15); color: #E5E7EB;">
                <td style="padding: 8px; font-weight: 700; color: {cond_col};">{nr['condition']}</td>
                <td style="padding: 8px; font-family: 'JetBrains Mono', monospace; color: #F59E0B;">{nr['noise_pct_str']}</td>
                <td style="padding: 8px; font-family: 'JetBrains Mono', monospace; color: #06B6D4;">{nr['observed_error_pct_str']}</td>
                <td style="padding: 8px; font-family: 'JetBrains Mono', monospace; color: #A855F7;">{nr['threshold_pct_str']}</td>
                <td style="padding: 8px; font-weight: 700; color: {v_col};">{nr['verdict']}</td>
                <td style="padding: 8px; font-weight: 600; color: {res_col};">{res_icon} {nr['classification_result']}</td>
            </tr>
        """

    st.markdown(clean_html(f"""
        <div class="cmd-card">
            <div style="font-size: 15px; font-weight: 700; color: #FFFFFF; margin-bottom: 2px; display:flex; align-items:center; gap:8px;">
                <span style="width:24px; height:24px; border-radius:50%; background:#F59E0B; color:#FFF; display:inline-flex; align-items:center; justify-content:center; font-size:12px; font-weight:800;">8</span>
                Noise & Robustness Analysis Module
            </div>
            <div style="font-size: 13px; color: #9CA3AF; margin-bottom: 16px;">
                Controlled noise robustness experiment evaluating baseline channel noise vs. attack-induced deviations. (Controlled Experiment / Prototype Simulation)
            </div>

            <!-- Noise Evaluation Flow -->
            <div style="background: linear-gradient(135deg, rgba(21, 29, 56, 0.9) 0%, rgba(15, 22, 41, 0.9) 100%); border: 1px solid rgba(245, 158, 11, 0.3); border-radius: 14px; padding: 14px 18px; margin-bottom: 16px;">
                <div style="font-size: 11px; font-weight: 700; color: #FDE68A; text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 8px;">
                    ⚡ Noise vs. Attack Classification Pipeline
                </div>
                <div class="cmd-flow-row" style="flex-wrap: wrap; gap: 6px;">
                    <div class="cmd-flow-box">
                        <div style="font-size:9px; color:#9CA3AF; font-weight:600;">Channel Model</div>
                        <div style="font-size:11px; font-weight:700; color:#F59E0B; margin-top:2px;">Baseline Noise</div>
                    </div>
                    <div class="cmd-flow-arrow">→</div>
                    <div class="cmd-flow-box">
                        <div style="font-size:9px; color:#9CA3AF; font-weight:600;">State Measurement</div>
                        <div style="font-size:11px; font-weight:700; color:#06B6D4; margin-top:2px;">Measurement Variation</div>
                    </div>
                    <div class="cmd-flow-arrow">→</div>
                    <div class="cmd-flow-box">
                        <div style="font-size:9px; color:#9CA3AF; font-weight:600;">Threshold Engine</div>
                        <div style="font-size:11px; font-weight:700; color:#A855F7; margin-top:2px;">Statistical Threshold</div>
                    </div>
                    <div class="cmd-flow-arrow">→</div>
                    <div class="cmd-flow-box">
                        <div style="font-size:9px; color:#9CA3AF; font-weight:600;">Decision Output</div>
                        <div style="font-size:11px; font-weight:700; color:#10B981; margin-top:2px;">Normal / Threat</div>
                    </div>
                </div>
            </div>

            <!-- Readout Boxes Grid (6 Items as requested) -->
            <div style="font-size: 11px; font-weight: 700; color: #9CA3AF; text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 6px;">
                📊 Active Condition Readout (Sample Noise Level)
            </div>
            <div class="cmd-tile-grid" style="grid-template-columns: repeat(6, 1fr); margin-bottom: 16px;">
                <div class="cmd-tile-status">
                    <div class="cmd-tile-lbl">🌐 NOISE LEVEL</div>
                    <div class="cmd-tile-val" style="color:#F59E0B;">{sel_noise_item['noise_pct_str']}</div>
                </div>
                <div class="cmd-tile-status">
                    <div class="cmd-tile-lbl">📈 OBSERVED ERROR</div>
                    <div class="cmd-tile-val" style="color:#06B6D4;">{sel_noise_item['observed_error_pct_str']}</div>
                </div>
                <div class="cmd-tile-status">
                    <div class="cmd-tile-lbl">⚖️ THRESHOLD</div>
                    <div class="cmd-tile-val" style="color:#A855F7;">{sel_noise_item['threshold_pct_str']}</div>
                </div>
                <div class="cmd-tile-status">
                    <div class="cmd-tile-lbl">🛡️ VERDICT</div>
                    <div class="cmd-tile-val" style="color:{'#EF4444' if sel_noise_item['is_threat'] else '#10B981'};">{sel_noise_item['verdict']}</div>
                </div>
                <div class="cmd-tile-status">
                    <div class="cmd-tile-lbl">⚔️ ATTACK STATUS</div>
                    <div class="cmd-tile-val" style="color:{'#EF4444' if sel_noise_item['expected_threat'] else '#10B981'}; font-size:10px;">{'ATTACK ACTIVE' if sel_noise_item['expected_threat'] else 'LEGITIMATE'}</div>
                </div>
                <div class="cmd-tile-status">
                    <div class="cmd-tile-lbl">🎯 CLASSIFICATION</div>
                    <div class="cmd-tile-val" style="color:{'#10B981' if sel_noise_item['is_correct'] else '#F59E0B'}; font-size:10px;">{sel_noise_item['classification_result']}</div>
                </div>
            </div>

            <!-- Compact Comparison Table -->
            <div style="background: #0B0F1F; border: 1px solid rgba(245, 158, 11, 0.25); border-radius: 12px; padding: 14px 16px;">
                <div style="font-size: 12px; font-weight: 700; color: #FDE68A; text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 10px; display:flex; align-items:center; gap:6px;">
                    <span>📋</span> Controlled Noise Robustness Matrix (0%, 1%, 2%, 5%, 10% Noise Levels)
                </div>
                <div style="overflow-x:auto;">
                    <table style="width: 100%; border-collapse: collapse; font-size: 12px; text-align: left;">
                        <thead>
                            <tr style="border-bottom: 1px solid rgba(245, 158, 11, 0.3); color: #9CA3AF;">
                                <th style="padding: 6px 8px;">Condition</th>
                                <th style="padding: 6px 8px;">Noise Level</th>
                                <th style="padding: 6px 8px;">Observed Error Rate</th>
                                <th style="padding: 6px 8px;">Threshold</th>
                                <th style="padding: 6px 8px;">Verdict</th>
                                <th style="padding: 6px 8px;">Classification Result</th>
                            </tr>
                        </thead>
                        <tbody>
                            {noise_table_rows_html}
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
    """), unsafe_allow_html=True)

    # --------------------------------------------------------
    # SECTION 09: UNAUTHORIZED VERIFICATION ATTEMPT MODULE
    # --------------------------------------------------------
    unauth_verification_data = attack_simulator.evaluate_unauthorized_verification(
        sender=expected_sender if attack_option == "IMPERSONATION" else "Alice",
        expected_verifier="Bob",
        actual_verifier=actual_verifier,
        signature_valid=(not threat_detected)
    )

    controlled_auth_data = attack_simulator.run_controlled_authorization_evaluation()
    auth_cases = controlled_auth_data["cases"]
    auth_metrics = controlled_auth_data["metrics"]

    auth_rows_html = ""
    for ac in auth_cases:
        ac_status_col = "#10B981" if ac["identity_status"] == "AUTHORIZED" else "#EF4444"
        ac_access_col = "#10B981" if ac["verification_allowed"] == "ALLOWED" else "#EF4444"
        ac_threat_col = "#EF4444" if ac["threat_detected"] == "YES" else "#10B981"

        auth_rows_html += f"""
            <tr style="border-bottom: 1px solid rgba(139, 92, 246, 0.15); color: #E5E7EB;">
                <td style="padding: 8px; font-weight: 700; color: #C4B5FD;">{ac['test_name']}</td>
                <td style="padding: 8px; color: #A855F7;">{ac['sender']}</td>
                <td style="padding: 8px; color: #3B82F6;">{ac['expected_verifier']}</td>
                <td style="padding: 8px; font-weight: 700; color: {'#10B981' if ac['actual_verifier']=='Bob' else '#EF4444'};">{ac['actual_verifier']}</td>
                <td style="padding: 8px; color: #06B6D4;">{ac['sig_valid']}</td>
                <td style="padding: 8px; font-weight: 700; color: {ac_status_col};">{ac['identity_status']}</td>
                <td style="padding: 8px; font-weight: 700; color: {ac_access_col};">{ac['verification_allowed']}</td>
                <td style="padding: 8px; font-weight: 700; color: {ac_threat_col};">{ac['threat_detected']}</td>
                <td style="padding: 8px; font-weight: 600; color: #F59E0B;">{ac['classification']}</td>
            </tr>
        """

    is_unauth_active = not unauth_verification_data["verification_allowed"]
    auth_badge_col = "#EF4444" if is_unauth_active else "#10B981"

    st.markdown(clean_html(f"""
        <div class="cmd-card">
            <div style="font-size: 15px; font-weight: 700; color: #FFFFFF; margin-bottom: 2px; display:flex; align-items:center; gap:8px;">
                <span style="width:24px; height:24px; border-radius:50%; background:#EF4444; color:#FFF; display:inline-flex; align-items:center; justify-content:center; font-size:12px; font-weight:800;">9</span>
                Unauthorized Verification Attempt Detection Module
            </div>
            <div style="font-size: 13px; color: #9CA3AF; margin-bottom: 16px;">
                Prototype identity authorization layer distinguishing legitimate verifier (Bob) from unauthorized verifier access attempts (Eve). (Simulated Authorization / Prototype Security)
            </div>

            <!-- Authorization Flow Pipeline -->
            <div style="background: linear-gradient(135deg, rgba(21, 29, 56, 0.9) 0%, rgba(15, 22, 41, 0.9) 100%); border: 1px solid rgba(239, 68, 68, 0.3); border-radius: 14px; padding: 14px 18px; margin-bottom: 16px;">
                <div style="font-size: 11px; font-weight: 700; color: #FCA5A5; text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 8px;">
                    🛡️ Verifier Authorization & Access Control Pipeline
                </div>
                <div class="cmd-flow-row" style="flex-wrap: wrap; gap: 6px;">
                    <div class="cmd-flow-box">
                        <div style="font-size:9px; color:#9CA3AF; font-weight:600;">Message Sender</div>
                        <div style="font-size:11px; font-weight:700; color:#A855F7; margin-top:2px;">{unauth_verification_data['sender']}</div>
                    </div>
                    <div class="cmd-flow-arrow">→</div>
                    <div class="cmd-flow-box">
                        <div style="font-size:9px; color:#9CA3AF; font-weight:600;">Expected Verifier</div>
                        <div style="font-size:11px; font-weight:700; color:#3B82F6; margin-top:2px;">{unauth_verification_data['expected_verifier']}</div>
                    </div>
                    <div class="cmd-flow-arrow">→</div>
                    <div class="cmd-flow-box">
                        <div style="font-size:9px; color:#9CA3AF; font-weight:600;">Actual Verifier</div>
                        <div style="font-size:11px; font-weight:700; color:{'#10B981' if unauth_verification_data['actual_verifier']=='Bob' else '#EF4444'}; margin-top:2px;">{unauth_verification_data['actual_verifier']}</div>
                    </div>
                    <div class="cmd-flow-arrow">→</div>
                    <div class="cmd-flow-box">
                        <div style="font-size:9px; color:#9CA3AF; font-weight:600;">Authorization Status</div>
                        <div style="font-size:11px; font-weight:700; color:{auth_badge_col}; margin-top:2px;">{unauth_verification_data['identity_status']}</div>
                    </div>
                    <div class="cmd-flow-arrow">→</div>
                    <div class="cmd-flow-box">
                        <div style="font-size:9px; color:#9CA3AF; font-weight:600;">Verification Access</div>
                        <div style="font-size:11px; font-weight:700; color:{auth_badge_col}; margin-top:2px;">{unauth_verification_data['access_label']}</div>
                    </div>
                    <div class="cmd-flow-arrow">→</div>
                    <div class="cmd-flow-box">
                        <div style="font-size:9px; color:#9CA3AF; font-weight:600;">Downstream Pipeline</div>
                        <div style="font-size:11px; font-weight:700; color:{'#10B981' if unauth_verification_data['verification_allowed'] else '#EF4444'}; margin-top:2px;">{'CONTINUED' if unauth_verification_data['verification_allowed'] else 'BLOCKED AT GATEWAY'}</div>
                    </div>
                </div>
            </div>

            <!-- Readouts Grid -->
            <div style="font-size: 11px; font-weight: 700; color: #9CA3AF; text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 6px;">
                📊 Active Authorization Readout
            </div>
            <div class="cmd-tile-grid" style="grid-template-columns: repeat(6, 1fr); margin-bottom: 16px;">
                <div class="cmd-tile-status">
                    <div class="cmd-tile-lbl">🔑 VERIFIER IDENTITY</div>
                    <div class="cmd-tile-val" style="color:#3B82F6;">{unauth_verification_data['actual_verifier']}</div>
                </div>
                <div class="cmd-tile-status">
                    <div class="cmd-tile-lbl">🔒 AUTHORIZATION</div>
                    <div class="cmd-tile-val" style="color:{auth_badge_col};">{unauth_verification_data['identity_status']}</div>
                </div>
                <div class="cmd-tile-status">
                    <div class="cmd-tile-lbl">🚫 VERIFICATION ACCESS</div>
                    <div class="cmd-tile-val" style="color:{auth_badge_col};">{unauth_verification_data['access_label']}</div>
                </div>
                <div class="cmd-tile-status">
                    <div class="cmd-tile-lbl">🛡️ THREAT STATUS</div>
                    <div class="cmd-tile-val" style="color:{auth_badge_col}; font-size:10px;">{'THREAT DETECTED' if unauth_verification_data['threat_detected'] else 'NORMAL'}</div>
                </div>
                <div class="cmd-tile-status">
                    <div class="cmd-tile-lbl">⚠️ THREAT TYPE</div>
                    <div class="cmd-tile-val" style="color:{auth_badge_col}; font-size:9px;">{unauth_verification_data['threat_type']}</div>
                </div>
                <div class="cmd-tile-status">
                    <div class="cmd-tile-lbl">📐 SIGNATURE VALIDITY</div>
                    <div class="cmd-tile-val" style="color:{'#10B981' if unauth_verification_data['signature_valid'] else '#EF4444'}; font-size:10px;">{'VALID MATH SIG' if unauth_verification_data['signature_valid'] else 'INVALID / FORGED'}</div>
                </div>
            </div>

            <!-- Controlled Authorization Benchmark Table -->
            <div style="background: #0B0F1F; border: 1px solid rgba(239, 68, 68, 0.25); border-radius: 12px; padding: 14px 16px;">
                <div style="font-size: 12px; font-weight: 700; color: #FCA5A5; text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 10px; display:flex; align-items:center; gap:6px;">
                    <span>📋</span> Controlled Authorization Detection Benchmark Matrix
                </div>
                <div style="overflow-x:auto;">
                    <table style="width: 100%; border-collapse: collapse; font-size: 12px; text-align: left;">
                        <thead>
                            <tr style="border-bottom: 1px solid rgba(239, 68, 68, 0.3); color: #9CA3AF;">
                                <th style="padding: 6px 8px;">Test Case</th>
                                <th style="padding: 6px 8px;">Sender</th>
                                <th style="padding: 6px 8px;">Expected Verifier</th>
                                <th style="padding: 6px 8px;">Actual Verifier</th>
                                <th style="padding: 6px 8px;">Sig State</th>
                                <th style="padding: 6px 8px;">Auth Status</th>
                                <th style="padding: 6px 8px;">Access</th>
                                <th style="padding: 6px 8px;">Threat</th>
                                <th style="padding: 6px 8px;">Classification Result</th>
                            </tr>
                        </thead>
                        <tbody>
                            {auth_rows_html}
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
    """), unsafe_allow_html=True)

    # --------------------------------------------------------
    # --------------------------------------------------------
    # SECTION 10: EFFICIENT VERIFICATION & PERFORMANCE EVALUATION MODULE
    # --------------------------------------------------------
    perf_eval_data = attack_simulator.run_performance_evaluation(attempts=100, shots=shots_val)
    perf_cases = perf_eval_data["cases"]
    perf_summary = perf_eval_data["summary"]
    perf_fp_summary = perf_eval_data.get("full_pipeline_summary", {})
    perf_ag_summary = perf_eval_data.get("auth_gateway_summary", {})

    perf_table_rows_html = ""
    for pc in perf_cases:
        res_col = "#10B981" if pc["result"] == "VALID" else ("#EF4444" if pc["result"] == "THREAT" else "#F59E0B")
        path_col = "#A855F7" if pc.get("path") == "Full Pipeline" else "#F59E0B"

        perf_table_rows_html += f"""
            <tr style="border-bottom: 1px solid rgba(139, 92, 246, 0.15); color: #E5E7EB;">
                <td style="padding: 8px; font-weight: 700; color: #3B82F6;">{pc['case_name']}</td>
                <td style="padding: 8px; font-weight: 600; color: {path_col};">{pc.get('path', 'Full Pipeline')}</td>
                <td style="padding: 8px; font-family: 'JetBrains Mono', monospace;">{pc['attempts']}</td>
                <td style="padding: 8px; font-weight: 700; color: #10B981; font-family: 'JetBrains Mono', monospace;">{pc['avg_time_ms_str']}</td>
                <td style="padding: 8px; font-family: 'JetBrains Mono', monospace; color: #06B6D4;">{pc['min_time_ms_str']}</td>
                <td style="padding: 8px; font-family: 'JetBrains Mono', monospace; color: #F59E0B;">{pc['max_time_ms_str']}</td>
                <td style="padding: 8px; font-weight: 700; color: {res_col};">{pc['result']}</td>
            </tr>
        """

    st.markdown(clean_html(f"""
        <div class="cmd-card">
            <div style="font-size: 15px; font-weight: 700; color: #FFFFFF; margin-bottom: 2px; display:flex; align-items:center; gap:8px;">
                <span style="width:24px; height:24px; border-radius:50%; background:#3B82F6; color:#FFF; display:inline-flex; align-items:center; justify-content:center; font-size:12px; font-weight:800;">10</span>
                Efficient Verification & Performance Evaluation Module
            </div>
            <div style="font-size: 13px; color: #9CA3AF; margin-bottom: 16px;">
                Controlled measurement of verification pipeline execution timing via high-resolution CPU timer. (Controlled Prototype Performance Evaluation)
            </div>

            <!-- Performance Flow -->
            <div style="background: linear-gradient(135deg, rgba(21, 29, 56, 0.9) 0%, rgba(15, 22, 41, 0.9) 100%); border: 1px solid rgba(59, 130, 246, 0.3); border-radius: 14px; padding: 14px 18px; margin-bottom: 16px;">
                <div style="font-size: 11px; font-weight: 700; color: #93C5FD; text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 8px;">
                    ⏱️ Verification Execution Timing Pipeline
                </div>
                <div class="cmd-flow-row" style="flex-wrap: wrap; gap: 6px;">
                    <div class="cmd-flow-box">
                        <div style="font-size:9px; color:#9CA3AF; font-weight:600;">Trigger Event</div>
                        <div style="font-size:11px; font-weight:700; color:#A855F7; margin-top:2px;">Timer Start</div>
                    </div>
                    <div class="cmd-flow-arrow">→</div>
                    <div class="cmd-flow-box">
                        <div style="font-size:9px; color:#9CA3AF; font-weight:600;">Gateway Layer</div>
                        <div style="font-size:11px; font-weight:700; color:#3B82F6; margin-top:2px;">Authorization Check</div>
                    </div>
                    <div class="cmd-flow-arrow">→</div>
                    <div class="cmd-flow-box">
                        <div style="font-size:9px; color:#9CA3AF; font-weight:600;">Verification Layer</div>
                        <div style="font-size:11px; font-weight:700; color:#F59E0B; margin-top:2px;">Quantum Verification</div>
                    </div>
                    <div class="cmd-flow-arrow">→</div>
                    <div class="cmd-flow-box">
                        <div style="font-size:9px; color:#9CA3AF; font-weight:600;">High-Res Measurement</div>
                        <div style="font-size:11px; font-weight:700; color:#06B6D4; margin-top:2px;">time.perf_counter()</div>
                    </div>
                    <div class="cmd-flow-arrow">→</div>
                    <div class="cmd-flow-box">
                        <div style="font-size:9px; color:#9CA3AF; font-weight:600;">Performance Output</div>
                        <div style="font-size:11px; font-weight:700; color:#10B981; margin-top:2px;">Avg / Min / Max ms</div>
                    </div>
                </div>
            </div>

            <!-- Readout Grid: Full Pipeline -->
            <div style="font-size: 11px; font-weight: 700; color: #10B981; text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 6px;">
                ⚡ FULL VERIFICATION PIPELINE METRICS (Cases 1–3, 300 Attempts)
            </div>
            <div class="cmd-readout-grid" style="margin-bottom: 14px;">
                <div class="cmd-readout-box">
                    <div class="cmd-readout-lbl">Full Pipeline Avg Time</div>
                    <div class="cmd-readout-val val-emerald">{perf_fp_summary.get('avg_time_ms_str', 'N/A')}</div>
                </div>
                <div class="cmd-readout-box">
                    <div class="cmd-readout-lbl">Full Pipeline Min Time</div>
                    <div class="cmd-readout-val val-cyan">{perf_fp_summary.get('min_time_ms_str', 'N/A')}</div>
                </div>
                <div class="cmd-readout-box">
                    <div class="cmd-readout-lbl">Full Pipeline Max Time</div>
                    <div class="cmd-readout-val val-amber">{perf_fp_summary.get('max_time_ms_str', 'N/A')}</div>
                </div>
                <div class="cmd-readout-box">
                    <div class="cmd-readout-lbl">Full Pipeline Total Time</div>
                    <div class="cmd-readout-val val-violet">{perf_fp_summary.get('total_time_ms_str', 'N/A')}</div>
                </div>
            </div>

            <!-- Readout Grid: Authorization Gateway -->
            <div style="font-size: 11px; font-weight: 700; color: #F59E0B; text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 6px;">
                🔑 AUTHORIZATION GATEWAY METRICS (Case 4, 100 Attempts)
            </div>
            <div class="cmd-readout-grid" style="margin-bottom: 16px;">
                <div class="cmd-readout-box">
                    <div class="cmd-readout-lbl">Auth Gateway Avg Time</div>
                    <div class="cmd-readout-val val-amber">{perf_ag_summary.get('avg_time_ms_str', 'N/A')}</div>
                </div>
                <div class="cmd-readout-box">
                    <div class="cmd-readout-lbl">Auth Gateway Min Time</div>
                    <div class="cmd-readout-val val-cyan">{perf_ag_summary.get('min_time_ms_str', 'N/A')}</div>
                </div>
                <div class="cmd-readout-box">
                    <div class="cmd-readout-lbl">Auth Gateway Max Time</div>
                    <div class="cmd-readout-val val-violet">{perf_ag_summary.get('max_time_ms_str', 'N/A')}</div>
                </div>
                <div class="cmd-readout-box">
                    <div class="cmd-readout-lbl">Total Benchmark Time</div>
                    <div class="cmd-readout-val val-emerald">{perf_summary['total_time_sec_str']}</div>
                </div>
            </div>

            <!-- Compact Performance Table -->
            <div style="background: #0B0F1F; border: 1px solid rgba(59, 130, 246, 0.25); border-radius: 12px; padding: 14px 16px; margin-bottom: 16px;">
                <div style="font-size: 12px; font-weight: 700; color: #93C5FD; text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 10px; display:flex; align-items:center; gap:6px;">
                    <span>⚡</span> Controlled Benchmark Performance Matrix (100 Attempts Per Case)
                </div>
                <div style="overflow-x:auto;">
                    <table style="width: 100%; border-collapse: collapse; font-size: 12px; text-align: left;">
                        <thead>
                            <tr style="border-bottom: 1px solid rgba(59, 130, 246, 0.3); color: #9CA3AF;">
                                <th style="padding: 6px 8px;">Test Case</th>
                                <th style="padding: 6px 8px;">Path</th>
                                <th style="padding: 6px 8px;">Attempts</th>
                                <th style="padding: 6px 8px;">Avg Time (ms)</th>
                                <th style="padding: 6px 8px;">Min (ms)</th>
                                <th style="padding: 6px 8px;">Max (ms)</th>
                                <th style="padding: 6px 8px;">Result</th>
                            </tr>
                        </thead>
                        <tbody>
                            {perf_table_rows_html}
                        </tbody>
                    </table>
                </div>
            </div>

            <!-- Efficiency Analysis Notice -->
            <div style="background: rgba(59, 130, 246, 0.08); border: 1px solid rgba(59, 130, 246, 0.25); border-radius: 10px; padding: 10px 14px; font-size: 12px; color: #9CA3AF; line-height: 1.5;">
                <strong style="color:#93C5FD;">💡 Measured Efficiency Analysis:</strong> Full verification pipeline timing includes Qiskit statevector generation, shot-based projective measurement, chi-square calculation, and threshold engine evaluation. Authorization gateway timing measures rapid blocking of unauthorized verifiers prior to quantum state processing.
            </div>
        </div>
    """), unsafe_allow_html=True)



# ------------------------------------------------------------
# RIGHT COLUMN (STATISTICAL ANALYSIS, SECURITY METRICS, NOTICE)
# ------------------------------------------------------------

with right_col:
    # --------------------------------------------------------
    # STATISTICAL ANALYSIS CARD
    # --------------------------------------------------------
    decision_str = threshold_engine_data["verdict"]
    decision_class = "val-red" if th_is_threat else "val-emerald"

    st.markdown(clean_html(f"""
        <div class="cmd-card">
            <div style="display:flex; align-items:center; gap:8px; margin-bottom:4px;">
                <span style="font-size:18px; color:#A855F7;">📊</span>
                <div style="font-size: 15px; font-weight: 700; color: #FFFFFF;">Statistical Analysis</div>
            </div>
            <div style="font-size: 12px; color: #9CA3AF; margin-bottom: 14px;">Measurement comparison and statistical tests.</div>

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
                    <div class="cmd-readout-lbl">Error Threshold</div>
                    <div class="cmd-readout-val val-amber">{error_threshold_pct:.1f}%</div>
                </div>
                <div class="cmd-readout-box">
                    <div class="cmd-readout-lbl">Threshold Verdict</div>
                    <div class="cmd-readout-val {decision_class}">{decision_str}</div>
                </div>
            </div>
        </div>
    """), unsafe_allow_html=True)

    # --------------------------------------------------------
    # AUTHORIZATION METRICS CARD
    # --------------------------------------------------------
    st.markdown(clean_html(f"""
        <div class="cmd-card">
            <div style="display:flex; align-items:center; gap:8px; margin-bottom:4px;">
                <span style="font-size:18px; color:#EF4444;">🔑</span>
                <div style="font-size: 15px; font-weight: 700; color: #FFFFFF;">Authorization Metrics</div>
            </div>
            <div style="font-size: 12px; color: #9CA3AF; margin-bottom: 14px;">Controlled Authorization Detection Evaluation</div>

            <div class="cmd-readout-grid">
                <div class="cmd-readout-box">
                    <div class="cmd-readout-lbl">Auth Detection Rate</div>
                    <div class="cmd-readout-val val-emerald">{auth_metrics['authorization_detection_rate_str']}</div>
                </div>
                <div class="cmd-readout-box">
                    <div class="cmd-readout-lbl">False Auth Rate</div>
                    <div class="cmd-readout-val val-cyan">{auth_metrics['false_authorization_rate_str']}</div>
                </div>
                <div class="cmd-readout-box">
                    <div class="cmd-readout-lbl">Blocked Unauthorized</div>
                    <div class="cmd-readout-val val-emerald">{auth_metrics['correctly_blocked']} / {auth_metrics['unauthorized_attempts']}</div>
                </div>
                <div class="cmd-readout-box">
                    <div class="cmd-readout-lbl">Allowed Authorized</div>
                    <div class="cmd-readout-val val-violet">{auth_metrics['correctly_allowed']} / {auth_metrics['authorized_attempts']}</div>
                </div>
            </div>
        </div>
    """), unsafe_allow_html=True)

    # --------------------------------------------------------
    # PERFORMANCE METRICS CARD
    # --------------------------------------------------------
    st.markdown(clean_html(f"""
        <div class="cmd-card">
            <div style="display:flex; align-items:center; gap:8px; margin-bottom:4px;">
                <span style="font-size:18px; color:#3B82F6;">⚡</span>
                <div style="font-size: 15px; font-weight: 700; color: #FFFFFF;">Verification Speed</div>
            </div>
            <div style="font-size: 12px; color: #9CA3AF; margin-bottom: 14px;">Software Pipeline Execution Benchmark</div>

            <div class="cmd-readout-grid">
                <div class="cmd-readout-box">
                    <div class="cmd-readout-lbl">Avg Time</div>
                    <div class="cmd-readout-val val-emerald">{perf_summary['avg_time_ms_str']}</div>
                </div>
                <div class="cmd-readout-box">
                    <div class="cmd-readout-lbl">Min Time</div>
                    <div class="cmd-readout-val val-cyan">{perf_summary['min_time_ms_str']}</div>
                </div>
                <div class="cmd-readout-box">
                    <div class="cmd-readout-lbl">Total Attempts</div>
                    <div class="cmd-readout-val val-violet">{perf_summary['total_attempts']}</div>
                </div>
                <div class="cmd-readout-box">
                    <div class="cmd-readout-lbl">Total Time</div>
                    <div class="cmd-readout-val val-amber">{perf_summary['total_time_sec_str']}</div>
                </div>
            </div>
        </div>
    """), unsafe_allow_html=True)

    # --------------------------------------------------------
    # SECURITY METRICS CARD (CONTROLLED EVALUATION)
    # --------------------------------------------------------
    benchmark_data = attack_simulator.run_controlled_8state_evaluation(shots=shots_val)
    m = benchmark_data["metrics"]

    st.markdown(clean_html(f"""
        <div class="cmd-card">
            <div style="display:flex; align-items:center; gap:8px; margin-bottom:4px;">
                <span style="font-size:18px; color:#A855F7;">📈</span>
                <div style="font-size: 15px; font-weight: 700; color: #FFFFFF;">Security Metrics</div>
            </div>
            <div style="font-size: 12px; color: #9CA3AF; margin-bottom: 14px;">Performance indicators (Controlled Evaluation)</div>
            
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
    """), unsafe_allow_html=True)

    # --------------------------------------------------------
    # PROJECT NOTICE CARD
    # --------------------------------------------------------
    st.markdown(clean_html("""
        <div class="cmd-card" style="border-color:rgba(6,182,212,0.35);">
            <div style="display:flex; align-items:center; gap:8px; margin-bottom:8px;">
                <span style="font-size:18px; color:#06B6D4;">ℹ️</span>
                <div style="font-size: 13px; font-weight: 700; color: #06B6D4;">Project Notice</div>
            </div>
            <div style="font-size: 12px; color: #9CA3AF; line-height: 1.5;">
                This is an Educational / Research Prototype for SIH 2026. Detection results depend on the selected quantum state, measurement basis, attack model, and statistical threshold.
            </div>
        </div>
    """), unsafe_allow_html=True)

    # --------------------------------------------------------
    # SECTION 11: CONSOLIDATED SECURITY ANALYSIS & ATTACK SUMMARY
    # --------------------------------------------------------
    sec_analysis_data = attack_simulator.run_security_analysis(shots=shots_val)
    attack_summary_list = sec_analysis_data["attack_summary"]
    metrics_summary_data = sec_analysis_data["metrics_summary"]

    sec_table_rows_html = ""
    for sec_item in attack_summary_list:
        dec_col = "#EF4444" if "THREAT" in sec_item["decision"] else ("#F59E0B" if "BLOCKED" in sec_item["decision"] else "#10B981")
        sec_table_rows_html += f"""
            <tr style="border-bottom: 1px solid rgba(139, 92, 246, 0.15); color: #E5E7EB;">
                <td style="padding: 8px; font-weight: 700; color: #3B82F6;">{sec_item['attack']}</td>
                <td style="padding: 8px; color: #9CA3AF;">{sec_item['mechanism']}</td>
                <td style="padding: 8px; font-weight: 700; color: {dec_col};">{sec_item['decision']}</td>
                <td style="padding: 8px; font-weight: 600; color: #10B981;">{sec_item['controlled_result']}</td>
            </tr>
        """

    st.markdown(clean_html(f"""
        <div class="cmd-card" style="margin-top: 16px;">
            <div style="font-size: 15px; font-weight: 700; color: #FFFFFF; margin-bottom: 2px; display:flex; align-items:center; gap:8px;">
                <span style="width:24px; height:24px; border-radius:50%; background:#8B5CF6; color:#FFF; display:inline-flex; align-items:center; justify-content:center; font-size:12px; font-weight:800;">11</span>
                Consolidated Security Analysis & Attack-Wise Summary
            </div>
            <div style="font-size: 13px; color: #9CA3AF; margin-bottom: 16px;">
                Comprehensive attack classification matrix and multi-layered verification decision flow. (Controlled Prototype Evaluation)
            </div>

            <!-- Security Decision Flow -->
            <div style="background: linear-gradient(135deg, rgba(24, 20, 50, 0.9) 0%, rgba(15, 22, 41, 0.9) 100%); border: 1px solid rgba(139, 92, 246, 0.3); border-radius: 14px; padding: 14px 18px; margin-bottom: 16px;">
                <div style="font-size: 11px; font-weight: 700; color: #C4B5FD; text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 10px;">
                    🛡️ Multi-Layer Security Decision Architecture
                </div>
                <div style="display:flex; flex-wrap:wrap; gap:8px; align-items:center; justify-content:space-between;">
                    <div style="background:rgba(59,130,246,0.15); border:1px solid rgba(59,130,246,0.3); border-radius:8px; padding:8px 12px; text-align:center; flex:1; min-width:120px;">
                        <div style="font-size:9px; color:#9CA3AF; font-weight:600;">STEP 1</div>
                        <div style="font-size:11px; font-weight:700; color:#3B82F6;">Incoming Request</div>
                    </div>
                    <div style="color:#6B7280; font-weight:800;">→</div>
                    <div style="background:rgba(245,158,11,0.15); border:1px solid rgba(245,158,11,0.3); border-radius:8px; padding:8px 12px; text-align:center; flex:1; min-width:120px;">
                        <div style="font-size:9px; color:#9CA3AF; font-weight:600;">STEP 2</div>
                        <div style="font-size:11px; font-weight:700; color:#F59E0B;">Authorization Check</div>
                    </div>
                    <div style="color:#6B7280; font-weight:800;">→</div>
                    <div style="background:rgba(168,85,247,0.15); border:1px solid rgba(168,85,247,0.3); border-radius:8px; padding:8px 12px; text-align:center; flex:1; min-width:120px;">
                        <div style="font-size:9px; color:#9CA3AF; font-weight:600;">STEP 3</div>
                        <div style="font-size:11px; font-weight:700; color:#A855F7;">Quantum Verification</div>
                    </div>
                    <div style="color:#6B7280; font-weight:800;">→</div>
                    <div style="background:rgba(6,182,212,0.15); border:1px solid rgba(6,182,212,0.3); border-radius:8px; padding:8px 12px; text-align:center; flex:1; min-width:120px;">
                        <div style="font-size:9px; color:#9CA3AF; font-weight:600;">STEP 4</div>
                        <div style="font-size:11px; font-weight:700; color:#06B6D4;">Statistical Engine</div>
                    </div>
                    <div style="color:#6B7280; font-weight:800;">→</div>
                    <div style="background:rgba(16,185,129,0.15); border:1px solid rgba(16,185,129,0.3); border-radius:8px; padding:8px 12px; text-align:center; flex:1; min-width:120px;">
                        <div style="font-size:9px; color:#9CA3AF; font-weight:600;">STEP 5</div>
                        <div style="font-size:11px; font-weight:700; color:#10B981;">Decision: VALID / THREAT</div>
                    </div>
                </div>
            </div>

            <!-- Attack Summary Table -->
            <div style="background: #0B0F1F; border: 1px solid rgba(139, 92, 246, 0.25); border-radius: 12px; padding: 14px 16px; margin-bottom: 16px;">
                <div style="font-size: 12px; font-weight: 700; color: #C4B5FD; text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 10px; display:flex; align-items:center; gap:6px;">
                    <span>🔒</span> Consolidated Attack-Wise Security Analysis Matrix
                </div>
                <div style="overflow-x:auto;">
                    <table style="width: 100%; border-collapse: collapse; font-size: 12px; text-align: left;">
                        <thead>
                            <tr style="border-bottom: 1px solid rgba(139, 92, 246, 0.3); color: #9CA3AF;">
                                <th style="padding: 6px 8px;">Attack Vector</th>
                                <th style="padding: 6px 8px;">Detection Mechanism</th>
                                <th style="padding: 6px 8px;">Decision</th>
                                <th style="padding: 6px 8px;">Controlled Result</th>
                            </tr>
                        </thead>
                        <tbody>
                            {sec_table_rows_html}
                        </tbody>
                    </table>
                </div>
            </div>

            <!-- Readout Grid for Consolidated Metrics -->
            <div style="font-size: 11px; font-weight: 700; color: #9CA3AF; text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 6px;">
                📈 Consolidated Empirical Indicators (Controlled Prototype Evaluation)
            </div>
            <div class="cmd-readout-grid">
                <div class="cmd-readout-box">
                    <div class="cmd-readout-lbl">Overall TPR / Detection Rate</div>
                    <div class="cmd-readout-val val-emerald">{metrics_summary_data['TPR']:.2f}%</div>
                </div>
                <div class="cmd-readout-box">
                    <div class="cmd-readout-lbl">Overall TNR / Specificity</div>
                    <div class="cmd-readout-val val-violet">{metrics_summary_data['TNR']:.2f}%</div>
                </div>
                <div class="cmd-readout-box">
                    <div class="cmd-readout-lbl">Auth Detection Rate</div>
                    <div class="cmd-readout-val val-emerald">{metrics_summary_data['authorization_detection_rate_str']}</div>
                </div>
                <div class="cmd-readout-box">
                    <div class="cmd-readout-lbl">Full Pipeline Avg Speed</div>
                    <div class="cmd-readout-val val-cyan">{metrics_summary_data['full_pipeline_avg_ms_str']}</div>
                </div>
            </div>
        </div>
    """), unsafe_allow_html=True)

    # --------------------------------------------------------
    # SECTION 12: MATHEMATICAL VERIFICATION & SECURITY DECISION MODEL
    # --------------------------------------------------------
    math_model_data = attack_simulator.get_mathematical_security_model(
        state_name=state_option,
        basis=basis,
        attack_type=attack_option,
        shots=shots_val,
        error_threshold_pct=error_threshold_pct,
        chi_threshold=chi_threshold_val
    )
    math_params = math_model_data["parameters"]

    st.markdown(clean_html(f"""
        <div class="cmd-card" style="margin-top: 16px;">
            <div style="font-size: 15px; font-weight: 700; color: #FFFFFF; margin-bottom: 2px; display:flex; align-items:center; gap:8px;">
                <span style="width:24px; height:24px; border-radius:50%; background:#10B981; color:#FFF; display:inline-flex; align-items:center; justify-content:center; font-size:12px; font-weight:800;">12</span>
                Mathematical Verification & Security Decision Model
            </div>
            <div style="font-size: 13px; color: #9CA3AF; margin-bottom: 16px;">
                Formalized mathematical formulations for measurement error, simulation-based forgery probability, Chi-Square testing, and decision mapping. (Controlled Prototype Model)
            </div>

            <!-- Mathematical Formulation Grid -->
            <div style="display:grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap:12px; margin-bottom: 16px;">
                <div style="background:#0B0F1F; border:1px solid rgba(59,130,246,0.25); border-radius:12px; padding:14px;">
                    <div style="font-size:11px; font-weight:700; color:#93C5FD; text-transform:uppercase; margin-bottom:6px;">1. Error Rate Formulation</div>
                    <div style="font-size:13px; font-family:'JetBrains Mono', monospace; color:#3B82F6; margin-bottom:6px;">E = M / N &nbsp;|&nbsp; E% = (M / N) × 100</div>
                    <div style="font-size:11px; color:#9CA3AF; line-height:1.4;">Where N = total shots ({math_params['total_shots_N']}) and M = mismatched outcome counts ({math_params['mismatches_M']}).</div>
                </div>

                <div style="background:#0B0F1F; border:1px solid rgba(168,85,247,0.25); border-radius:12px; padding:14px;">
                    <div style="font-size:11px; font-weight:700; color:#C4B5FD; text-transform:uppercase; margin-bottom:6px;">2. Simulation-Based Forgery Probability</div>
                    <div style="font-size:13px; font-family:'JetBrains Mono', monospace; color:#A855F7; margin-bottom:6px;">P_f = M / N &nbsp;|&nbsp; P_f% = (M / N) × 100%</div>
                    <div style="font-size:11px; color:#9CA3AF; line-height:1.4;">Simulation-based probability estimate derived from observed measurement outcome deviation under attack.</div>
                </div>

                <div style="background:#0B0F1F; border:1px solid rgba(6,182,212,0.25); border-radius:12px; padding:14px;">
                    <div style="font-size:11px; font-weight:700; color:#67E8F9; text-transform:uppercase; margin-bottom:6px;">3. Chi-Square Test Statistic</div>
                    <div style="font-size:13px; font-family:'JetBrains Mono', monospace; color:#06B6D4; margin-bottom:6px;">χ² = Σ ((O_i - E_i)² / E_i)</div>
                    <div style="font-size:11px; color:#9CA3AF; line-height:1.4;">Compares observed counts O_i against theoretical expected counts E_i with safe zero-count handling.</div>
                </div>

                <div style="background:#0B0F1F; border:1px solid rgba(245,158,11,0.25); border-radius:12px; padding:14px;">
                    <div style="font-size:11px; font-weight:700; color:#FCD34D; text-transform:uppercase; margin-bottom:6px;">4. Threshold Security Decision Rule</div>
                    <div style="font-size:13px; font-family:'JetBrains Mono', monospace; color:#F59E0B; margin-bottom:6px;">THREAT = error_threat OR chi_threat</div>
                    <div style="font-size:11px; color:#9CA3AF; line-height:1.4;">Triggered when observed error % ({math_params['error_pct_str']}) > {math_params['error_threshold_pct']:.1f}% OR χ² ({math_params['chi_square_str']}) > {math_params['chi_threshold']:.1f}.</div>
                </div>
            </div>

            <!-- Mathematical Model Live Readout Card -->
            <div style="background: #0B0F1F; border: 1px solid rgba(16, 185, 129, 0.3); border-radius: 12px; padding: 14px 16px;">
                <div style="font-size: 12px; font-weight: 700; color: #10B981; text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 10px; display:flex; align-items:center; gap:6px;">
                    <span>⚡</span> Mathematical Model Live Evaluation (Current State: {math_params['state']} in {math_params['basis']}-Basis)
                </div>
                <div class="cmd-readout-grid">
                    <div class="cmd-readout-box">
                        <div class="cmd-readout-lbl">Total Shots (N)</div>
                        <div class="cmd-readout-val val-violet">{math_params['total_shots_N']}</div>
                    </div>
                    <div class="cmd-readout-box">
                        <div class="cmd-readout-lbl">Mismatches (M)</div>
                        <div class="cmd-readout-val val-cyan">{math_params['mismatches_M']}</div>
                    </div>
                    <div class="cmd-readout-box">
                        <div class="cmd-readout-lbl">Observed Error (E%)</div>
                        <div class="cmd-readout-val val-emerald">{math_params['error_pct_str']}</div>
                    </div>
                    <div class="cmd-readout-box">
                        <div class="cmd-readout-lbl">Chi-Square (χ²)</div>
                        <div class="cmd-readout-val val-amber">{math_params['chi_square_str']}</div>
                    </div>
                </div>
            </div>
        </div>
    """), unsafe_allow_html=True)

    # --------------------------------------------------------
    # SECTION 13: END-TO-END SECURITY VALIDATION & FINAL SYSTEM BENCHMARK
    # --------------------------------------------------------
    e2e_data = attack_simulator.run_end_to_end_validation(shots=shots_val)
    e2e_matrix = e2e_data["matrix"]
    e2e_metrics = e2e_data["metrics"]
    e2e_perf = e2e_data["performance_reference"]
    e2e_sec = e2e_data["security_metrics_reference"]

    e2e_rows_html = ""
    for row in e2e_matrix:
        exp_col = "#10B981" if row["expected_decision"] == "VALID" else ("#EF4444" if row["expected_decision"] == "THREAT" else "#F59E0B")
        act_col = "#10B981" if row["actual_decision"] == "VALID" else ("#EF4444" if row["actual_decision"] == "THREAT" else "#F59E0B")
        status_col = "#10B981" if row["status"] == "PASS" else "#EF4444"

        e2e_rows_html += f"""
            <tr style="border-bottom: 1px solid rgba(59, 130, 246, 0.15); color: #E5E7EB;">
                <td style="padding: 8px; font-weight: 700; color: #93C5FD;">S{row['scenario_id']}: {row['scenario_name']}</td>
                <td style="padding: 8px; color: #A855F7; font-weight: 600;">{row['path']}</td>
                <td style="padding: 8px; font-weight: 700; color: {exp_col};">{row['expected_decision']}</td>
                <td style="padding: 8px; font-weight: 700; color: {act_col};">{row['actual_decision']}</td>
                <td style="padding: 8px; font-weight: 800; color: {status_col};">{row['status']}</td>
            </tr>
        """

    st.markdown(clean_html(f"""
        <div class="cmd-card" style="margin-top: 16px;">
            <div style="font-size: 15px; font-weight: 700; color: #FFFFFF; margin-bottom: 2px; display:flex; align-items:center; gap:8px;">
                <span style="width:24px; height:24px; border-radius:50%; background:#06B6D4; color:#FFF; display:inline-flex; align-items:center; justify-content:center; font-size:12px; font-weight:800;">13</span>
                End-to-End Security Validation & Final System Benchmark
            </div>
            <div style="font-size: 13px; color: #9CA3AF; margin-bottom: 16px;">
                Complete integrated verification pipeline validation across 6 controlled benchmark scenarios. (Controlled Prototype Evaluation)
            </div>

            <!-- Complete System Architecture Flow -->
            <div style="background: linear-gradient(135deg, rgba(15, 29, 45, 0.9) 0%, rgba(10, 18, 32, 0.9) 100%); border: 1px solid rgba(6, 182, 212, 0.35); border-radius: 14px; padding: 14px 18px; margin-bottom: 16px;">
                <div style="font-size: 11px; font-weight: 700; color: #67E8F9; text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 10px;">
                    🔄 Complete End-to-End Security Verification Pipeline
                </div>
                <div class="cmd-flow-row" style="flex-wrap: wrap; gap: 6px;">
                    <div class="cmd-flow-box"><div style="font-size:9px; color:#9CA3AF;">INP</div><div style="font-size:10px; font-weight:700; color:#3B82F6;">User Input</div></div>
                    <div class="cmd-flow-arrow">→</div>
                    <div class="cmd-flow-box"><div style="font-size:9px; color:#9CA3AF;">SIG</div><div style="font-size:10px; font-weight:700; color:#A855F7;">Signature Layer</div></div>
                    <div class="cmd-flow-arrow">→</div>
                    <div class="cmd-flow-box"><div style="font-size:9px; color:#9CA3AF;">AUTH</div><div style="font-size:10px; font-weight:700; color:#F59E0B;">Authorization</div></div>
                    <div class="cmd-flow-arrow">→</div>
                    <div class="cmd-flow-box"><div style="font-size:9px; color:#9CA3AF;">Q-VER</div><div style="font-size:10px; font-weight:700; color:#10B981;">Quantum Prep</div></div>
                    <div class="cmd-flow-arrow">→</div>
                    <div class="cmd-flow-box"><div style="font-size:9px; color:#9CA3AF;">MEAS</div><div style="font-size:10px; font-weight:700; color:#06B6D4;">Measurement</div></div>
                    <div class="cmd-flow-arrow">→</div>
                    <div class="cmd-flow-box"><div style="font-size:9px; color:#9CA3AF;">STAT</div><div style="font-size:10px; font-weight:700; color:#EC4899;">Chi-Square Engine</div></div>
                    <div class="cmd-flow-arrow">→</div>
                    <div class="cmd-flow-box"><div style="font-size:9px; color:#9CA3AF;">VERDICT</div><div style="font-size:10px; font-weight:700; color:#10B981;">Final Security Result</div></div>
                </div>
            </div>

            <!-- 6-Scenario Validation Table -->
            <div style="background: #0B0F1F; border: 1px solid rgba(6, 182, 212, 0.25); border-radius: 12px; padding: 14px 16px; margin-bottom: 16px;">
                <div style="font-size: 12px; font-weight: 700; color: #67E8F9; text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 10px; display:flex; align-items:center; gap:6px;">
                    <span>📊</span> 6-Scenario End-to-End Controlled Validation Matrix
                </div>
                <div style="overflow-x:auto;">
                    <table style="width: 100%; border-collapse: collapse; font-size: 12px; text-align: left;">
                        <thead>
                            <tr style="border-bottom: 1px solid rgba(6, 182, 212, 0.3); color: #9CA3AF;">
                                <th style="padding: 6px 8px;">Benchmark Scenario</th>
                                <th style="padding: 6px 8px;">Pipeline Path</th>
                                <th style="padding: 6px 8px;">Expected Decision</th>
                                <th style="padding: 6px 8px;">Actual Decision</th>
                                <th style="padding: 6px 8px;">Status</th>
                            </tr>
                        </thead>
                        <tbody>
                            {e2e_rows_html}
                        </tbody>
                    </table>
                </div>
            </div>

            <!-- Validation & Benchmark Readout Grid -->
            <div style="font-size: 11px; font-weight: 700; color: #9CA3AF; text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 6px;">
                ⚡ Final System Performance & Security Indicators
            </div>
            <div class="cmd-readout-grid" style="margin-bottom: 16px;">
                <div class="cmd-readout-box">
                    <div class="cmd-readout-lbl">Validation Rate</div>
                    <div class="cmd-readout-val val-emerald">{e2e_metrics['validation_rate_str']}</div>
                </div>
                <div class="cmd-readout-box">
                    <div class="cmd-readout-lbl">Scenarios Passed</div>
                    <div class="cmd-readout-val val-cyan">{e2e_metrics['passed_scenarios']} / {e2e_metrics['total_scenarios']}</div>
                </div>
                <div class="cmd-readout-box">
                    <div class="cmd-readout-lbl">Full Pipeline Avg Speed</div>
                    <div class="cmd-readout-val val-violet">{e2e_perf['full_pipeline_avg_ms_str']}</div>
                </div>
                <div class="cmd-readout-box">
                    <div class="cmd-readout-lbl">Auth Gateway Speed</div>
                    <div class="cmd-readout-val val-amber">{e2e_perf['auth_gateway_avg_ms_str']}</div>
                </div>
            </div>

            <!-- Scientific Limitation Notice Card -->
            <div style="background: rgba(6, 182, 212, 0.08); border: 1px solid rgba(6, 182, 212, 0.25); border-radius: 10px; padding: 10px 14px; font-size: 12px; color: #9CA3AF; line-height: 1.5;">
                <strong style="color:#67E8F9;">ℹ️ Scientific Scope Notice:</strong> {e2e_data['scientific_limitation']}
            </div>
        </div>
    """), unsafe_allow_html=True)


    # --------------------------------------------------------
    # SECTION 14 — RESEARCH & SECURITY EVALUATION
    # --------------------------------------------------------
    research_eval = attack_simulator.run_research_evaluation(shots=shots_val)
    sih_matrix = research_eval["sih_objective_matrix"]
    sol_coverage = research_eval["expected_solution_coverage"]
    exp_evidence = research_eval["experimental_evidence"]
    atk_matrix = research_eval["attack_coverage_matrix"]
    sec_arch = research_eval["security_model_architecture"]
    limitations = research_eval["research_gaps_and_limitations"]
    contributions = research_eval["prototype_contributions"]

    # Build HTML rows for SIH Objectives
    sih_rows_html = ""
    for r in sih_matrix:
        st_color = "#10B981" if "IMPLEMENTED" in r["status"] else "#A855F7"
        sih_rows_html += f"""
            <tr style="border-bottom: 1px solid rgba(139, 92, 246, 0.15); color: #E5E7EB;">
                <td style="padding: 7px 8px; font-weight: 700; color: #C4B5FD;">{r['objective']}</td>
                <td style="padding: 7px 8px; color: #9CA3AF;">{r['implementation']}</td>
                <td style="padding: 7px 8px; color: #67E8F9; font-weight: 600;">{r['evidence_metric']}</td>
                <td style="padding: 7px 8px; font-weight: 800; color: {st_color};">{r['status']}</td>
            </tr>
        """

    # Build HTML rows for Solution Coverage
    sol_rows_html = ""
    for r in sol_coverage:
        st_color = "#10B981" if "IMPLEMENTED" in r["status"] else "#A855F7"
        sol_rows_html += f"""
            <tr style="border-bottom: 1px solid rgba(236, 72, 153, 0.15); color: #E5E7EB;">
                <td style="padding: 7px 8px; font-weight: 700; color: #F472B6;">{r['component']}</td>
                <td style="padding: 7px 8px; color: #9CA3AF;">{r['implementation']}</td>
                <td style="padding: 7px 8px; font-weight: 800; color: {st_color};">{r['status']}</td>
            </tr>
        """

    # Build HTML rows for Attack Coverage Matrix
    atk_rows_html = ""
    for r in atk_matrix:
        dec_col = "#EF4444" if r["decision"] == "THREAT" else ("#F59E0B" if r["decision"] == "BLOCKED" else "#10B981")
        atk_rows_html += f"""
            <tr style="border-bottom: 1px solid rgba(59, 130, 246, 0.15); color: #E5E7EB;">
                <td style="padding: 7px 8px; font-weight: 700; color: #93C5FD;">{r['attack']}</td>
                <td style="padding: 7px 8px; color: #A855F7;">{r['detection_layer']}</td>
                <td style="padding: 7px 8px; font-weight: 800; color: {dec_col};">{r['decision']}</td>
                <td style="padding: 7px 8px; color: #67E8F9; font-size: 11px;">{r['controlled_evidence']}</td>
            </tr>
        """

    # Build Limitations list HTML
    limits_html = "".join([f"<li style='margin-bottom: 4px; color: #D1D5DB;'>{lim}</li>" for lim in limitations])
    
    # Build Contributions list HTML
    contribs_html = "".join([f"<li style='margin-bottom: 4px; color: #D1D5DB;'>{c}</li>" for c in contributions])

    st.markdown(clean_html(f"""
        <div class="cmd-card" style="margin-top: 16px;">
            <div style="font-size: 15px; font-weight: 700; color: #FFFFFF; margin-bottom: 2px; display:flex; align-items:center; gap:8px;">
                <span style="width:24px; height:24px; border-radius:50%; background:#8B5CF6; color:#FFF; display:inline-flex; align-items:center; justify-content:center; font-size:12px; font-weight:800;">14</span>
                Research & Security Evaluation
            </div>
            <div style="font-size: 13px; color: #9CA3AF; margin-bottom: 16px;">
                Formal evidence-based mapping of prototype capabilities against SIH26141 problem statement objectives.
            </div>

            <!-- A. SIH Objective Coverage Matrix -->
            <div style="background: #0B0F1F; border: 1px solid rgba(139, 92, 246, 0.3); border-radius: 12px; padding: 14px 16px; margin-bottom: 16px;">
                <div style="font-size: 12px; font-weight: 700; color: #C4B5FD; text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 10px; display:flex; align-items:center; gap:6px;">
                    <span>📋</span> A. SIH Problem Statement Objective Coverage Matrix
                </div>
                <div style="overflow-x:auto;">
                    <table style="width: 100%; border-collapse: collapse; font-size: 11px; text-align: left;">
                        <thead>
                            <tr style="border-bottom: 1px solid rgba(139, 92, 246, 0.4); color: #9CA3AF;">
                                <th style="padding: 6px 8px;">SIH Objective</th>
                                <th style="padding: 6px 8px;">Existing Implementation</th>
                                <th style="padding: 6px 8px;">Evidence / Metric</th>
                                <th style="padding: 6px 8px;">Status</th>
                            </tr>
                        </thead>
                        <tbody>
                            {sih_rows_html}
                        </tbody>
                    </table>
                </div>
            </div>

            <!-- B. Expected Solution Coverage Matrix -->
            <div style="background: #0B0F1F; border: 1px solid rgba(236, 72, 153, 0.3); border-radius: 12px; padding: 14px 16px; margin-bottom: 16px;">
                <div style="font-size: 12px; font-weight: 700; color: #F472B6; text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 10px; display:flex; align-items:center; gap:6px;">
                    <span>🧬</span> B. Expected Solution Component Coverage Matrix
                </div>
                <div style="overflow-x:auto;">
                    <table style="width: 100%; border-collapse: collapse; font-size: 11px; text-align: left;">
                        <thead>
                            <tr style="border-bottom: 1px solid rgba(236, 72, 153, 0.4); color: #9CA3AF;">
                                <th style="padding: 6px 8px;">Expected Solution Component</th>
                                <th style="padding: 6px 8px;">Implementation Details</th>
                                <th style="padding: 6px 8px;">Status</th>
                            </tr>
                        </thead>
                        <tbody>
                            {sol_rows_html}
                        </tbody>
                    </table>
                </div>
            </div>

            <!-- C. Experimental Evidence Summary Readout -->
            <div style="background: linear-gradient(135deg, rgba(17, 24, 46, 0.9) 0%, rgba(15, 23, 42, 0.9) 100%); border: 1px solid rgba(6, 182, 212, 0.35); border-radius: 12px; padding: 14px 16px; margin-bottom: 16px;">
                <div style="font-size: 12px; font-weight: 700; color: #67E8F9; text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 10px;">
                    📊 C. Experimental Evidence Summary
                </div>
                <div style="font-size: 12px; color: #E5E7EB; line-height: 1.8;">
                    <div>• <strong>Controlled 8-Case Benchmark:</strong> {exp_evidence['controlled_8case_benchmark']}</div>
                    <div>• <strong>Authorization Test:</strong> {exp_evidence['authorization_test']}</div>
                    <div>• <strong>Controlled Noise Experiment:</strong> {exp_evidence['controlled_noise_experiment']}</div>
                    <div>• <strong>Controlled End-to-End Validation Rate:</strong> {exp_evidence['controlled_end_to_end_validation_rate']}</div>
                    <div>• <strong>Controlled Software-Simulation Runtime:</strong> {exp_evidence['controlled_software_simulation_runtime']}</div>
                </div>
            </div>

            <!-- D. Attack Coverage Matrix -->
            <div style="background: #0B0F1F; border: 1px solid rgba(59, 130, 246, 0.3); border-radius: 12px; padding: 14px 16px; margin-bottom: 16px;">
                <div style="font-size: 12px; font-weight: 700; color: #93C5FD; text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 10px; display:flex; align-items:center; gap:6px;">
                    <span>🛡️</span> D. Attack Coverage Matrix
                </div>
                <div style="overflow-x:auto;">
                    <table style="width: 100%; border-collapse: collapse; font-size: 11px; text-align: left;">
                        <thead>
                            <tr style="border-bottom: 1px solid rgba(59, 130, 246, 0.4); color: #9CA3AF;">
                                <th style="padding: 6px 8px;">Attack Category</th>
                                <th style="padding: 6px 8px;">Detection Layer</th>
                                <th style="padding: 6px 8px;">Decision</th>
                                <th style="padding: 6px 8px;">Controlled Evidence</th>
                            </tr>
                        </thead>
                        <tbody>
                            {atk_rows_html}
                        </tbody>
                    </table>
                </div>
            </div>

            <!-- E. Security Architecture Flow Diagram -->
            <div style="background: rgba(15, 23, 42, 0.8); border: 1px solid rgba(168, 85, 247, 0.3); border-radius: 12px; padding: 14px 16px; margin-bottom: 16px;">
                <div style="font-size: 12px; font-weight: 700; color: #C4B5FD; text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 10px;">
                    📐 E. Implemented Threat Detection Security Architecture
                </div>
                <pre style="background: #0B0F1F; color: #A7F3D0; padding: 12px; border-radius: 8px; font-family: monospace; font-size: 11px; line-height: 1.4; border: 1px solid rgba(16, 185, 129, 0.2); overflow-x: auto;">{sec_arch}</pre>
                <div style="font-size: 11px; color: #9CA3AF; margin-top: 6px; font-style: italic;">
                    Note: The threat-detection layer consists of the integrated verification, measurement, identity, replay, authorization and statistical engine logic. Teleportation provides quantum state transfer simulation.
                </div>
            </div>

            <!-- F. Research Gap & Limitations + G. Prototype Contribution Summary -->
            <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 14px;">
                <div style="background: rgba(245, 158, 11, 0.06); border: 1px solid rgba(245, 158, 11, 0.3); border-radius: 12px; padding: 14px;">
                    <div style="font-size: 12px; font-weight: 700; color: #FBBF24; text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 8px;">
                        ⚠️ F. Research Gap & Prototype Limitations
                    </div>
                    <ul style="padding-left: 18px; margin: 0; font-size: 11px; line-height: 1.5;">
                        {limits_html}
                    </ul>
                </div>

                <div style="background: rgba(16, 185, 129, 0.06); border: 1px solid rgba(16, 185, 129, 0.3); border-radius: 12px; padding: 14px;">
                    <div style="font-size: 12px; font-weight: 700; color: #34D399; text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 8px;">
                        ✨ G. Prototype Contribution Summary
                    </div>
                    <ul style="padding-left: 18px; margin: 0; font-size: 11px; line-height: 1.5;">
                        {contribs_html}
                    </ul>
                </div>
            </div>

        </div>
    """), unsafe_allow_html=True)


    # --------------------------------------------------------
    # SECTION 15 — FINAL DEMONSTRATION & REPRODUCIBILITY
    # --------------------------------------------------------
    import importlib.metadata
    def get_mod_version(mod_name):
        try:
            return importlib.metadata.version(mod_name)
        except Exception:
            try:
                m = __import__(mod_name)
                return getattr(m, "__version__", "Available")
            except Exception:
                return "Not installed / unavailable"

    py_ver = f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
    qiskit_ver = get_mod_version("qiskit")
    streamlit_ver = get_mod_version("streamlit")
    numpy_ver = get_mod_version("numpy")
    scipy_ver = get_mod_version("scipy")

    st.markdown(clean_html(f"""
        <div class="cmd-card" style="margin-top: 16px;">
            <div style="font-size: 15px; font-weight: 700; color: #FFFFFF; margin-bottom: 2px; display:flex; align-items:center; gap:8px;">
                <span style="width:24px; height:24px; border-radius:50%; background:#10B981; color:#FFF; display:inline-flex; align-items:center; justify-content:center; font-size:12px; font-weight:800;">15</span>
                Final Demonstration & Reproducibility Package
            </div>
            <div style="font-size: 13px; color: #9CA3AF; margin-bottom: 16px;">
                Complete reproducible demonstration suite, dynamic environment audit, and automated validation status.
            </div>

            <!-- A. Environment Audit Grid -->
            <div style="background: #0B0F1F; border: 1px solid rgba(16, 185, 129, 0.3); border-radius: 12px; padding: 14px 16px; margin-bottom: 16px;">
                <div style="font-size: 12px; font-weight: 700; color: #A7F3D0; text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 10px; display:flex; align-items:center; gap:6px;">
                    <span>💻</span> A. Dynamic Prototype Environment Audit
                </div>
                <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(140px, 1fr)); gap: 10px; font-size: 12px;">
                    <div style="background: rgba(17, 24, 39, 0.7); padding: 8px 12px; border-radius: 8px; border: 1px solid rgba(16, 185, 129, 0.2);">
                        <div style="color: #9CA3AF; font-size: 10px;">PYTHON</div>
                        <div style="color: #67E8F9; font-weight: 700; font-size: 13px;">{py_ver}</div>
                    </div>
                    <div style="background: rgba(17, 24, 39, 0.7); padding: 8px 12px; border-radius: 8px; border: 1px solid rgba(16, 185, 129, 0.2);">
                        <div style="color: #9CA3AF; font-size: 10px;">QISKIT</div>
                        <div style="color: #C4B5FD; font-weight: 700; font-size: 13px;">{qiskit_ver}</div>
                    </div>
                    <div style="background: rgba(17, 24, 39, 0.7); padding: 8px 12px; border-radius: 8px; border: 1px solid rgba(16, 185, 129, 0.2);">
                        <div style="color: #9CA3AF; font-size: 10px;">STREAMLIT</div>
                        <div style="color: #F472B6; font-weight: 700; font-size: 13px;">{streamlit_ver}</div>
                    </div>
                    <div style="background: rgba(17, 24, 39, 0.7); padding: 8px 12px; border-radius: 8px; border: 1px solid rgba(16, 185, 129, 0.2);">
                        <div style="color: #9CA3AF; font-size: 10px;">NUMPY</div>
                        <div style="color: #FBBF24; font-weight: 700; font-size: 13px;">{numpy_ver}</div>
                    </div>
                    <div style="background: rgba(17, 24, 39, 0.7); padding: 8px 12px; border-radius: 8px; border: 1px solid rgba(16, 185, 129, 0.2);">
                        <div style="color: #9CA3AF; font-size: 10px;">SCIPY</div>
                        <div style="color: #34D399; font-weight: 700; font-size: 13px;">{scipy_ver}</div>
                    </div>
                </div>
            </div>

            <!-- B. Demonstration Flow Guide -->
            <div style="background: #0B0F1F; border: 1px solid rgba(59, 130, 246, 0.3); border-radius: 12px; padding: 14px 16px; margin-bottom: 16px;">
                <div style="font-size: 12px; font-weight: 700; color: #93C5FD; text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 10px; display:flex; align-items:center; gap:6px;">
                    <span>⚡</span> B. Final SIH Demonstration Presets
                </div>
                <div style="font-size: 12px; color: #D1D5DB; line-height: 1.6;">
                    Select any scenario from the <strong>⚡ FINAL SIH DEMO PRESETS</strong> dropdown in the left sidebar to pre-configure the prototype controls, then click <strong>▶ Run Security Verification</strong> to observe live threat detection results.
                </div>
            </div>

            <!-- C. Reproducibility Instructions -->
            <div style="background: rgba(15, 23, 42, 0.8); border: 1px solid rgba(139, 92, 246, 0.3); border-radius: 12px; padding: 14px 16px; margin-bottom: 16px;">
                <div style="font-size: 12px; font-weight: 700; color: #C4B5FD; text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 10px;">
                    🛠️ C. Reproducibility & Master Validation Commands
                </div>
                <div style="font-size: 11px; color: #9CA3AF; margin-bottom: 6px;">Execute in PowerShell / Command Prompt from project root directory:</div>
                <pre style="background: #0B0F1F; color: #38BDF8; padding: 10px; border-radius: 8px; font-family: monospace; font-size: 11px; margin: 0; border: 1px solid rgba(56, 189, 248, 0.2); overflow-x: auto;">
# 1. Activate virtual environment
.venv\Scripts\Activate.ps1

# 2. Check environment status
.venv\Scripts\python.exe scratch/environment_check.py

# 3. Run Master Validation Suite (Tasks #1–#11 & Reproducibility)
.venv\Scripts\python.exe scratch/run_all_validation.py

# 4. Run Task #12 Reproducibility Verification
.venv\Scripts\python.exe scratch/test_task12_reproducibility.py
</pre>
            </div>

            <!-- D. Scientific Scope Statement -->
            <div style="background: rgba(6, 182, 212, 0.08); border: 1px solid rgba(6, 182, 212, 0.25); border-radius: 10px; padding: 10px 14px; font-size: 12px; color: #9CA3AF; line-height: 1.5;">
                <strong style="color:#67E8F9;">ℹ️ Scientific Scope Notice:</strong> This project is a quantum-inspired cybersecurity prototype evaluated through controlled software simulation. Results demonstrate statistical threat detection across simulated state preparation and measurement logic.
            </div>
        </div>
    """), unsafe_allow_html=True)





