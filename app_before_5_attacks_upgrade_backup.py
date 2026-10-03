import streamlit as st
from qds_attack_simulator import QDSAttackSimulator

if "attack_simulator" not in st.session_state:
    st.session_state.attack_simulator = QDSAttackSimulator()

attack_simulator = st.session_state.attack_simulator
from qiskit import QuantumCircuit
from qiskit.quantum_info import Statevector
from qiskit.primitives import StatevectorSampler


# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="Quantum Digital Signature Security",
    page_icon="âš›ï¸",
    layout="wide",
    initial_sidebar_state="expanded"
)


# ============================================================
# CUSTOM CSS
# ============================================================

st.markdown("""
<style>

.block-container {
    padding-top: 2rem;
    padding-bottom: 2rem;
}

.hero {
    padding: 32px;
    border-radius: 20px;
    background: linear-gradient(135deg, #111827, #1e3a8a);
    color: white;
    margin-bottom: 25px;
}

.hero h1 {
    font-size: 38px;
    margin-bottom: 8px;
}

.hero p {
    font-size: 17px;
    color: #dbeafe;
}

.section-card {
    padding: 20px;
    border-radius: 15px;
    background: white;
    border: 1px solid #e5e7eb;
    margin-bottom: 15px;
}

.success-box {
    padding: 18px;
    border-radius: 12px;
    background: #ecfdf5;
    border: 1px solid #10b981;
    color: #065f46;
    font-size: 18px;
    font-weight: 600;
}

.danger-box {
    padding: 18px;
    border-radius: 12px;
    background: #fef2f2;
    border: 1px solid #ef4444;
    color: #991b1b;
    font-size: 18px;
    font-weight: 600;
}

.info-box {
    padding: 18px;
    border-radius: 12px;
    background: #eff6ff;
    border: 1px solid #3b82f6;
    color: #1e40af;
}

.flow-box {
    padding: 18px;
    border-radius: 12px;
    background: #f8fafc;
    border: 1px solid #cbd5e1;
    text-align: center;
    font-size: 16px;
    font-weight: 600;
}

.footer {
    text-align: center;
    color: #64748b;
    padding: 20px;
}

    
/* FORCE SIDEBAR INPUT TEXT VISIBILITY */
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
</style>
""", unsafe_allow_html=True)


# ============================================================
# QUANTUM STATE CREATION
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


# ============================================================
# BASIS SELECTION
# ============================================================

def get_basis(state_name):

    if state_name in ["0", "1"]:
        return "Z"

    return "X"


# ============================================================
# APPLY ATTACK
# ============================================================

def apply_attack(state, attack):

    attack_circuit = QuantumCircuit(1)

    if attack == "X":
        attack_circuit.x(0)

    elif attack == "Z":
        attack_circuit.z(0)

    return state.evolve(attack_circuit)


# ============================================================
# MEASURE QUANTUM STATE
# ============================================================

def measure_state(state, basis, shots):

    qc = QuantumCircuit(1, 1)

    qc.initialize(state.data, 0)

    if basis == "X":
        qc.h(0)

    qc.measure(0, 0)

    sampler = StatevectorSampler()

    result = sampler.run(
        [qc],
        shots=shots
    ).result()

    return result[0].data.c.get_counts()


# ============================================================
# EXPECTED DISTRIBUTION
# ============================================================

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


# ============================================================
# CHI-SQUARE
# ============================================================

def calculate_chi_square(observed, expected_probabilities, shots):

    chi = 0.0

    for bit in ["0", "1"]:

        expected = expected_probabilities[bit] * shots
        observed_value = observed.get(bit, 0)

        if expected > 0:

            chi += (
                (observed_value - expected) ** 2
            ) / expected

    return chi


# ============================================================
# ERROR RATE
# ============================================================

def calculate_error_rate(original, received):

    total = sum(received.values())

    if total == 0:
        return 0.0

    difference = 0

    for bit in ["0", "1"]:

        difference += abs(
            original.get(bit, 0)
            - received.get(bit, 0)
        )

    return difference / (2 * total)


# ============================================================
# TELEPORTATION-INSPIRED CIRCUIT
# ============================================================

