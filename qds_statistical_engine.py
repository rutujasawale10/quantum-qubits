from qiskit import QuantumCircuit
from qiskit.quantum_info import Statevector
from qiskit.primitives import StatevectorSampler
import random
import math


# ============================================================
# QDS STATISTICAL THREAT DETECTION ENGINE
# ============================================================

ROUNDS = 100
SHOTS = 100
THRESHOLD = 10

STATES = ["0", "1", "+", "-"]
BASES = ["Z", "X"]
ATTACKS = ["NONE", "X", "Z"]


# ============================================================
# 1. CREATE QUANTUM STATE
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
# 2. APPLY ATTACK
# ============================================================

def apply_attack(state, attack):

    qc = QuantumCircuit(1)

    if attack == "NONE":
        pass

    elif attack == "X":
        qc.x(0)

    elif attack == "Z":
        qc.z(0)

    return state.evolve(qc)


# ============================================================
# 3. THEORETICAL EXPECTED PROBABILITIES
# ============================================================

def expected_probabilities(state, basis):

    # Computational / Z basis
    if state == "0" and basis == "Z":
        return {"0": 1.0, "1": 0.0}

    if state == "1" and basis == "Z":
        return {"0": 0.0, "1": 1.0}

    # X basis
    if state == "+" and basis == "X":
        return {"0": 1.0, "1": 0.0}

    if state == "-" and basis == "X":
        return {"0": 0.0, "1": 1.0}

    # States measured in the opposite basis
    return {"0": 0.5, "1": 0.5}


# ============================================================
# 4. MEASURE QUANTUM STATE
# ============================================================

def measure_state(state, basis, shots=100):

    qc = QuantumCircuit(1, 1)

    # Initialize state
    qc.initialize(state.data, 0)

    # X-basis measurement
    # H converts X basis to computational basis
    if basis == "X":
        qc.h(0)

    qc.measure(0, 0)

    sampler = StatevectorSampler()

    result = sampler.run(
        [qc],
        shots=shots
    ).result()

    counts = result[0].data.c.get_counts()

    return {
        "0": counts.get("0", 0),
        "1": counts.get("1", 0)
    }


# ============================================================
# 5. CHI-SQUARE CALCULATION
# ============================================================

def chi_square(observed, expected_prob, shots):

    chi = 0.0

    for bit in ["0", "1"]:

        expected = expected_prob[bit] * shots
        observed_value = observed.get(bit, 0)

        # Impossible outcome
        if expected == 0:

            if observed_value > 0:
                return float("inf")

            continue

        chi += ((observed_value - expected) ** 2) / expected

    return chi


# ============================================================
# 6. DETECTION DECISION
# ============================================================

def detect_threat(chi):

    if math.isinf(chi):
        return True

    return chi > THRESHOLD


# ============================================================
# 7. MAIN ENGINE
# ============================================================

print("=" * 65)
print("        QUANTUM DIGITAL SIGNATURE")
print("        STATISTICAL THREAT DETECTION ENGINE")
print("=" * 65)

print(f"Total Rounds : {ROUNDS}")
print(f"Shots/Round  : {SHOTS}")
print(f"Threshold    : {THRESHOLD}")

print("\nStates       :", STATES)
print("Bases        :", BASES)
print("Attacks      :", ATTACKS)

print("\n" + "=" * 65)


# ============================================================
# STATISTICAL COUNTERS
# ============================================================

TP = 0   # Attack detected
TN = 0   # No attack correctly accepted
FP = 0   # Genuine round incorrectly rejected
FN = 0   # Attack not detected

total_chi = 0.0
finite_chi_count = 0


# ============================================================
# ROUND SIMULATION
# ============================================================

