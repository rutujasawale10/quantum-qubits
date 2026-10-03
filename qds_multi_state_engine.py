from qiskit import QuantumCircuit
from qiskit.quantum_info import Statevector
from qiskit.primitives import StatevectorSampler
import random
import math


# ============================================================
# QDS MULTI-STATE THREAT DETECTION ENGINE
# ============================================================

ROUNDS = 100
SHOTS = 100

STATES = ["0", "1", "+", "-"]

# 50% NONE, 25% X, 25% Z
ATTACK_TYPES = ["NONE", "NONE", "X", "Z"]


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
# 3. SELECT VERIFICATION BASIS
# ============================================================

def get_basis(state_name):

    if state_name in ["0", "1"]:
        return "Z"

    return "X"


# ============================================================
# 4. EXPECTED RESULT
# ============================================================

def get_expected_result(state_name):

    if state_name == "0":
        return "0"

    elif state_name == "1":
        return "1"

    elif state_name == "+":
        return "0"

    elif state_name == "-":
        return "1"


# ============================================================
# 5. MEASURE STATE
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

    return {
        "0": counts.get("0", 0),
        "1": counts.get("1", 0)
    }


# ============================================================
# 6. STATISTICAL TEST
# ============================================================

def chi_square_test(counts, expected_result, shots):

    correct = counts.get(expected_result, 0)

    wrong_result = "1" if expected_result == "0" else "0"

    wrong = counts.get(wrong_result, 0)

    # Ideal signature should never produce the wrong result
    if wrong > 0:
        return float("inf")

    return 0.0


# ============================================================
# 7. THREAT DECISION
# ============================================================

def detect_threat(chi):

    if math.isinf(chi):
        return True

    return False


# ============================================================
# HEADER
# ============================================================

print("=" * 80)
print("             QUANTUM DIGITAL SIGNATURE")
print("             MULTI-STATE THREAT DETECTION")
print("=" * 80)

print(f"Total Rounds : {ROUNDS}")
print(f"Shots/Round  : {SHOTS}")

print("\nQuantum States:")
print("Z Basis → |0>, |1>")
print("X Basis → |+>, |->")

print("\nAttack Distribution:")
print("NONE → 50%")
print("X    → 25%")
print("Z    → 25%")

print("\n" + "=" * 80)


# ============================================================
# CONFUSION MATRIX
# ============================================================

TP = 0
TN = 0
FP = 0
FN = 0

x_total = 0
x_detected = 0

z_total = 0
z_detected = 0

genuine_total = 0
genuine_rejected = 0


# ============================================================
# ROUND SIMULATION
# ============================================================

for round_number in range(1, ROUNDS + 1):

    # Random state
    state_name = random.choice(STATES)

    # Correct basis
    basis = get_basis(state_name)

    # Random attack
    attack = random.choice(ATTACK_TYPES)

    # Original signature
    original_state = create_state(state_name)

    # Apply attack
    received_state = apply_attack(
        original_state,
        attack
    )

    # Expected result
    expected = get_expected_result(state_name)

    # Measurement
    counts = measure_state(
        received_state,
        basis,
        SHOTS
    )

    # Chi-square
    chi = chi_square_test(
        counts,
        expected,
        SHOTS
    )

    # Threat decision
    threat = detect_threat(chi)


    # ========================================================
    # CLASSIFICATION
    # ========================================================

    if attack == "NONE":

        genuine_total += 1

        if threat:

            FP += 1
            genuine_rejected += 1
            status = "FALSE ALARM"

        else:

            TN += 1
            status = "VALID"

    elif attack == "X":

        x_total += 1

        if threat:

            TP += 1
            x_detected += 1
            status = "X ATTACK DETECTED"

        else:

            FN += 1
            status = "X ATTACK NOT DETECTED"

    elif attack == "Z":

        z_total += 1

        if threat:

            TP += 1
            z_detected += 1
            status = "Z ATTACK DETECTED"

        else:

            FN += 1
            status = "Z ATTACK NOT DETECTED"


    # ========================================================
    # PRINT FIRST 20 ROUNDS
    # ========================================================

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
            f"Expected: {expected} | "
            f"Counts: {counts} | "
            f"Chi²: {chi_display:8s} | "
            f"{status}"
        )


# ============================================================
# METRICS
# ============================================================

total_attacks = x_total + z_total

total_detected = x_detected + z_detected

if total_attacks > 0:

    overall_detection_rate = (
        total_detected / total_attacks
    ) * 100

    false_acceptance_rate = (
        (total_attacks - total_detected)
        / total_attacks
    ) * 100

else:

    overall_detection_rate = 0
    false_acceptance_rate = 0


if x_total > 0:

    x_detection_rate = (
        x_detected / x_total
    ) * 100

else:

    x_detection_rate = 0


if z_total > 0:

    z_detection_rate = (
        z_detected / z_total
    ) * 100

else:

    z_detection_rate = 0


if genuine_total > 0:

    false_rejection_rate = (
        genuine_rejected / genuine_total
    ) * 100

    false_alarm_rate = (
        genuine_rejected / genuine_total
    ) * 100

else:

    false_rejection_rate = 0
    false_alarm_rate = 0


# ============================================================
# FINAL RESULTS
# ============================================================

print("\n" + "=" * 80)
print("                         FINAL RESULTS")
print("=" * 80)

print(f"\nTotal Rounds          : {ROUNDS}")

print(f"Genuine Rounds        : {genuine_total}")

print(f"X Attack Rounds       : {x_total}")
print(f"Z Attack Rounds       : {z_total}")

print("\n" + "-" * 80)

print("CONFUSION MATRIX")

print("-" * 80)

print(f"True Positives (TP)   : {TP}")
print(f"False Positives (FP)  : {FP}")
print(f"True Negatives (TN)   : {TN}")
print(f"False Negatives (FN)  : {FN}")


# ============================================================
# ATTACK-SPECIFIC RESULTS
# ============================================================

print("\n" + "-" * 80)

print("ATTACK-SPECIFIC DETECTION")

print("-" * 80)

print(
    f"X Attack Detection Rate : "
    f"{x_detection_rate:.2f}%"
)

print(
    f"Z Attack Detection Rate : "
    f"{z_detection_rate:.2f}%"
)

print(
    f"Overall Detection Rate  : "
    f"{overall_detection_rate:.2f}%"
)


# ============================================================
# ERROR RATES
# ============================================================

print("\n" + "-" * 80)

print("SECURITY ERROR METRICS")

print("-" * 80)

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
# FINAL DECISION
# ============================================================

print("\n" + "=" * 80)

if total_detected > 0:

    print("🚨 QUANTUM CYBER THREATS DETECTED")

else:

    print("✅ NO QUANTUM THREAT DETECTED")

print("=" * 80)


# ============================================================
# SYSTEM FLOW
# ============================================================

print("""
QDS SECURITY FLOW

Alice
  ↓
Quantum Signature
  ↓
BB84 Quantum States
  ↓
Quantum Channel
  ↓
X / Z Attack
  ↓
Bob
  ↓
Correct Basis Verification
  ↓
Projective Measurement
  ↓
Statistical Analysis
  ↓
Chi-Square Test
  ↓
Threat Decision
  ↓
VALID / FORGED
""")


print("=" * 80)
print("MULTI-STATE QDS ENGINE COMPLETED")
print("=" * 80)