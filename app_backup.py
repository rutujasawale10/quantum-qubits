import streamlit as st
import math
from qiskit import QuantumCircuit
from qiskit.quantum_info import Statevector
from qiskit.primitives import StatevectorSampler


# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="Quantum Digital Signature Security",
    page_icon="⚛️",
    layout="wide"
)


# ============================================================
# CUSTOM CSS
# ============================================================

st.markdown("""
<style>

.main {
    background-color: #f7f9fc;
}

.block-container {
    padding-top: 2rem;
    padding-bottom: 2rem;
}

.hero {
    padding: 30px;
    border-radius: 18px;
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

.metric-card {
    padding: 20px;
    border-radius: 14px;
    background-color: white;
    border: 1px solid #e5e7eb;
    box-shadow: 0 3px 10px rgba(0,0,0,0.05);
}

.success-box {
    padding: 18px;
    border-radius: 12px;
    background-color: #ecfdf5;
    border: 1px solid #10b981;
    color: #065f46;
    font-size: 18px;
    font-weight: 600;
}

.danger-box {
    padding: 18px;
    border-radius: 12px;
    background-color: #fef2f2;
    border: 1px solid #ef4444;
    color: #991b1b;
    font-size: 18px;
    font-weight: 600;
}

.info-box {
    padding: 18px;
    border-radius: 12px;
    background-color: #eff6ff;
    border: 1px solid #3b82f6;
    color: #1e40af;
}

</style>
""", unsafe_allow_html=True)


# ============================================================
# HEADER
# ============================================================

st.markdown("""
<div class="hero">

<h1>⚛️ Quantum Digital Signature Security</h1>

<p>
Quantum-Inspired Cyber Threat Detection for Digital Signature Security
</p>

<p>
SIH 2026 Prototype | QDS + Quantum Teleportation + Threat Detection
</p>

</div>
""", unsafe_allow_html=True)


# ============================================================
# SIDEBAR
# ============================================================

st.sidebar.title("⚙️ Security Configuration")

