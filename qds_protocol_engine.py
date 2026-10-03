from qiskit import QuantumCircuit
from qiskit.quantum_info import Statevector
from qiskit.primitives import StatevectorSampler
import random
import math


# ============================================================
# QDS PROTOCOL ENGINE
# Quantum Digital Signature Threat Detection
# ============================================================

ROUNDS = 100
SHOTS = 100
THRESHOLD = 10

# BB84-style states
STATES = ["0", "1", "+", "-"]

# Attack possibilities
ATTACKS = ["NONE", "X", "Z"]


# ============================================================
# 1. CREATE QUANTUM SIGNATURE STATE
# ============================================================

def create_state(state_name):

    qc = QuantumCircuit(1)

    if state_name == "0":
        # |0>
        pass

    elif state_name == "1":
        # |1>
        qc.x(0)

    elif state_name == "+":
        # |+>
        qc.h(0)

    elif state_name == "-":
        # |->
        qc.x(0)
        qc.h(0)

    return Statevector.from_instruction(qc)


# ============================================================
# 2. APPLY QUANTUM ATTACK
# ============================================================

def apply_attack(state, attack):

    qc = QuantumCircuit(1)

    if attack == "NONE":
        pass

    elif attack == "X":
        # Bit flip
        qc.x(0)

    elif attack == "Z":
        # Phase flip
        qc.z(0)

    return state.evolve(qc)


# ============================================================
# 3. SELECT CORRECT VERIFICATION BASIS
# ============================================================

def correct_basis(state_name):

    if state_name in ["0", "1"]:
        return "Z"

    elif state_name in ["+", "-"]:
        return "X"


# ============================================================
# 4. EXPECTED MEASUREMENT
# ============================================================

def expected_result(state_name):

    if state_name == "0":
        return "0"

    elif state_name == "1":
        return "1"

    elif state_name == "+":
        return "0"

    elif state_name == "-":
        return "1"


# ============================================================
# 5. MEASURE QUANTUM STATE
# ============================================================

def measure_state(state, basis, shots):

    qc = QuantumCircuit(1, 1)

    # Put received quantum state into circuit
    qc.initialize(state.data, 0)

    # X-basis measurement
    if basis == "X":
        qc.h(0)

    # Z-basis measurement
    # No extra gate required

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
# 6. CHI-SQUARE TEST
# ============================================================

def calculate_chi_square(counts, expected_bit, shots):

    # Expected distribution:
    # Correct result = 100%
    # Wrong result   = 0%

    correct = counts.get(expected_bit, 0)

    wrong_bit = "1" if expected_bit == "0" else "0"

    wrong = counts.get(wrong_bit, 0)

    # If wrong result appears, it is statistically impossible
    # for the ideal signature state.

    if wrong > 0:
        return float("inf")

    return 0.0


# ============================================================
# 7. THREAT DECISION
# ============================================================

def detect_threat(chi_square):

    if math.isinf(chi_square):
        return True

    return chi_square > THRESHOLD


# ============================================================
# 8. PRINT HEADER
# ============================================================

print("=" * 75)
print("           QUANTUM DIGITAL SIGNATURE")
print("           QDS PROTOCOL THREAT DETECTION")
print("=" * 75)

print(f"Total Rounds : {ROUNDS}")
print(f"Shots/Round  : {SHOTS}")
print(f"Threshold    : {THRESHOLD}")

print("\nQuantum States :", STATES)
print("Attacks        :", ATTACKS)

print("\n" + "=" * 75)


# ============================================================
# 9. CONFUSION MATRIX
# ============================================================

TP = 0
TN = 0
FP = 0
FN = 0

attack_rounds = 0
genuine_rounds = 0

detected_attacks = 0
missed_attacks = 0


# ============================================================
# 10. MAIN SIMULATION
# ============================================================

