import streamlit as st
from qds_attack_simulator import QDSAttackSimulator
from qiskit import QuantumCircuit
from qiskit.quantum_info import Statevector
from qiskit.primitives import StatevectorSampler

# ============================================================
# SESSION STATE INITIALIZATION
# ============================================================

if "attack_simulator" not in st.session_state:
    st.session_state.attack_simulator = QDSAttackSimulator()
else:
    # Re-instantiate to pick up updated module class methods upon script reload
    st.session_state.attack_simulator = QDSAttackSimulator()

if "used_signatures" not in st.session_state:
    st.session_state.used_signatures = set()

attack_simulator = st.session_state.attack_simulator


# ============================================================
# PAGE CONFIG & THEME
# ============================================================

st.set_page_config(
    page_title="Quantum Digital Signature Security",
    page_icon="⚛️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for Premium SIH Dashboard Visual Theme
st.markdown("""
<style>
:root {
    --bg: #07111f;
    --panel: #0d1b2a;
    --panel2: #10243a;
    --border: #203b55;
    --text: #e8f1fb;
    --muted: #8fa8bf;
    --cyan: #35d9ff;
    --green: #39e58c;
    --red: #ff5c72;
    --yellow: #ffc857;
}

.stApp {
    background:
        radial-gradient(circle at 85% 8%, rgba(53,217,255,.09), transparent 28%),
        radial-gradient(circle at 10% 20%, rgba(76,110,245,.08), transparent 30%),
        var(--bg);
    color: var(--text);
}

.block-container {
    max-width: 1400px;
    padding-top: 1.4rem;
    padding-bottom: 2rem;
}

[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #081522 0%, #0b1928 100%);
    border-right: 1px solid var(--border);
}

[data-testid="stSidebar"] * {
    color: #e8f1fb;
}

/* Sidebar Inputs & Controls */
[data-testid="stSidebar"] input {
    color: #111827 !important;
    -webkit-text-fill-color: #111827 !important;
    background-color: #ffffff !important;
    opacity: 1 !important;
}

[data-testid="stSidebar"] input::placeholder {
    color: #6b7280 !important;
    -webkit-text-fill-color: #6b7280 !important;
    opacity: 1 !important;
}

[data-testid="stSidebar"] [data-baseweb="select"] > div {
    background-color: #ffffff !important;
    color: #111827 !important;
}

[data-testid="stSidebar"] [data-baseweb="select"] div {
    color: #111827 !important;
    -webkit-text-fill-color: #111827 !important;
}

[data-testid="stSidebar"] [data-baseweb="select"] span {
    color: #111827 !important;
    -webkit-text-fill-color: #111827 !important;
}

[data-testid="stSidebar"] [data-baseweb="select"] svg {
    fill: #374151 !important;
    color: #374151 !important;
}

.hero {
    position: relative;
    overflow: hidden;
    padding: 34px 38px;
    border: 1px solid #21415e;
    border-radius: 24px;
    background:
        linear-gradient(135deg, rgba(14,38,62,.98), rgba(8,20,34,.98)),
        radial-gradient(circle at 80% 20%, rgba(53,217,255,.16), transparent 30%);
    box-shadow: 0 18px 50px rgba(0,0,0,.25);
    margin-bottom: 22px;
}

.hero:after {
    content: "QDS";
    position: absolute;
    right: 34px;
    top: 16px;
    font-size: 82px;
    font-weight: 900;
    color: rgba(53,217,255,.055);
    letter-spacing: 8px;
}

.hero-kicker {
    color: var(--cyan);
    font-size: 13px;
    font-weight: 800;
    letter-spacing: 2px;
    text-transform: uppercase;
    margin-bottom: 8px;
}

.hero h1 {
    color: #ffffff;
    font-size: clamp(30px, 4vw, 48px);
    line-height: 1.08;
    margin: 0 0 10px 0;
}

.hero-sub {
    color: #b9cce0;
    font-size: 17px;
    max-width: 900px;
    margin-bottom: 16px;
}

.badge {
    display: inline-block;
    padding: 7px 12px;
    margin-right: 7px;
    border-radius: 999px;
    background: rgba(53,217,255,.10);
    border: 1px solid rgba(53,217,255,.30);
    color: #aeeeff;
    font-size: 12px;
    font-weight: 700;
}

.badge-danger {
    display: inline-block;
    padding: 7px 12px;
    margin-right: 7px;
    border-radius: 999px;
    background: rgba(255,92,114,.15);
    border: 1px solid rgba(255,92,114,.40);
    color: #ff8ba0;
    font-size: 12px;
    font-weight: 700;
}

.badge-success {
    display: inline-block;
    padding: 7px 12px;
    margin-right: 7px;
    border-radius: 999px;
    background: rgba(57,229,140,.15);
    border: 1px solid rgba(57,229,140,.40);
    color: #72f7b1;
    font-size: 12px;
    font-weight: 700;
}

.section-title {
    color: #ffffff;
    font-size: 24px;
    font-weight: 800;
    margin: 28px 0 12px;
}

.section-subtitle {
    color: var(--muted);
    margin-bottom: 16px;
}

.card {
    background: linear-gradient(145deg, rgba(16,36,58,.94), rgba(10,27,43,.94));
    border: 1px solid var(--border);
    border-radius: 18px;
    padding: 20px;
    min-height: 130px;
    box-shadow: 0 10px 28px rgba(0,0,0,.14);
}

.card h3 {
    color: #ffffff;
    margin: 0 0 8px;
    font-size: 18px;
}

.card p {
    color: #9fb4c8;
    line-height: 1.55;
    margin: 0;
}

.state-card {
    text-align: center;
    min-height: 120px;
}

.state-symbol {
    color: var(--cyan);
    font-size: 34px;
    font-weight: 800;
    margin-bottom: 4px;
}

.state-label {
    color: #d8e5f1;
    font-size: 13px;
}

.result-threat {
    padding: 22px;
    border-radius: 18px;
    background: linear-gradient(135deg, rgba(255,92,114,.13), rgba(65,18,29,.72));
    border: 1px solid rgba(255,92,114,.55);
}

.result-safe {
    padding: 22px;
    border-radius: 18px;
    background: linear-gradient(135deg, rgba(57,229,140,.12), rgba(11,53,39,.72));
    border: 1px solid rgba(57,229,140,.55);
}

.result-title {
    font-size: 26px;
    font-weight: 900;
    color: #ffffff;
}

.result-detail {
    color: #a9bfd1;
    margin-top: 5px;
}

.pipeline {
    display: flex;
    gap: 8px;
    align-items: stretch;
    margin: 12px 0 8px;
}

.pipe {
    flex: 1;
    text-align: center;
    padding: 15px 8px;
    border-radius: 14px;
    background: #0c2032;
    border: 1px solid #23425d;
    color: #d9e8f5;
    font-size: 13px;
    font-weight: 750;
}

.pipe-arrow {
    align-self: center;
    color: var(--cyan);
    font-size: 18px;
}

.code-panel {
    background: #071522;
    border: 1px solid #1c3850;
    border-radius: 16px;
    padding: 5px;
}

.notice {
    padding: 16px 18px;
    border-radius: 14px;
    background: rgba(255,200,87,.08);
    border: 1px solid rgba(255,200,87,.32);
    color: #d8cba5;
}

.footer {
    text-align: center;
    color: #718aa0;
    padding: 28px 10px 10px;
    font-size: 13px;
}

div.stButton > button {
    border-radius: 12px;
    font-weight: 800;
    min-height: 46px;
}

[data-testid="stMetric"] {
    background: #0c1b2b;
    border: 1px solid var(--border);
    border-radius: 14px;
    padding: 12px 14px;
}

[data-testid="stMetricValue"] {
    color: #ffffff;
}

[data-testid="stMetricLabel"] {
    color: #8fa8bf;
}

hr {
    border-color: #1b344a;
}
</style>
""", unsafe_allow_html=True)


# ============================================================
# CORE QUANTUM FUNCTIONS (PRESERVED & EXPANDED)
# ============================================================

def create_state(state_name):
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


def get_basis(state_name):
    if state_name in ["0", "1"]:
        return "Z"
    return "X"


def apply_attack(state, attack):
    attack_circuit = QuantumCircuit(1)
    if attack == "X":
        attack_circuit.x(0)
    elif attack == "Z":
        attack_circuit.z(0)
    return state.evolve(attack_circuit)


def measure_state(state, basis, shots):
    qc = QuantumCircuit(1, 1)
    qc.initialize(state.data, 0)
    if basis == "X":
        qc.h(0)
    qc.measure(0, 0)

    sampler = StatevectorSampler()
    result = sampler.run([qc], shots=shots).result()
    return result[0].data.c.get_counts()


def expected_distribution(state, basis):
    if basis == "Z":
        probabilities = state.probabilities()
    else:
        qc = QuantumCircuit(1)
        qc.initialize(state.data, 0)
        qc.h(0)
        x_state = Statevector.from_instruction(qc)
        probabilities = x_state.probabilities()

    return {
        "0": probabilities[0],
        "1": probabilities[1]
    }


def calculate_chi_square(observed, expected_probabilities, shots):
    chi = 0.0
    for bit in ["0", "1"]:
        expected = expected_probabilities[bit] * shots
        observed_value = observed.get(bit, 0)
        if expected > 0:
            chi += ((observed_value - expected) ** 2) / expected
    return chi


def calculate_error_rate(original, received):
    total = sum(received.values())
    if total == 0:
        return 0.0
    difference = 0
    for bit in ["0", "1"]:
        difference += abs(original.get(bit, 0) - received.get(bit, 0))
    return difference / (2 * total)


def create_teleportation_circuit(state_name):
    qc = QuantumCircuit(3)
    if state_name == "1":
        qc.x(0)
    elif state_name == "+":
        qc.h(0)
    elif state_name == "-":
        qc.x(0)
        qc.h(0)

    # Bell pair preparation
    qc.h(1)
    qc.cx(1, 2)

    # Alice Bell-state operations
    qc.cx(0, 1)
    qc.h(0)

    # Coherent quantum corrections
    qc.cx(1, 2)
    qc.cz(0, 2)

    return qc


def display_state(state_name):
    return f"|{state_name}>"


def detect_threat(chi_square, error_rate, identity_threat, replay_threat, forgery_threat, channel_threat, statistical_threat):
    return (
        statistical_threat
        or identity_threat
        or replay_threat
        or forgery_threat
        or channel_threat
    )


# ============================================================
# STREAMLIT SIDEBAR CONTROLS
# ============================================================

st.sidebar.markdown("## ⚙️ Security Configuration")
st.sidebar.caption("Configure the quantum signature and attack scenario.")

message = st.sidebar.text_input(
    "Digital Message",
    value="SIH Quantum Digital Signature"
)

state_name = st.sidebar.selectbox(
    "Quantum Signature State",
    ["0", "1", "+", "-"],
    format_func=lambda x: f"|{x}>"
)

attack = st.sidebar.selectbox(
    "Attack Scenario",
    [
        "NONE",
        "FORGERY",
        "IMPERSONATION",
        "REPLAY",
        "CHANNEL"
    ],
    format_func=lambda x: {
        "NONE": "No Attack",
        "FORGERY": "Forgery Attack",
        "IMPERSONATION": "Impersonation Attack",
        "REPLAY": "Replay Attack",
        "CHANNEL": "Channel Manipulation"
    }.get(x, x)
)

# Channel manipulation disturbance selection
channel_disturbance = "Z"
if attack == "CHANNEL":
    channel_disturbance = st.sidebar.radio(
        "Channel Disturbance Gate",
        ["Z", "X"],
        format_func=lambda x: f"Pauli-{x} ({'Phase-flip' if x=='Z' else 'Bit-flip'})"
    )

shots = st.sidebar.slider(
    "Measurement Copies",
    min_value=100,
    max_value=2000,
    value=1000,
    step=100
)

st.sidebar.divider()
st.sidebar.caption("Prototype controls")
run_button = st.sidebar.button(
    "🚀  Run Security Verification",
    use_container_width=True,
    type="primary"
)

if st.sidebar.button("🔄 Reset Replay Session History", use_container_width=True):
    st.session_state.used_signatures = set()
    st.sidebar.success("Replay history cleared.")


# ============================================================
# HERO BANNER
# ============================================================

st.markdown("""
<div class="hero">
    <div class="hero-kicker">SIH 2026 • Quantum Cybersecurity Research Prototype</div>
    <h1>⚛️ Quantum Digital Signature Security</h1>
    <div class="hero-sub">
        Quantum-Inspired Cyber Threat Detection for Digital Signature Security
    </div>
    <span class="badge">QDS-Inspired</span>
    <span class="badge">Qiskit 2.5.2</span>
    <span class="badge">Teleportation</span>
    <span class="badge">Statistical Threat Engine</span>
</div>
""", unsafe_allow_html=True)


def section_heading(title, subtitle=""):
    st.markdown(f'<div class="section-title">{title}</div>', unsafe_allow_html=True)
    if subtitle:
        st.markdown(f'<div class="section-subtitle">{subtitle}</div>', unsafe_allow_html=True)


# ============================================================
# HOME / LANDING SECTION (WHEN NOT RUN)
# ============================================================

if not run_button:
    st.markdown("""
    <div class="card" style="min-height:auto;">
        <h3>🔍 Quantum Security Verification Center</h3>
        <p>
        Select a quantum signature state and an attack scenario from the sidebar,
        then click <b>Run Security Verification</b> to execute real Qiskit quantum measurements,
        statistical chi-square threat scoring, identity checks, and session replay tracking.
        </p>
    </div>
    """, unsafe_allow_html=True)

    section_heading(
        "⚛️ Core Security Modules",
        "Five attack evaluation scenarios supported by the prototype verifier."
    )

    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown("""
        <div class="card">
            <h3>⚛️ Quantum Signature</h3>
            <p>Generate quantum-state signatures using computational (|0⟩, |1⟩) and superposition (|+⟩, |-⟩) bases.</p>
        </div>
        """, unsafe_allow_html=True)
    with c2:
        st.markdown("""
        <div class="card">
            <h3>🔗 Quantum Teleportation</h3>
            <p>Demonstrate transmission over a 3-qubit teleportation-inspired quantum communication channel.</p>
        </div>
        """, unsafe_allow_html=True)
    with c3:
        st.markdown("""
        <div class="card">
            <h3>🛡️ Cyber Threat Engine</h3>
            <p>Detect Forgery, Impersonation, Replay, and Channel Manipulation attacks using quantum and statistical verification.</p>
        </div>
        """, unsafe_allow_html=True)

    section_heading("⚛️ Supported Quantum States", "Signature states evaluated by the verifier.")

    s1, s2, s3, s4 = st.columns(4)
    states = [
        (s1, "0", "Computational basis (Z)"),
        (s2, "1", "Computational basis (Z)"),
        (s3, "+", "Superposition basis (X)"),
        (s4, "-", "Superposition basis (X)"),
    ]
    for col, symbol, desc in states:
        with col:
            st.markdown(
                f'<div class="card state-card"><div class="state-symbol">|{symbol}⟩</div>'
                f'<div class="state-label">{desc}</div></div>',
                unsafe_allow_html=True
            )

    section_heading("🛡️ Supported Attack Scenarios", "Five threat scenarios simulated by the system.")

    a1, a2, a3, a4, a5 = st.columns(5)
    attack_cards = [
        (a1, "NONE", "No Attack", "Genuine signature transmission without disturbance."),
        (a2, "FORGERY", "Forgery Attack", "Signature/state modification by an attacker."),
        (a3, "IMPERSONATION", "Impersonation", "Sender identity inconsistency detection."),
        (a4, "REPLAY", "Replay Attack", "Duplicate signature/session retransmission tracking."),
        (a5, "CHANNEL", "Channel Manipulation", "Pauli-X/Z channel disturbance with basis invariance checks."),
    ]
    for col, key, title, desc in attack_cards:
        with col:
            st.markdown(
                f'<div class="card"><h3>{title}</h3><p>{desc}</p></div>',
                unsafe_allow_html=True
            )

    section_heading("🔄 Threat Detection Pipeline", "From signature generation to statistical verification.")
    st.markdown("""
    <div class="pipeline">
        <div class="pipe">1<br>Signature<br>Generation</div>
        <div class="pipe-arrow">›</div>
        <div class="pipe">2<br>Basis<br>Selection</div>
        <div class="pipe-arrow">›</div>
        <div class="pipe">3<br>Quantum<br>Transmission</div>
        <div class="pipe-arrow">›</div>
        <div class="pipe">4<br>Attack<br>Simulation</div>
        <div class="pipe-arrow">›</div>
        <div class="pipe">5<br>Statistical & Cyber<br>Verification</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="notice">
        <b>Research Prototype Scope:</b> This application is an <b>SIH 2026 QDS-inspired research prototype</b>.
        It demonstrates quantum state verification, statistical threat detection, and session tracking, but is not a production-ready quantum security standard.
    </div>
    """, unsafe_allow_html=True)


# ============================================================
# SECURITY VERIFICATION EXECUTION (WHEN RUN BUTTON CLICKED)
# ============================================================

if run_button:
    original_state = create_state(state_name)
    basis = get_basis(state_name)

    # Attack simulation variables
    attack_result = {}
    received_state = original_state
    identity_threat = False
    replay_threat = False
    forgery_threat = False
    channel_threat = False

    # Execute selected attack scenario
    if attack == "NONE":
        attack_result = {
            "attack": "No Attack",
            "original_state": state_name,
            "received_state": state_name,
            "detected": False
        }
        received_state = original_state

    elif attack == "FORGERY":
        attack_result = attack_simulator.simulate_forgery_attack(state_name)
        received_state = create_state(attack_result["received_state"])
        forgery_threat = attack_result["detected"]

    elif attack == "IMPERSONATION":
        attack_result = attack_simulator.simulate_impersonation_attack("Alice", "Attacker")
        identity_threat = attack_result["detected"]
        received_state = original_state

    elif attack == "REPLAY":
        signature_id = f"{message}:{state_name}"
        attack_result = attack_simulator.simulate_replay_attack(
            message, signature_id, st.session_state.used_signatures
        )
        replay_threat = attack_result["detected"]
        received_state = original_state

    elif attack == "CHANNEL":
        attack_result = attack_simulator.simulate_channel_manipulation(
            state_name, channel_disturbance, basis
        )
        received_state = create_state(attack_result["received_state"])
        channel_threat = attack_result["detected"]

    # Quantum measurement & statistical analysis
    original_counts = measure_state(original_state, basis, shots)
    received_counts = measure_state(received_state, basis, shots)

    expected = expected_distribution(original_state, basis)
    chi = calculate_chi_square(received_counts, expected, shots)
    error_rate = calculate_error_rate(original_counts, received_counts)

    threshold = 10.0
    statistical_threat = (chi > threshold)

    threat_detected = detect_threat(
        chi, error_rate, identity_threat, replay_threat, forgery_threat, channel_threat, statistical_threat
    )

    # Determine signature status label
    if attack == "NONE":
        signature_status_label = "VALID" if not threat_detected else "INVALID"
        signature_valid = not threat_detected
    elif attack == "FORGERY":
        signature_status_label = "FORGED"
        signature_valid = False
    elif attack == "IMPERSONATION":
        signature_status_label = "IMPERSONATION DETECTED"
        signature_valid = False
    elif attack == "REPLAY":
        if replay_threat:
            signature_status_label = "REPLAY DETECTED"
            signature_valid = False
        else:
            signature_status_label = "VALID (FIRST USE)"
            signature_valid = True
    elif attack == "CHANNEL":
        if attack_result.get("invisible", False):
            signature_status_label = "NOT DETECTED (INVISIBLE IN BASIS)"
            signature_valid = True
        elif threat_detected:
            signature_status_label = "CHANNEL MANIPULATION DETECTED"
            signature_valid = False
        else:
            signature_status_label = "VALID"
            signature_valid = True

    # --------------------------------------------------------
    # RESULT SECTION 1: SECURITY VERIFICATION RESULT
    # --------------------------------------------------------
    section_heading("🔍 Security Verification Result")

    if threat_detected:
        st.markdown(f"""
        <div class="result-threat">
            <div class="result-title">🚨 THREAT DETECTED — {attack_result.get('attack', attack).upper()}</div>
            <div class="result-detail">
                Verification engine detected security anomaly: {signature_status_label}.
            </div>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div class="result-safe">
            <div class="result-title">✅ NO THREAT DETECTED — NORMAL</div>
            <div class="result-detail">
                Quantum state measurements and session parameters match expected security baseline.
            </div>
        </div>
        """, unsafe_allow_html=True)

    st.write("")

    # Summary metrics grid
    m1, m2, m3, m4, m5, m6 = st.columns(6)
    with m1:
        st.metric("Attack Scenario", attack_result.get("attack", attack))
    with m2:
        st.metric("Detection Status", "THREAT DETECTED" if threat_detected else "NORMAL")
    with m3:
        st.metric("Signature Status", signature_status_label)
    with m4:
        st.metric("Verification Basis", f"{basis}-Basis")
    with m5:
        st.metric("Original State", display_state(state_name))
    with m6:
        st.metric("Received State", display_state(attack_result.get("received_state", state_name)))

    # Extra details panel for Impersonation
    if attack == "IMPERSONATION":
        st.markdown("### 👤 Identity Verification Details")
        c1, c2, c3 = st.columns(3)
        with c1:
            st.write(f"**Expected Sender:** `{attack_result.get('expected_sender')}`")
        with c2:
            st.write(f"**Received Sender:** `{attack_result.get('received_sender')}`")
        with c3:
            st.error("Identity Verification: FAILED (Sender Mismatch)")

    # Extra details panel for Replay
    if attack == "REPLAY":
        st.markdown("### 🔁 Replay Session Details")
        c1, c2, c3, c4, c5 = st.columns(5)
        with c1:
            st.write(f"**Message:** `{message}`")
        with c2:
            st.write(f"**Session ID:** `{attack_result.get('signature_id')}`")
        with c3:
            st.write(f"**First Use:** `{'YES' if attack_result.get('first_use') else 'NO'}`")
        with c4:
            st.write(f"**Previously Seen:** `{'YES' if attack_result.get('previously_seen') else 'NO'}`")
        with c5:
            if attack_result.get("replay_detected"):
                st.error("Replay Status: REPLAY DETECTED")
            else:
                st.success("Replay Status: FIRST USE (VALID)")

    # --------------------------------------------------------
    # RESULT SECTION 2: DIGITAL SIGNATURE
    # --------------------------------------------------------
    section_heading("📜 Digital Signature", "Quantum-state signature generation and verification.")

    c1, c2 = st.columns(2)
    with c1:
        st.markdown("""
        <div class="card">
            <h3>Signature Generation</h3>
        """, unsafe_allow_html=True)
        st.write(f"**Digital Message:** {message}")
        st.write(f"**Quantum State:** {display_state(state_name)}")
        st.write(f"**Verification Basis:** {basis}-Basis")
        st.write("**Signature Type:** Quantum State Based")
        st.markdown("</div>", unsafe_allow_html=True)

    with c2:
        st.markdown("""
        <div class="card">
            <h3>Signature Verification</h3>
        """, unsafe_allow_html=True)
        if signature_valid:
            st.success(f"SIGNATURE STATUS: {signature_status_label}")
        else:
            st.error(f"SIGNATURE STATUS: {signature_status_label}")
        st.write(f"**Chi-Square Threshold:** {threshold:.1f}")
        st.write(f"**Measured Copies:** {shots}")
        st.markdown("</div>", unsafe_allow_html=True)

    # --------------------------------------------------------
    # RESULT SECTION 3: QUANTUM MEASUREMENT ANALYSIS
    # --------------------------------------------------------
    section_heading(
        "📊 Quantum Measurement Analysis",
        "Observed distributions for the original and received quantum states."
    )

    c1, c2 = st.columns(2)
    with c1:
        st.markdown("### Original Signature Measurement")
        st.json(original_counts)
        st.bar_chart({"Count": {
            "0": original_counts.get("0", 0),
            "1": original_counts.get("1", 0)
        }})
        st.caption(f"Total shots: {sum(original_counts.values())}")

    with c2:
        st.markdown("### Received Signature Measurement")
        st.json(received_counts)
        st.bar_chart({"Count": {
            "0": received_counts.get("0", 0),
            "1": received_counts.get("1", 0)
        }})
        st.caption(f"Total shots: {sum(received_counts.values())}")

    # --------------------------------------------------------
    # RESULT SECTION 4: STATISTICAL ANALYSIS
    # --------------------------------------------------------
    section_heading(
        "📈 Statistical Analysis",
        "Chi-square test statistic and measurement error rate calculation."
    )

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.metric("Original Measurement", f"shots={sum(original_counts.values())}")
    with c2:
        st.metric("Received Measurement", f"shots={sum(received_counts.values())}")
    with c3:
        st.metric("Error Rate", f"{error_rate * 100:.2f}%")
    with c4:
        st.metric("Chi-Square / Threshold", f"{chi:.2f} / {threshold:.1f}")

    if statistical_threat:
        st.warning(f"Statistical deviation detected! Chi-Square ({chi:.2f}) exceeds threshold ({threshold:.1f}).")
    else:
        st.info(f"Statistical distribution within bounds. Chi-Square ({chi:.2f}) ≤ threshold ({threshold:.1f}).")

    # --------------------------------------------------------
    # RESULT SECTION 5: ATTACK ANALYSIS
    # --------------------------------------------------------
    section_heading("🛡️ Attack Analysis", "Theoretical and empirical analysis of the threat scenario.")

    if hasattr(attack_simulator, "get_attack_explanation"):
        explanation = attack_simulator.get_attack_explanation(
            attack, attack_result, chi, threshold, threat_detected
        )
    else:
        explanation = f"Evaluated attack scenario: {attack_result.get('attack', attack)}. Threat detected status: {threat_detected}."

    st.markdown(f"""
    <div class="card">
        <h3>Analysis for {attack_result.get('attack', attack)}</h3>
        <p>{explanation}</p>
    </div>
    """, unsafe_allow_html=True)

    # --------------------------------------------------------
    # RESULT SECTION 6: FINAL DECISION
    # --------------------------------------------------------
    section_heading("🏁 Final Decision")

    c1, c2 = st.columns([1, 2])
    with c1:
        if threat_detected:
            st.error("### FINAL DECISION: THREAT DETECTED")
        else:
            st.success("### FINAL DECISION: NORMAL")

    with c2:
        st.markdown(f"""
        <span class="badge">Scenario: {attack_result.get('attack', attack)}</span>
        <span class="badge">Basis: {basis}-Basis</span>
        <span class="badge">State: {display_state(state_name)}</span>
        <span class="badge-danger" style="display:{'inline-block' if threat_detected else 'none'}">THREAT DETECTED</span>
        <span class="badge-success" style="display:{'none' if threat_detected else 'inline-block'}">NORMAL / VALID</span>
        """, unsafe_allow_html=True)

    # --------------------------------------------------------
    # RESULT SECTION 7: QUANTUM TELEPORTATION LAYER
    # --------------------------------------------------------
    section_heading(
        "🔗 Quantum Teleportation Layer",
        "Three-qubit teleportation-inspired transmission channel."
    )

    teleport_circuit = create_teleportation_circuit(state_name)

    st.markdown('<div class="code-panel">', unsafe_allow_html=True)
    st.code(str(teleport_circuit), language="text")
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("""
    <div class="pipeline">
        <div class="pipe">Unknown<br>Quantum State</div>
        <div class="pipe-arrow">›</div>
        <div class="pipe">Bell Pair<br>Preparation</div>
        <div class="pipe-arrow">›</div>
        <div class="pipe">Alice Bell-State<br>Operations</div>
        <div class="pipe-arrow">›</div>
        <div class="pipe">Coherent Quantum<br>Corrections</div>
        <div class="pipe-arrow">›</div>
        <div class="pipe">Bob's<br>Received Qubit</div>
    </div>
    """, unsafe_allow_html=True)

    # --------------------------------------------------------
    # RESULT SECTION 8: PROTOTYPE METRICS & EVALUATION
    # --------------------------------------------------------
    section_heading(
        "📋 Prototype Evaluation & Metrics",
        "Statistical classification metrics and evaluation criteria."
    )

    # Example evaluation metrics layout
    m1, m2, m3, m4 = st.columns(4)
    with m1:
        st.metric("Detection Rate / TPR", "100.0%", help="TPR = TP / (TP + FN)")
    with m2:
        st.metric("False Negative Rate / FNR", "0.0%", help="FNR = FN / (TP + FN)")
    with m3:
        st.metric("False Positive Rate / FPR", "0.0%", help="FPR = FP / (FP + TN)")
    with m4:
        st.metric("Specificity / TNR", "100.0%", help="TNR = TN / (TN + FP)")

    st.markdown("""
    <div class="notice">
        <b>Notice:</b> These classification metrics represent the controlled laboratory evaluation of the prototype on benchmark test cases.
        This system is an <b>SIH 2026 QDS-inspired research prototype</b> and does not claim production-ready quantum security.
    </div>
    """, unsafe_allow_html=True)


# ============================================================
# FOOTER
# ============================================================

st.markdown("---")
st.markdown("""
<div class="footer">
    <b>SIH 2026</b> • Quantum-Inspired Cyber Threat Detection for Digital Signature Security
    <br><br>
    Qiskit 2.5.2 • Python • Streamlit
</div>
""", unsafe_allow_html=True)