message = st.sidebar.text_input(
    "Message",
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
# BASIS MAPPING
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
# MEASUREMENT
# ============================================================

def measure_state(state, basis, shots):

    qc = QuantumCircuit(1, 1)

    qc.initialize(state.data, 0)

    # X-basis measurement
    if basis == "X":
        qc.h(0)

    qc.measure(0, 0)

    sampler = StatevectorSampler()

    result = sampler.run(
        [qc],
        shots=shots
    ).result()

    counts = result[0].data.c.get_counts()

    return counts


# ============================================================
# EXPECTED DISTRIBUTION
# ============================================================

def expected_distribution(state, basis):

    if basis == "Z":

        probabilities = state.probabilities()

    else:

        # Convert state into X basis
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

def chi_square(observed, expected_probabilities, shots):

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
# TELEPORTATION CIRCUIT
# ============================================================

def create_teleportation_circuit(state_name):

    qc = QuantumCircuit(3)

    # Original state q0
    if state_name == "1":
        qc.x(0)

    elif state_name == "+":
        qc.h(0)

    elif state_name == "-":
        qc.x(0)
        qc.h(0)

    # Bell pair
    qc.h(1)
    qc.cx(1, 2)

    # Alice's operations
    qc.cx(0, 1)
    qc.h(0)

    # Bob's coherent corrections
    qc.cx(1, 2)
    qc.cz(0, 2)

    return qc


# ============================================================
# MAIN VERIFICATION
# ============================================================

if run_button:

    # --------------------------------------------------------
    # ORIGINAL SIGNATURE
    # --------------------------------------------------------

    original_state = create_state(state_name)

    basis = get_basis(state_name)

    # --------------------------------------------------------
    # ATTACK
    # --------------------------------------------------------

    received_state = apply_attack(
        original_state,
        attack
    )

    # --------------------------------------------------------
    # MEASUREMENTS
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
    # STATISTICS
    # --------------------------------------------------------

    expected = expected_distribution(
        original_state,
        basis
    )

    chi = chi_square(
        received_counts,
        expected,
        shots
    )

    error_rate = calculate_error_rate(
        original_counts,
        received_counts
    )

    # Detection threshold
    threshold = 10

    threat_detected = chi > threshold

    # --------------------------------------------------------
    # SIGNATURE STATUS
    # --------------------------------------------------------

    if attack == "NONE":

        signature_valid = True

    else:

        signature_valid = not threat_detected

    # ========================================================
    # RESULT HEADER
    # ========================================================

    st.subheader("🔐 Security Verification Result")

    if threat_detected:

        st.markdown(
            """
            <div class="danger-box">
            🚨 THREAT DETECTED — Possible signature forgery or quantum attack detected.
            </div>
            """,
            unsafe_allow_html=True
        )

    else:

        st.markdown(
            """
            <div class="success-box">
            ✅ NO THREAT DETECTED — Signature appears valid under this test.
            </div>
            """,
            unsafe_allow_html=True
        )

    st.write("")

    # ========================================================
    # METRICS
    # ========================================================

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            "Quantum State",
            f"|{state_name}⟩"
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
    # SIGNATURE INFORMATION
    # ========================================================

    st.subheader("📝 Digital Signature")

    col1, col2 = st.columns(2)

    with col1:

        st.markdown("### Signature Generation")

        st.write(
            f"**Message:** {message}"
        )

        st.write(
            f"**Quantum State:** |{state_name}⟩"
        )

        st.write(
            f"**Verification Basis:** {basis}-Basis"
        )

        st.write(
            "**Signature Type:** Quantum State Based"
        )

    with col2:

        st.markdown("### Verification")

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
    # MEASUREMENT RESULTS
    # ========================================================

    st.subheader("📊 Quantum Measurement Analysis")

    col1, col2 = st.columns(2)

    with col1:

        st.markdown("### Original Signature")

        st.json(original_counts)

        original_total = sum(
            original_counts.values()
        )

        st.write(
            f"Total Measurements: {original_total}"
        )

    with col2:

        st.markdown("### Received Signature")

        st.json(received_counts)

        received_total = sum(
            received_counts.values()
        )

        st.write(
            f"Total Measurements: {received_total}"
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
            "The observed distribution is within the "
            "configured security threshold."
        )

    # ========================================================
    # TELEPORTATION
    # ========================================================

    st.subheader("🔗 Quantum Teleportation Layer")

    st.write(
        "The signature state is prepared and transmitted "
        "through a 3-qubit teleportation-inspired circuit."
    )

    teleport_circuit = create_teleportation_circuit(
        state_name
    )

    st.code(
        str(teleport_circuit),
        language="text"
    )

    st.markdown(
        """
        **Teleportation Flow**

        `Unknown Quantum State`
        → `Bell Pair`
        → `Alice Measurement`
        → `Quantum Corrections`
        → `Bob's Qubit`
        """
    )

    # ========================================================
    # ATTACK EXPLANATION
    # ========================================================

    st.subheader("🛡️ Attack Analysis")

    if attack == "NONE":

        st.success(
            "No attack was injected. The received state "
            "represents the genuine signature."
        )

    elif attack == "X":

        st.warning(
            "Pauli-X attack was injected. X acts like a "
            "quantum bit-flip operation."
        )

    elif attack == "Z":

        st.warning(
            "Pauli-Z attack was injected. Z introduces a "
            "phase-flip that can be detected in the X basis."
        )

    # ========================================================
    # SECURITY INFORMATION
    # ========================================================

    st.subheader("🧠 Security Logic")

    st.markdown(
        """
        1. **Generate quantum signature** from the selected quantum state.
        2. **Select verification basis** according to the state.
        3. **Transmit through quantum teleportation layer.**
        4. **Inject optional attack** such as Pauli-X or Pauli-Z.
        5. **Measure multiple copies** of the received state.
        6. **Compare measurement distribution** with the expected distribution.
        7. **Calculate statistical deviation** using chi-square.
        8. If deviation exceeds the threshold → **THREAT DETECTED**.
        """
    )

    # ========================================================
    # IMPORTANT LIMITATION
    # ========================================================

    st.info(
        "⚠️ Prototype Notice: This is a quantum-inspired / "
        "QDS-inspired research prototype for SIH demonstration. "
        "It is not a production-ready Quantum Digital Signature "
        "protocol or a real-world security guarantee."
    )


# ============================================================
# DEFAULT SCREEN
# ============================================================

else:

    st.markdown(
        """
        <div class="info-box">

        <b>Welcome to the Quantum Security Dashboard.</b>

        <br><br>

        Configure a quantum signature state and optional attack
        from the sidebar, then click
        <b>Run Security Verification</b>.

        </div>
        """,
        unsafe_allow_html=True
    )

    st.write("")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("### ⚛️ Quantum Signature")
        st.write(
            "Generate a signature using computational "
            "and superposition quantum states."
        )

    with col2:
        st.markdown("### 🔗 Teleportation")
        st.write(
            "Demonstrate secure quantum-state transmission "
            "using a three-qubit teleportation circuit."
        )

    with col3:
        st.markdown("### 🛡️ Threat Detection")
        st.write(
            "Analyze quantum measurements and detect "
            "simulated Pauli-X and Pauli-Z attacks."
        )

    st.write("")

    st.markdown(
        """
        ### Supported Quantum States

        | State | Description |
        |---|---|
        | **|0⟩** | Computational basis state |
        | **|1⟩** | Computational basis state |
        | **|+⟩** | Superposition state |
        | **|−⟩** | Superposition state |

        ### Supported Attacks

        - **NONE** → Genuine signature
        - **X** → Pauli-X / bit-flip attack
        - **Z** → Pauli-Z / phase-flip attack
        """
    )


# ============================================================
# FOOTER
# ============================================================

st.markdown("---")

st.caption(
    "SIH 2026 | Quantum-Inspired Cyber Threat Detection "
    "for Digital Signature Security | Qiskit + Streamlit"
)