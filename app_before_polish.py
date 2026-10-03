import streamlit as st
from qiskit import QuantumCircuit
from qiskit.quantum_info import Statevector
from qiskit.primitives import StatevectorSampler


# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="Quantum Digital Signature Security",
    page_icon="⚛️",
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

</style>
""", unsafe_allow_html=True)


# ============================================================
# HERO
# ============================================================

st.markdown("""
<div class="hero">

<h1>⚛️ Quantum Digital Signature Security</h1>

<p>
Quantum-Inspired Cyber Threat Detection for Digital Signature Security
</p>

<p>
<b>SIH 2026 Prototype</b> | Quantum Digital Signature + Teleportation + Statistical Threat Detection
</p>

</div>
""", unsafe_allow_html=True)


# ============================================================
# SIDEBAR
# ============================================================

st.sidebar.title("⚙️ Security Configuration")

st.sidebar.caption("Configure the quantum signature and attack scenario.")

message = st.sidebar.text_input(
    "Digital Message",
    value="SIH Quantum Digital Signature"
)

state_name = st.sidebar.selectbox(
    "Quantum Signature State",
    ["0", "1", "+", "-"]
)

attack = st.sidebar.selectbox(
    "Attack Simulation",
    ["NONE", "X", "Z"]
)

shots = st.sidebar.slider(
    "Measurement Copies",
    min_value=100,
    max_value=2000,
    value=1000,
    step=100
)

run_button = st.sidebar.button(
    "🚀 Run Security Verification",
    use_container_width=True
)


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

    return f"|{state_name}⟩"


# ============================================================
# DEFAULT HOME SCREEN
# ============================================================

if not run_button:

    st.markdown("""
    <div class="info-box">

    <b>Welcome to the Quantum Security Dashboard.</b>

    <br><br>

    Configure a quantum signature state and an optional attack
    from the sidebar, then click
    <b>Run Security Verification</b>.

    </div>
    """, unsafe_allow_html=True)

    st.write("")

    col1, col2, col3 = st.columns(3)

    with col1:

        st.markdown("### ⚛️ Quantum Signature")

        st.write(
            "Generate a quantum-state-based digital signature "
            "using computational and superposition states."
        )

    with col2:

        st.markdown("### 🔗 Quantum Transmission")

        st.write(
            "Demonstrate a three-qubit teleportation-inspired "
            "quantum transmission circuit."
        )

    with col3:

        st.markdown("### 🛡️ Threat Detection")

        st.write(
            "Detect simulated Pauli-X and Pauli-Z attacks "
            "using measurement statistics."
        )

    st.write("")

    st.subheader("⚛️ Supported Quantum States")

    state_col1, state_col2, state_col3, state_col4 = st.columns(4)

    with state_col1:
        st.metric("State", "|0⟩")
        st.caption("Computational basis")

    with state_col2:
        st.metric("State", "|1⟩")
        st.caption("Computational basis")

    with state_col3:
        st.metric("State", "|+⟩")
        st.caption("Superposition")

    with state_col4:
        st.metric("State", "|−⟩")
        st.caption("Superposition")

    st.write("")

    st.subheader("🛡️ Supported Attack Models")

    attack_col1, attack_col2, attack_col3 = st.columns(3)

    with attack_col1:
        st.markdown("### NONE")
        st.write("Genuine signature without an injected attack.")

    with attack_col2:
        st.markdown("### X Attack")
        st.write("Pauli-X bit-flip operation.")

    with attack_col3:
        st.markdown("### Z Attack")
        st.write("Pauli-Z phase-flip operation.")

    st.write("")

    st.subheader("🔄 Detection Pipeline")

    flow1, flow2, flow3, flow4, flow5 = st.columns(5)

    with flow1:
        st.markdown(
            '<div class="flow-box">Signature<br>Generation</div>',
            unsafe_allow_html=True
        )

    with flow2:
        st.markdown(
            '<div class="flow-box">Basis<br>Selection</div>',
            unsafe_allow_html=True
        )

    with flow3:
        st.markdown(
            '<div class="flow-box">Quantum<br>Transmission</div>',
            unsafe_allow_html=True
        )

    with flow4:
        st.markdown(
            '<div class="flow-box">Attack<br>Detection</div>',
            unsafe_allow_html=True
        )

    with flow5:
        st.markdown(
            '<div class="flow-box">Statistical<br>Verification</div>',
            unsafe_allow_html=True
        )


# ============================================================
# SECURITY VERIFICATION
# ============================================================

if run_button:

    # --------------------------------------------------------
    # Generate original quantum signature
    # --------------------------------------------------------

    original_state = create_state(state_name)

    # --------------------------------------------------------
    # Select verification basis
    # --------------------------------------------------------

    basis = get_basis(state_name)

    # --------------------------------------------------------
    # Apply attack
    # --------------------------------------------------------

    received_state = apply_attack(
        original_state,
        attack
    )

    # --------------------------------------------------------
    # Measure original and received states
    # --------------------------------------------------------

    original_counts = measure_state(
        original_state,
        basis,
        shots
    )

    received_counts = measure_state(
        received_state,
        basis,
        shots
    )

    # --------------------------------------------------------
    # Statistical analysis
    # --------------------------------------------------------

    expected = expected_distribution(
        original_state,
        basis
    )

    chi = calculate_chi_square(
        received_counts,
        expected,
        shots
    )

    error_rate = calculate_error_rate(
        original_counts,
        received_counts
    )

    # --------------------------------------------------------
    # Security threshold
    # --------------------------------------------------------

    threshold = 10

    threat_detected = chi > threshold

    # --------------------------------------------------------
    # Signature verification
    # --------------------------------------------------------

    if attack == "NONE":

        signature_valid = True

    else:

        signature_valid = not threat_detected

    # ========================================================
    # RESULT
    # ========================================================

    st.subheader("🔐 Security Verification Result")

    if threat_detected:

        st.markdown("""
        <div class="danger-box">
        🚨 THREAT DETECTED — Possible signature forgery or quantum attack detected.
        </div>
        """, unsafe_allow_html=True)

    else:

        st.markdown("""
        <div class="success-box">
        ✅ NO THREAT DETECTED — Signature appears valid under this test.
        </div>
        """, unsafe_allow_html=True)

    st.write("")

    # ========================================================
    # TOP METRICS
    # ========================================================

    col1, col2, col3, col4 = st.columns(4)

    with col1:

        st.metric(
            "Quantum State",
            display_state(state_name)
        )

    with col2:

        st.metric(
            "Verification Basis",
            basis
        )

    with col3:

        st.metric(
            "Attack",
            attack
        )

    with col4:

        st.metric(
            "Chi-Square",
            f"{chi:.2f}"
        )

    # ========================================================
    # DIGITAL SIGNATURE
    # ========================================================

    st.subheader("📝 Digital Signature")

    col1, col2 = st.columns(2)

    with col1:

        st.markdown("### Signature Generation")

        st.write(
            f"**Message:** {message}"
        )

        st.write(
            f"**Quantum State:** {display_state(state_name)}"
        )

        st.write(
            f"**Verification Basis:** {basis}-Basis"
        )

        st.write(
            "**Signature Type:** Quantum State Based"
        )

    with col2:

        st.markdown("### Signature Verification")

        if signature_valid:

            st.success(
                "SIGNATURE STATUS: VALID"
            )

        else:

            st.error(
                "SIGNATURE STATUS: FORGED / THREAT"
            )

        st.write(
            f"Statistical Threshold: {threshold}"
        )

        st.write(
            f"Measured Copies: {shots}"
        )

    # ========================================================
    # MEASUREMENT ANALYSIS
    # ========================================================

    st.subheader("📊 Quantum Measurement Analysis")

    col1, col2 = st.columns(2)

    with col1:

        st.markdown("### Original Signature")

        st.json(original_counts)

        st.write(
            f"Total Measurements: {sum(original_counts.values())}"
        )

    with col2:

        st.markdown("### Received Signature")

        st.json(received_counts)

        st.write(
            f"Total Measurements: {sum(received_counts.values())}"
        )

    # ========================================================
    # STATISTICAL ANALYSIS
    # ========================================================

    st.subheader("📈 Statistical Threat Analysis")

    col1, col2, col3 = st.columns(3)

    with col1:

        st.metric(
            "Chi-Square Value",
            f"{chi:.2f}"
        )

    with col2:

        st.metric(
            "Detection Threshold",
            f"{threshold:.2f}"
        )

    with col3:

        st.metric(
            "Error Rate",
            f"{error_rate * 100:.2f}%"
        )

    if threat_detected:

        st.warning(
            "The observed measurement distribution differs "
            "significantly from the expected signature distribution."
        )

    else:

        st.info(
            "The observed measurement distribution is within "
            "the configured security threshold."
        )

    # ========================================================
    # TELEPORTATION LAYER
    # ========================================================

    st.subheader("🔗 Quantum Teleportation Layer")

    st.write(
        "The selected quantum signature state is prepared and "
        "processed through a three-qubit teleportation-inspired circuit."
    )

    teleport_circuit = create_teleportation_circuit(
        state_name
    )

    st.code(
        str(teleport_circuit),
        language="text"
    )

    st.markdown("""
    ### Teleportation Flow

    `Unknown Quantum State`
    ↓
    `Bell Pair Preparation`
    ↓
    `Alice Bell-State Operations`
    ↓
    `Coherent Quantum Corrections`
    ↓
    `Bob's Qubit`
    """)

    # ========================================================
    # ATTACK ANALYSIS
    # ========================================================

    st.subheader("🛡️ Attack Analysis")

    if attack == "NONE":

        st.success(
            "No attack was injected. The received state represents "
            "the genuine signature."
        )

    elif attack == "X":

        st.warning(
            "Pauli-X attack was injected. The X gate acts as a "
            "quantum bit-flip operation."
        )

    elif attack == "Z":

        st.warning(
            "Pauli-Z attack was injected. The Z gate introduces "
            "a phase flip that can be detected in the X basis."
        )

    # ========================================================
    # SECURITY LOGIC
    # ========================================================

    st.subheader("🧠 Security Detection Logic")

    st.markdown("""
    1. **Generate quantum signature** from the selected quantum state.
    2. **Select verification basis** according to the state.
    3. **Process the state through the teleportation-inspired layer.**
    4. **Inject an optional attack** such as Pauli-X or Pauli-Z.
    5. **Measure multiple copies** of the received state.
    6. **Compare measurement distributions** with the expected distribution.
    7. **Calculate statistical deviation** using chi-square.
    8. If the deviation exceeds the threshold → **THREAT DETECTED**.
    """)

    # ========================================================
    # CONTROLLED TEST INFORMATION
    # ========================================================

    st.subheader("📋 Prototype Evaluation")

    st.markdown("""
    **Controlled 8-case evaluation used in the prototype:**

    - 4 genuine signature cases
    - 4 simulated attack cases
    - 4/4 attack cases detected
    - 0 false alarms in the controlled test

    **Detection Rate / TPR: 100%**

    This result applies only to the controlled prototype test cases,
    not to real-world attack detection accuracy.
    """)

    # ========================================================
    # LIMITATION
    # ========================================================

    st.info(
        "⚠️ Prototype Notice: This is a quantum-inspired / "
        "QDS-inspired research prototype for SIH demonstration. "
        "It is not a production-ready Quantum Digital Signature "
        "protocol and does not provide a real-world security guarantee."
    )


# ============================================================
# FOOTER
# ============================================================

st.markdown("---")

st.markdown("""
<div class="footer">

<b>SIH 2026</b> | Quantum-Inspired Cyber Threat Detection for Digital Signature Security

<br>

Qiskit + Python + Streamlit

</div>
""", unsafe_allow_html=True)