for round_number in range(1, ROUNDS + 1):

    # Random quantum state
    state_name = random.choice(STATES)

    # Random measurement basis
    basis = random.choice(BASES)

    # Random attack / no attack
    attack = random.choice(ATTACKS)

    # Create original quantum state
    original_state = create_state(state_name)

    # Apply attack
    received_state = apply_attack(
        original_state,
        attack
    )

    # Expected distribution for original state
    expected = expected_probabilities(
        state_name,
        basis
    )

    # Measure received state
    received_counts = measure_state(
        received_state,
        basis,
        SHOTS
    )

    # Chi-square
    chi = chi_square(
        received_counts,
        expected,
        SHOTS
    )

    # Threat decision
    threat = detect_threat(chi)

    # --------------------------------------------------------
    # Confusion Matrix
    # --------------------------------------------------------

    if attack != "NONE":

        # Attack exists
        if threat:
            TP += 1
            status = "THREAT DETECTED"
        else:
            FN += 1
            status = "ATTACK NOT DETECTED"

    else:

        # No attack
        if threat:
            FP += 1
            status = "FALSE ALARM"
        else:
            TN += 1
            status = "NORMAL"

    # Average chi-square
    if not math.isinf(chi):
        total_chi += chi
        finite_chi_count += 1

    # --------------------------------------------------------
    # Print first 20 rounds
    # --------------------------------------------------------

    if round_number <= 20:

        if math.isinf(chi):
            chi_display = "INFINITY"
        else:
            chi_display = f"{chi:.2f}"

        print(
            f"Round {round_number:03d} | "
            f"State: |{state_name}> | "
            f"Basis: {basis} | "
            f"Attack: {attack:4s} | "
            f"Counts: {received_counts} | "
            f"Chi²: {chi_display:8s} | "
            f"{status}"
        )


# ============================================================
# METRICS
# ============================================================

total_attack_rounds = TP + FN
total_genuine_rounds = TN + FP

if total_attack_rounds > 0:
    detection_rate = (TP / total_attack_rounds) * 100
    false_acceptance_rate = (FN / total_attack_rounds) * 100
else:
    detection_rate = 0
    false_acceptance_rate = 0


if total_genuine_rounds > 0:
    false_rejection_rate = (FP / total_genuine_rounds) * 100
    false_alarm_rate = (FP / total_genuine_rounds) * 100
else:
    false_rejection_rate = 0
    false_alarm_rate = 0


if finite_chi_count > 0:
    average_chi = total_chi / finite_chi_count
else:
    average_chi = float("inf")


# ============================================================
# FINAL RESULTS
# ============================================================

print("\n" + "=" * 65)
print("                  FINAL RESULTS")
print("=" * 65)

print(f"\nTotal Rounds              : {ROUNDS}")

print(f"True Positives (TP)      : {TP}")
print(f"False Negatives (FN)     : {FN}")
print(f"False Positives (FP)     : {FP}")
print(f"True Negatives (TN)      : {TN}")

print("\n" + "-" * 65)

print(
    f"Threat Detection Rate    : "
    f"{detection_rate:.2f}%"
)

print(
    f"False Acceptance Rate    : "
    f"{false_acceptance_rate:.2f}%"
)

print(
    f"False Rejection Rate     : "
    f"{false_rejection_rate:.2f}%"
)

print(
    f"False Alarm Rate         : "
    f"{false_alarm_rate:.2f}%"
)

print(
    f"Average Chi-Square       : "
    f"{average_chi:.2f}"
)

print(f"Detection Threshold      : {THRESHOLD}")


# ============================================================
# FINAL SECURITY DECISION
# ============================================================

print("\n" + "=" * 65)

if TP > 0:
    print("🚨 QUANTUM THREAT DETECTION ACTIVE")
else:
    print("✅ NO QUANTUM THREAT DETECTED")

print("=" * 65)


# ============================================================
# PROJECT INTERPRETATION
# ============================================================

print("\nPROJECT FLOW")
print("-" * 65)

print("Quantum State")
print("      ↓")
print("Digital Signature State")
print("      ↓")
print("Quantum Channel")
print("      ↓")
print("X / Z Attack or No Attack")
print("      ↓")
print("Projective Measurement")
print("      ↓")
print("Statistical Analysis")
print("      ↓")
print("Chi-Square Test")
print("      ↓")
print("Threshold Comparison")
print("      ↓")
print("VALID / THREAT DETECTED")

print("\n" + "=" * 65)
print("QDS STATISTICAL ENGINE COMPLETED")
print("=" * 65)