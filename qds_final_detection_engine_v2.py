from qiskit import QuantumCircuit
from qiskit.primitives import StatevectorSampler
import random

# ==========================================
# CONFIGURATION
# ==========================================

ROUNDS = 100
COPIES = 20
THRESHOLD = 0.20

STATES = ["0", "1", "+", "-"]


# ==========================================
# CREATE QUANTUM STATE
# ==========================================

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

    return qc


# ==========================================
# APPLY ATTACK
# ==========================================

def apply_attack(state_name, attack):

    qc = create_state(state_name)

    if attack == "X":
        qc.x(0)

    elif attack == "Z":
        qc.z(0)

    return qc


# ==========================================
# MEASURE
# ==========================================

def measure_state(state_name, attack, basis, shots):

    qc = apply_attack(state_name, attack)

    # X basis measurement
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


# ==========================================
# EXPECTED RESULT
# ==========================================

def expected_result(state_name):

    if state_name == "0":
        return "0"

    elif state_name == "1":
        return "1"

    elif state_name == "+":
        return "0"

    elif state_name == "-":
        return "1"


# ==========================================
# CORRECT BASIS
# ==========================================

def correct_basis(state_name):

    if state_name in ["0", "1"]:
        return "Z"

    else:
        return "X"


# ==========================================
# ERROR RATE
# ==========================================

def calculate_error(counts, expected, shots):

    wrong = 0

    for result, count in counts.items():

        if result != expected:
            wrong += count

    return wrong / shots


# ==========================================
# MAIN ENGINE
# ==========================================

tp = 0
tn = 0
fp = 0
fn = 0

total_error = 0

x_attack_total = 0
z_attack_total = 0

x_detected = 0
z_detected = 0


print("=" * 70)
print("QDS MULTI-COPY QUANTUM THREAT DETECTION ENGINE V2")
print("=" * 70)

print("Total Rounds :", ROUNDS)
print("Copies       :", COPIES)
print("Threshold    :", THRESHOLD)

print("=" * 70)


# ==========================================
# RUN ROUNDS
# ==========================================

for round_no in range(1, ROUNDS + 1):

    # Random quantum state
    state = random.choice(STATES)

    # Correct verification basis
    basis = correct_basis(state)

    # Randomly decide whether attack exists
    if random.random() < 0.50:

        attack = random.choice(["X", "Z"])

    else:

        attack = "NONE"


    # Expected result
    expected = expected_result(state)


    # Measure multiple copies
    counts = measure_state(
        state,
        attack,
        basis,
        COPIES
    )


    # Calculate error
    error_rate = calculate_error(
        counts,
        expected,
        COPIES
    )


    total_error += error_rate


    # Threat decision
    if error_rate > THRESHOLD:
        threat = True
    else:
        threat = False


    # ======================================
    # CONFUSION MATRIX
    # ======================================

    if attack == "NONE":

        if threat:
            fp += 1
        else:
            tn += 1

    else:

        if attack == "X":
            x_attack_total += 1

        elif attack == "Z":
            z_attack_total += 1


        if threat:

            tp += 1

            if attack == "X":
                x_detected += 1

            elif attack == "Z":
                z_detected += 1

        else:

            fn += 1


    # ======================================
    # DISPLAY FIRST 20 ROUNDS
    # ======================================

    if round_no <= 20:

        result = "THREAT" if threat else "NORMAL"

        print(
            f"Round {round_no:03d} | "
            f"State={state:>2} | "
            f"Basis={basis} | "
            f"Attack={attack:>4} | "
            f"Error={error_rate:.2f} | "
            f"{result}"
        )


# ==========================================
# METRICS
# ==========================================

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


average_error = total_error / ROUNDS


if x_attack_total > 0:

    x_detection_rate = (
        x_detected / x_attack_total
    ) * 100

else:

    x_detection_rate = 0


if z_attack_total > 0:

    z_detection_rate = (
        z_detected / z_attack_total
    ) * 100

else:

    z_detection_rate = 0


# ==========================================
# FINAL REPORT
# ==========================================

print("\n")
print("=" * 70)
print("FINAL QDS DETECTION REPORT")
print("=" * 70)

print(f"Total Rounds          : {ROUNDS}")
print(f"Copies per Round     : {COPIES}")

print("\n--- CONFUSION MATRIX ---")

print(f"True Positive (TP)   : {tp}")
print(f"False Negative (FN)  : {fn}")
print(f"True Negative (TN)   : {tn}")
print(f"False Positive (FP)  : {fp}")

print("\n--- PERFORMANCE ---")

print(
    f"Detection Rate       : "
    f"{detection_rate:.2f}%"
)

print(
    f"False Acceptance Rate: "
    f"{false_acceptance_rate:.2f}%"
)

print(
    f"False Rejection Rate : "
    f"{false_rejection_rate:.2f}%"
)

print(
    f"Average Error Rate   : "
    f"{average_error:.2%}"
)

print("\n--- ATTACK ANALYSIS ---")

print(
    f"X Attack Rounds      : "
    f"{x_attack_total}"
)

print(
    f"X Detection Rate     : "
    f"{x_detection_rate:.2f}%"
)

print(
    f"Z Attack Rounds      : "
    f"{z_attack_total}"
)

print(
    f"Z Detection Rate     : "
    f"{z_detection_rate:.2f}%"
)

print("=" * 70)


if tp > 0:

    print("FINAL DECISION: QUANTUM THREAT ANALYSIS COMPLETED")

else:

    print("FINAL DECISION: NO THREAT DETECTED")


print("=" * 70)