def create_teleportation_circuit(state_name):

    qc = QuantumCircuit(3)

    # --------------------------------------------------------
    # Original quantum state on q0
    # --------------------------------------------------------

    if state_name == "1":
        qc.x(0)

    elif state_name == "+":
        qc.h(0)

    elif state_name == "-":
        qc.x(0)
        qc.h(0)

    # --------------------------------------------------------
    # Bell pair preparation
    # --------------------------------------------------------

    qc.h(1)
    qc.cx(1, 2)

    # --------------------------------------------------------
    # Alice Bell-state operations
    # --------------------------------------------------------

    qc.cx(0, 1)
    qc.h(0)

    # --------------------------------------------------------
    # Coherent quantum corrections
    # --------------------------------------------------------

    qc.cx(1, 2)
    qc.cz(0, 2)

    return qc


# ============================================================
# STATE DISPLAY
# ============================================================

def display_state(state_name):

    return f"|{state_name}âŸ©"


# ============================================================

# ============================================================
# POLISHED SIH DASHBOARD UI
# ============================================================

# ---------- Premium visual theme ----------
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

.section-title {
    color: #ffffff;
    font-size: 25px;
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
    min-height: 145px;
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

.attack-none { border-top: 3px solid var(--green); }
.attack-x { border-top: 3px solid var(--yellow); }
.attack-z { border-top: 3px solid var(--red); }

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

.metric-panel {
    background: #0c1b2b;
    border: 1px solid var(--border);
    border-radius: 16px;
    padding: 8px 14px;
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

@media (max-width: 800px) {
    .pipeline { flex-direction: column; }
    .pipe-arrow { transform: rotate(90deg); }
    .hero { padding: 25px; }
}
    
/* FORCE SIDEBAR INPUT TEXT VISIBILITY */
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
</style>
""", unsafe_allow_html=True)


# ---------- Sidebar ----------
st.sidebar.markdown("## âš™ï¸ Security Configuration")
st.sidebar.caption("Configure the quantum signature and attack scenario.")

message = st.sidebar.text_input(
    "Digital Message",
    value="SIH Quantum Digital Signature"
)

state_name = st.sidebar.selectbox(
    "Quantum Signature State",
    ["0", "1", "+", "-"],
    format_func=lambda x: f"|{x}âŸ©"
)

attack = st.sidebar.selectbox(
    "Attack Simulation",
    [
        "NONE",
        "FORGERY",
        "IMPERSONATION",
        "REPLAY",
        "CHANNEL"
    ],
    format_func=lambda x: {
        "NONE": "Genuine - No Attack",
        "FORGERY": "Forgery Attack",
        "IMPERSONATION": "Impersonation Attack",
        "REPLAY": "Replay Attack",
        "CHANNEL": "Channel Manipulation"
    }.get(x, x)
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
    "ðŸš€  Run Security Verification",
    use_container_width=True,
    type="primary"
)

# ---------- Hero ----------
st.markdown("""
<div class="hero">
    <div class="hero-kicker">SIH 2026 â€¢ Quantum Cybersecurity Research Prototype</div>
    <h1>âš›ï¸ Quantum Digital Signature Security</h1>
    <div class="hero-sub">
        Quantum-Inspired Cyber Threat Detection for Digital Signature Security
    </div>
    <span class="badge">QDS-Inspired</span>
    <span class="badge">Qiskit</span>
    <span class="badge">Teleportation</span>
    <span class="badge">Statistical Detection</span>
</div>
""", unsafe_allow_html=True)


def section_heading(title, subtitle=""):
    st.markdown(f'<div class="section-title">{title}</div>', unsafe_allow_html=True)
    if subtitle:
        st.markdown(f'<div class="section-subtitle">{subtitle}</div>', unsafe_allow_html=True)


# ---------- Home ----------
if not run_button:
    st.markdown("""
    <div class="card" style="min-height:auto;">
        <h3>ðŸ” Quantum Security Verification Center</h3>
        <p>
        Configure a quantum signature state and an optional attack from the
        sidebar, then run the verification engine to inspect quantum
        measurements, statistical deviation, and threat status.
        </p>
    </div>
    """, unsafe_allow_html=True)

    section_heading(
        "âš›ï¸ Core Security Modules",
        "Three layers combine to create the SIH demonstration workflow."
    )

    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown("""
        <div class="card">
            <h3>âš›ï¸ Quantum Signature</h3>
            <p>Generate a quantum-state-based signature using computational and superposition states.</p>
        </div>
        """, unsafe_allow_html=True)
    with c2:
        st.markdown("""
        <div class="card">
            <h3>ðŸ”— Quantum Transmission</h3>
            <p>Demonstrate a three-qubit teleportation-inspired transmission circuit.</p>
        </div>
        """, unsafe_allow_html=True)
    with c3:
        st.markdown("""
        <div class="card">
            <h3>ðŸ›¡ï¸ Threat Detection</h3>
            <p>Detect Forgery, Impersonation, Replay, and Channel Manipulation attacks using quantum and statistical verification.</p>
        </div>
        """, unsafe_allow_html=True)

    section_heading("âš›ï¸ Supported Quantum States", "States used by the prototype verifier.")

    s1, s2, s3, s4 = st.columns(4)
    states = [
        (s1, "0", "Computational basis"),
        (s2, "1", "Computational basis"),
        (s3, "+", "Superposition"),
        (s4, "-", "Superposition"),
    ]
    for col, symbol, desc in states:
        with col:
            st.markdown(
                f'<div class="card state-card"><div class="state-symbol">|{symbol}âŸ©</div>'
                f'<div class="state-label">{desc}</div></div>',
                unsafe_allow_html=True
            )

    section_heading("ðŸ›¡ï¸ Supported Attack Models", "Four attack scenarios are supported by the prototype.")

    a1, a2, a3 = st.columns(3)
    attack_cards = [
        (a1, "attack-none", "NONE", "Genuine signature without an injected attack."),
        (a2, "attack-x", "Pauli-X", "Bit-flip operation that can alter computational-basis states."),
        (a3, "attack-z", "Pauli-Z", "Phase-flip operation that can alter X-basis states."),
    ]
    for col, cls, title, desc in attack_cards:
        with col:
            st.markdown(
                f'<div class="card {cls}"><h3>{title}</h3><p>{desc}</p></div>',
                unsafe_allow_html=True
            )

    section_heading("ðŸ”„ Detection Pipeline", "From signature generation to statistical verification.")
    st.markdown("""
    <div class="pipeline">
        <div class="pipe">1<br>Signature<br>Generation</div>
        <div class="pipe-arrow">â€º</div>
        <div class="pipe">2<br>Basis<br>Selection</div>
        <div class="pipe-arrow">â€º</div>
        <div class="pipe">3<br>Quantum<br>Transmission</div>
        <div class="pipe-arrow">â€º</div>
        <div class="pipe">4<br>Attack<br>Detection</div>
        <div class="pipe-arrow">â€º</div>
        <div class="pipe">5<br>Statistical<br>Verification</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="notice">
        <b>Prototype scope:</b> This dashboard demonstrates a QDS-inspired
        research workflow. It is not a production-ready Quantum Digital
        Signature protocol and does not provide a real-world security guarantee.
    </div>
    """, unsafe_allow_html=True)


# ---------- Security Verification ----------
if run_button:
    original_state = create_state(state_name)
    basis = get_basis(state_name)

    # Attack simulation
    attack_result = None
    received_state = original_state
    identity_threat = False
    replay_threat = False

    if attack == "NONE":
        received_state = original_state

    elif attack == "FORGERY":
        attack_result = attack_simulator.simulate_forgery_attack(state_name)
        received_state = create_state(attack_result["received_state"])

    elif attack == "IMPERSONATION":
        attack_result = attack_simulator.simulate_impersonation_attack("Alice")
        identity_threat = attack_result["detected"]
        received_state = original_state

    elif attack == "REPLAY":
        signature_id = f"{message}:{state_name}"
        attack_result = attack_simulator.simulate_replay_attack(message, signature_id)
        replay_threat = attack_result["detected"]
        received_state = original_state

    elif attack == "CHANNEL":
        manipulation = "Z" if basis == "X" else "X"
        attack_result = attack_simulator.simulate_channel_manipulation(
            state_name, manipulation
        )
        received_state = create_state(attack_result["received_state"])

    # Quantum measurement
    original_counts = measure_state(original_state, basis, shots)
    received_counts = measure_state(received_state, basis, shots)

    expected = expected_distribution(original_state, basis)
    chi = calculate_chi_square(received_counts, expected, shots)
    error_rate = calculate_error_rate(original_counts, received_counts)

    threshold = 10
    statistical_threat = chi > threshold

    threat_detected = (
        statistical_threat
        or identity_threat
        or replay_threat
    )

    if attack == "NONE":
        signature_valid = not statistical_threat
    elif attack == "IMPERSONATION":
        signature_valid = False
    elif attack == "REPLAY":
        signature_valid = not replay_threat
    else:
        signature_valid = not threat_detected

    # ---------- Result ----------
    section_heading("ðŸ” Security Verification Result")

    if threat_detected:
        st.markdown("""
        <div class="result-threat">
            <div class="result-title">ðŸš¨ THREAT DETECTED</div>
            <div class="result-detail">
                Measurement statistics indicate a significant deviation from
                the expected quantum signature distribution.
            </div>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div class="result-safe">
            <div class="result-title">âœ… NO THREAT DETECTED</div>
            <div class="result-detail">
                The observed distribution remains within the configured
                statistical threshold for this prototype test.
            </div>
        </div>
        """, unsafe_allow_html=True)

    st.write("")

    m1, m2, m3, m4 = st.columns(4)
    with m1:
        st.metric("Quantum State", display_state(state_name))
    with m2:
        st.metric("Verification Basis", f"{basis}-Basis")
    with m3:
        st.metric("Attack Scenario", attack)
    with m4:
        st.metric("Chi-Square", f"{chi:.2f}")

    # ---------- Signature ----------
    section_heading("ðŸ“ Digital Signature", "Quantum-state signature generation and verification.")

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
            st.success("SIGNATURE STATUS: VALID")
        else:
            st.error("SIGNATURE STATUS: FORGED / THREAT")
        st.write(f"**Statistical Threshold:** {threshold}")
        st.write(f"**Measured Copies:** {shots}")
        st.markdown("</div>", unsafe_allow_html=True)

    # ---------- Measurement ----------
    section_heading("ðŸ“Š Quantum Measurement Analysis",
                    "Observed distributions for the original and received quantum states.")

    c1, c2 = st.columns(2)
    with c1:
        st.markdown("### Original Signature")
        st.json(original_counts)
        st.bar_chart({"Count": {
            "0": original_counts.get("0", 0),
            "1": original_counts.get("1", 0)
        }})
        st.caption(f"Total measurements: {sum(original_counts.values())}")

    with c2:
        st.markdown("### Received Signature")
        st.json(received_counts)
        st.bar_chart({"Count": {
            "0": received_counts.get("0", 0),
            "1": received_counts.get("1", 0)
        }})
        st.caption(f"Total measurements: {sum(received_counts.values())}")

    # ---------- Statistics ----------
    section_heading("ðŸ“ˆ Statistical Threat Analysis",
                    "Chi-square deviation and measurement error are used as the prototype detection signals.")

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.metric("Chi-Square", f"{chi:.2f}")
    with c2:
        st.metric("Threshold", f"{threshold:.2f}")
    with c3:
        st.metric("Error Rate", f"{error_rate * 100:.2f}%")
    with c4:
        st.metric("Decision", "THREAT" if threat_detected else "NORMAL")

    if threat_detected:
        st.warning(
            "The received measurement distribution differs significantly "
            "from the expected signature distribution."
        )
    else:
        st.info(
            "The received measurement distribution is within the configured "
            "security threshold."
        )

    # ---------- Teleportation ----------
    section_heading("ðŸ”— Quantum Teleportation Layer",
                    "Three-qubit teleportation-inspired transmission used as the quantum communication layer.")

    teleport_circuit = create_teleportation_circuit(state_name)

    st.markdown('<div class="code-panel">', unsafe_allow_html=True)
    st.code(str(teleport_circuit), language="text")
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("""
    <div class="pipeline">
        <div class="pipe">Unknown<br>Quantum State</div>
        <div class="pipe-arrow">â€º</div>
        <div class="pipe">Bell Pair<br>Preparation</div>
        <div class="pipe-arrow">â€º</div>
        <div class="pipe">Alice Bell-State<br>Operations</div>
        <div class="pipe-arrow">â€º</div>
        <div class="pipe">Coherent Quantum<br>Corrections</div>
        <div class="pipe-arrow">â€º</div>
        <div class="pipe">Bob's<br>Qubit</div>
    </div>
    """, unsafe_allow_html=True)

    st.caption(
        "Implementation note: the prototype uses coherent quantum corrections "
        "for compatibility with the installed Qiskit workflow; this display "
        "does not claim a classical-measurement implementation."
    )

    # ---------- Attack analysis ----------
    section_heading("ðŸ›¡ï¸ Attack Analysis", "Interpretation of the selected threat scenario.")

    if attack == "NONE":
        st.success(
            "Genuine scenario: no attack was injected. The received state "
            "represents the genuine signature."
        )
    elif attack == "X":
        st.warning(
            "Pauli-X attack injected: the X gate acts as a quantum bit-flip. "
            "Its visibility depends on the verification basis and state."
        )
    else:
        st.warning(
            "Pauli-Z attack injected: the Z gate introduces a phase flip. "
            "For superposition states, the X basis can reveal this disturbance."
        )

    # ---------- Security logic ----------
    section_heading("ðŸ§  Security Detection Logic")

    steps = [
        ("01", "Generate", "Create the quantum-state signature."),
        ("02", "Select", "Choose the corresponding verification basis."),
        ("03", "Transmit", "Process the state through the teleportation-inspired layer."),
        ("04", "Attack", "Inject an optional Pauli-X or Pauli-Z attack."),
        ("05", "Measure", "Measure multiple copies of the received state."),
        ("06", "Compare", "Compare observed and expected distributions."),
        ("07", "Score", "Calculate statistical deviation using chi-square."),
        ("08", "Decide", "Deviation above threshold â†’ threat detected."),
    ]

    for row_start in range(0, len(steps), 4):
        cols = st.columns(4)
        for col, (num, title, desc) in zip(cols, steps[row_start:row_start + 4]):
            with col:
                st.markdown(
                    f'<div class="card" style="min-height:145px;">'
                    f'<div style="color:#35d9ff;font-weight:900;font-size:12px;">STEP {num}</div>'
                    f'<h3 style="margin-top:6px;">{title}</h3>'
                    f'<p>{desc}</p></div>',
                    unsafe_allow_html=True
                )

    # ---------- Prototype evaluation ----------
    section_heading("ðŸ“‹ Prototype Evaluation",
                    "Controlled evaluation used to demonstrate the detection workflow.")

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.metric("Genuine Cases", "4")
    with c2:
        st.metric("Attack Cases", "4")
    with c3:
        st.metric("Attacks Detected", "4 / 4")
    with c4:
        st.metric("False Alarms", "0")

    st.markdown("""
    <div class="notice">
        <b>Controlled prototype result:</b> Detection Rate / TPR = 100%.
        This is based only on the 8 controlled test cases used in the prototype
        and must not be interpreted as real-world attack-detection accuracy.
    </div>
    """, unsafe_allow_html=True)

    st.info(
        "âš ï¸ Prototype Notice: This is a quantum-inspired / QDS-inspired "
        "research prototype for SIH demonstration. It is not a production-ready "
        "Quantum Digital Signature protocol and does not provide a real-world "
        "security guarantee."
    )


# ---------- Footer ----------
st.markdown("---")
st.markdown("""
<div class="footer">
    <b>SIH 2026</b> â€¢ Quantum-Inspired Cyber Threat Detection for Digital Signature Security
    <br><br>
    Qiskit â€¢ Python â€¢ Streamlit
</div>
""", unsafe_allow_html=True)










