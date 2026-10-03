from qiskit import QuantumCircuit
from qiskit.primitives import StatevectorSampler
import random


# =========================================================
# QDS PROTOCOL DEMO
# =========================================================

COPIES = 100
ERROR_THRESHOLD = 0.20

STATES = ["0", "1", "+", "-"]
ATTACKS = ["NONE", "X", "Z"]


# =========================================================
# 1. QUANTUM SIGNATURE GENERATION
# =========================================================

def generate_signature(state_name):

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

    return qc


# =========================================================
# 2. SELECT VERIFICATION BASIS
# =========================================================

def select_basis(state_name):

    if state_name in ["0", "1"]:
        return "Z"

    return "X"


# =========================================================
# 3. EXPECTED VERIFICATION RESULT
# =========================================================

def expected_result(state_name):

    if state_name == "0":
        return "0"

    elif state_name == "1":
        return "1"

    elif state_name == "+":
        return "0"

    elif state_name == "-":
        return "1"


# =========================================================
# 4. APPLY CHANNEL ATTACK
# =========================================================

def apply_attack(qc, attack):

    attacked = qc.copy()

    if attack == "X":
        attacked.x(0)

    elif attack == "Z":
        attacked.z(0)

    return attacked


# =========================================================
# 5. QUANTUM VERIFICATION
# =========================================================

def verify_signature(signature, attack, basis, shots):

    qc = apply_attack(signature, attack)

    # X-basis measurement
    if basis == "X":
        qc.h(0)

    qc.measure_all()

    sampler = StatevectorSampler()

    result = sampler.run(
        [qc],
        shots=shots
    ).result()

    counts = result[0].data.meas.get_counts()

    return counts


# =========================================================
# 6. ERROR / DISTURBANCE CALCULATION
# =========================================================

def calculate_error(counts, expected, shots):

    correct_count = counts.get(expected, 0)

    error_count = shots - correct_count

    error_rate = error_count / shots

    return error_rate


# =========================================================
# 7. SINGLE QDS TRANSACTION
# =========================================================

def run_qds_transaction(state_name, attack):

    basis = select_basis(state_name)

    expected = expected_result(state_name)

    signature = generate_signature(state_name)

    counts = verify_signature(
        signature,
        attack,
        basis,
        COPIES
    )

    error_rate = calculate_error(
        counts,
        expected,
        COPIES
    )

    if error_rate > ERROR_THRESHOLD:
        status = "FORGED / THREAT"

    else:
        status = "VALID"

    return basis, expected, counts, error_rate, status


# =========================================================
# MAIN PROGRAM
# =========================================================

print("=" * 80)
print("QUANTUM DIGITAL SIGNATURE PROTOCOL DEMONSTRATION")
print("=" * 80)

print("Copies Used      :", COPIES)
print("Error Threshold  :", ERROR_THRESHOLD)

print("=" * 80)


# =========================================================
# DEMO 1 - GENUINE SIGNATURE
# =========================================================

print("\n")
print("1. GENUINE SIGNATURE VERIFICATION")
print("-" * 80)

state = "+"

basis, expected, counts, error, status = run_qds_transaction(
    state,
    "NONE"
)

print("Original State   :", state)
print("Verification Basis:", basis)
print("Expected Result  :", expected)
print("Measurement      :", counts)
print(f"Error Rate       : {error:.2f}")
print("Signature Status :", status)


# =========================================================
# DEMO 2 - Z ATTACK
# =========================================================

print("\n")
print("2. Z ATTACK SIMULATION")
print("-" * 80)

state = "+"

basis, expected, counts, error, status = run_qds_transaction(
    state,
    "Z"
)

print("Original State   :", state)
print("Attack Applied   : Z")
print("Verification Basis:", basis)
print("Expected Result  :", expected)
print("Measurement      :", counts)
print(f"Error Rate       : {error:.2f}")
print("Signature Status :", status)


# =========================================================
# DEMO 3 - X ATTACK
# =========================================================

print("\n")
print("3. X ATTACK SIMULATION")
print("-" * 80)

state = "0"

basis, expected, counts, error, status = run_qds_transaction(
    state,
    "X"
)

print("Original State   :", state)
print("Attack Applied   : X")
print("Verification Basis:", basis)
print("Expected Result  :", expected)
print("Measurement      :", counts)
print(f"Error Rate       : {error:.2f}")
print("Signature Status :", status)


# =========================================================
# 4. RANDOM MULTI-ROUND TEST
# =========================================================

print("\n")
print("=" * 80)
print("MULTI-ROUND QDS VERIFICATION")
print("=" * 80)

ROUNDS = 20

tp = 0
tn = 0
fp = 0
fn = 0

for round_no in range(1, ROUNDS + 1):

    state = random.choice(STATES)

    # Alternate genuine and attack rounds
    if round_no % 2 == 0:
        attack = random.choice(["X", "Z"])
    else:
        attack = "NONE"

    basis, expected, counts, error, status = run_qds_transaction(
        state,
        attack
    )

    threat = error > ERROR_THRESHOLD

    # Confusion matrix
    if attack == "NONE":

        if threat:
            fp += 1
        else:
            tn += 1

    else:

        if threat:
            tp += 1
        else:
            fn += 1


    print(
        f"Round {round_no:02d} | "
        f"State={state:>2} | "
        f"Basis={basis} | "
        f"Attack={attack:>4} | "
        f"Error={error:.2f} | "
        f"{status}"
    )


# =========================================================
# FINAL PERFORMANCE
# =========================================================

attack_rounds = tp + fn
genuine_rounds = tn + fp

if attack_rounds > 0:

    detection_rate = (
        tp / attack_rounds
    ) * 100

    false_acceptance_rate = (
        fn / attack_rounds
    ) * 100

else:

    detection_rate = 0
    false_acceptance_rate = 0


if genuine_rounds > 0:

    false_rejection_rate = (
        fp / genuine_rounds
    ) * 100

else:

    false_rejection_rate = 0


print("\n")
print("=" * 80)
print("QDS PROTOCOL PERFORMANCE")
print("=" * 80)

print("\nConfusion Matrix")

print("True Positive (TP)   :", tp)
print("False Negative (FN)  :", fn)
print("True Negative (TN)   :", tn)
print("False Positive (FP)  :", fp)

print("\nPerformance")

print(
    f"Detection Rate       : {detection_rate:.2f}%"
)

print(
    f"False Acceptance Rate: {false_acceptance_rate:.2f}%"
)

print(
    f"False Rejection Rate : {false_rejection_rate:.2f}%"
)

print("\n" + "=" * 80)

if detection_rate >= 50:

    print(
        "FINAL DECISION: "
        "QDS THREAT DETECTION SUCCESSFUL"
    )

else:

    print(
        "FINAL DECISION: "
        "FURTHER VERIFICATION REQUIRED"
    )

print("=" * 80)