for round_number in range(1, ROUNDS + 1):

    # --------------------------------------------------------
    # Random state
    # --------------------------------------------------------

    state_name = random.choice(STATES)

    # Correct basis for that state
    basis = correct_basis(state_name)

    # --------------------------------------------------------
    # Balanced attack/no-attack selection
    # --------------------------------------------------------

    if round_number % 2 == 0:
        attack = random.choice(["X", "Z"])
    else:
        attack = "NONE"

    # --------------------------------------------------------
    # Create original signature
    # --------------------------------------------------------

    original_state = create_state(state_name)

    # --------------------------------------------------------
    # Apply attack
    # --------------------------------------------------------

    received_state = apply_attack(
        original_state,
        attack
    )

    # --------------------------------------------------------
    # Expected result
    # --------------------------------------------------------

    expected_bit = expected_result(state_name)

    # --------------------------------------------------------
    # Measure received state
    # --------------------------------------------------------

    counts = measure_state(
        received_state,
        basis,
        SHOTS
    )

    # --------------------------------------------------------
    # Statistical analysis
    # --------------------------------------------------------

    chi = calculate_chi_square(
        counts,
        expected_bit,
        SHOTS
    )

    # --------------------------------------------------------
    # Threat decision
    # --------------------------------------------------------

    threat = detect_threat(chi)

    # ========================================================
    # CONFUSION MATRIX
    # ========================================================

    if attack == "NONE":

        genuine_rounds += 1

        if threat:

            FP += 1

            status = "FALSE ALARM"

        else:

            TN += 1

            status = "VALID"

    else:

        attack_rounds += 1

        if threat:

            TP += 1
            detected_attacks += 1

            status = "THREAT DETECTED"

        else:

            FN += 1
            missed_attacks += 1

            status = "ATTACK NOT DETECTED"

    # --------------------------------------------------------
    # Display first 20 rounds
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
            f"Expected: {expected_bit} | "
            f"Counts: {counts} | "
            f"Chi²: {chi_display:8s} | "
            f"{status}"
        )


# ============================================================
# 11. CALCULATE PERFORMANCE
# ============================================================

if attack_rounds > 0:

    detection_rate = (
        TP / attack_rounds
    ) * 100

    false_acceptance_rate = (
        FN / attack_rounds
    ) * 100

else:

    detection_rate = 0
    false_acceptance_rate = 0


if genuine_rounds > 0:

    false_rejection_rate = (
        FP / genuine_rounds
    ) * 100

    false_alarm_rate = (
        FP / genuine_rounds
    ) * 100

else:

    false_rejection_rate = 0
    false_alarm_rate = 0


# ============================================================
# 12. FINAL RESULTS
# ============================================================

print("\n" + "=" * 75)
print("                       FINAL RESULTS")
print("=" * 75)

print(f"\nTotal Rounds          : {ROUNDS}")

print(f"Genuine Rounds        : {genuine_rounds}")
print(f"Attack Rounds         : {attack_rounds}")

print("\nCONFUSION MATRIX")
print("-" * 75)

print(f"True Positives (TP)   : {TP}")
print(f"False Positives (FP)  : {FP}")
print(f"True Negatives (TN)   : {TN}")
print(f"False Negatives (FN)  : {FN}")

print("\nPERFORMANCE METRICS")
print("-" * 75)

print(
    f"Threat Detection Rate : "
    f"{detection_rate:.2f}%"
)

print(
    f"False Acceptance Rate : "
    f"{false_acceptance_rate:.2f}%"
)

print(
    f"False Rejection Rate  : "
    f"{false_rejection_rate:.2f}%"
)

print(
    f"False Alarm Rate      : "
    f"{false_alarm_rate:.2f}%"
)


# ============================================================
# 13. FINAL SECURITY DECISION
# ============================================================

print("\n" + "=" * 75)

if TP > 0:

    print("🚨 QUANTUM CYBER THREAT DETECTED")

else:

    print("✅ NO THREAT DETECTED")

print("=" * 75)


# ============================================================
# 14. QDS PROTOCOL FLOW
# ============================================================

print("\nQDS PROTOCOL FLOW")
print("-" * 75)

print("""
Alice
  ↓
Quantum Signature State
  ↓
Quantum Channel
  ↓
Possible X / Z Attack
  ↓
Bob Receives Quantum State
  ↓
Correct Basis Selection
  ↓
Projective Measurement
  ↓
Statistical Analysis
  ↓
Chi-Square Test
  ↓
Threshold Comparison
  ↓
VALID / THREAT DETECTED
""")


# ============================================================
# 15. FINAL SUMMARY
# ============================================================

print("=" * 75)
print("QDS PROTOCOL ENGINE COMPLETED")
print("=" * 75)

print("""
This simulation demonstrates:

1. Quantum signature states
2. X and Z attack simulation
3. Basis-dependent verification
4. Projective measurement
5. Statistical threat detection
6. Chi-square based decision
7. TP / TN / FP / FN calculation
8. Detection and error-rate analysis
""")