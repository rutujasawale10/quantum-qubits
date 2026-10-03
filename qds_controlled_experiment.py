from qiskit import QuantumCircuit
from qiskit.primitives import StatevectorSampler
import random


# =========================================================
# CONFIGURATION
# =========================================================

ROUNDS = 100
COPIES = 100

ERROR_THRESHOLD = 0.20

STATES = ["0", "1", "+", "-"]
ATTACKS = ["NONE", "X", "Z"]


# =========================================================
# CREATE QUANTUM STATE
# =========================================================

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


# =========================================================
# CORRECT VERIFICATION BASIS
# =========================================================

def get_basis(state_name):

    if state_name in ["0", "1"]:
        return "Z"

    return "X"


# =========================================================
# APPLY ATTACK
# =========================================================

def apply_attack(state_circuit, attack):

    qc = state_circuit.copy()

    if attack == "X":
        qc.x(0)

    elif attack == "Z":
        qc.z(0)

    return qc


# =========================================================
# EXPECTED MEASUREMENT RESULT
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
# MEASURE
# =========================================================

def measure_state(
    state_circuit,
    attack,
    basis,
    shots
):

    qc = apply_attack(
        state_circuit,
        attack
    )

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
# CALCULATE ERROR RATE
# =========================================================

def calculate_error_rate(
    counts,
    expected,
    shots
):

    correct = counts.get(
        expected,
        0
    )

    error_count = shots - correct

    return error_count / shots


# =========================================================
# COUNTERS
# =========================================================

genuine_rounds = 0
attack_rounds = 0

tp = 0
tn = 0
fp = 0
fn = 0

x_total = 0
z_total = 0

x_detected = 0
z_detected = 0

total_error = 0


# =========================================================
# HEADER
# =========================================================

print("=" * 75)
print("CONTROLLED QDS THREAT DETECTION EXPERIMENT")
print("=" * 75)

print("Total Rounds       :", ROUNDS)
print("Copies per Round  :", COPIES)
print("Error Threshold   :", ERROR_THRESHOLD)

print("=" * 75)


# =========================================================
# CONTROLLED EXPERIMENT
# =========================================================

for round_no in range(
    1,
    ROUNDS + 1
):

    # -----------------------------------------------------
    # Select state
    # -----------------------------------------------------

    state_name = random.choice(
        STATES
    )

    state_circuit = create_state(
        state_name
    )

    # -----------------------------------------------------
    # ALWAYS USE CORRECT BASIS
    # -----------------------------------------------------

    basis = get_basis(
        state_name
    )

    # -----------------------------------------------------
    # 50% genuine / 50% attack
    # -----------------------------------------------------

    if round_no % 2 == 0:

        attack = random.choice(
            ["X", "Z"]
        )

        attack_rounds += 1

    else:

        attack = "NONE"

        genuine_rounds += 1


    # -----------------------------------------------------
    # Attack counters
    # -----------------------------------------------------

    if attack == "X":
        x_total += 1

    elif attack == "Z":
        z_total += 1


    # -----------------------------------------------------
    # Expected result
    # -----------------------------------------------------

    expected = expected_result(
        state_name
    )


    # -----------------------------------------------------
    # Measure multiple copies
    # -----------------------------------------------------

    counts = measure_state(
        state_circuit,
        attack,
        basis,
        COPIES
    )


    # -----------------------------------------------------
    # Error rate
    # -----------------------------------------------------

    error_rate = calculate_error_rate(
        counts,
        expected,
        COPIES
    )

    total_error += error_rate


    # -----------------------------------------------------
    # Decision
    # -----------------------------------------------------

    if error_rate > ERROR_THRESHOLD:

        threat = True

    else:

        threat = False


    # -----------------------------------------------------
    # CONFUSION MATRIX
    # -----------------------------------------------------

    if attack == "NONE":

        if threat:

            fp += 1

        else:

            tn += 1

    else:

        if threat:

            tp += 1

            if attack == "X":
                x_detected += 1

            elif attack == "Z":
                z_detected += 1

        else:

            fn += 1


    # -----------------------------------------------------
    # DISPLAY FIRST 30 ROUNDS
    # -----------------------------------------------------

    if round_no <= 30:

        result = (
            "THREAT"
            if threat
            else
            "VALID"
        )

        print(
            f"Round {round_no:03d} | "
            f"State={state_name:>2} | "
            f"Basis={basis} | "
            f"Attack={attack:>4} | "
            f"Error={error_rate:.2f} | "
            f"{result}"
        )


# =========================================================
# METRICS
# =========================================================

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


average_error = (
    total_error / ROUNDS
)


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


# =========================================================
# FINAL REPORT
# =========================================================

print("\n")

print("=" * 75)
print("CONTROLLED QDS EXPERIMENT REPORT")
print("=" * 75)

print("\n--- ROUND SUMMARY ---")

print(
    f"Genuine Rounds       : "
    f"{genuine_rounds}"
)

print(
    f"Attack Rounds        : "
    f"{attack_rounds}"
)

print(
    f"X Attack Rounds      : "
    f"{x_total}"
)

print(
    f"Z Attack Rounds      : "
    f"{z_total}"
)


print("\n--- CONFUSION MATRIX ---")

print(
    f"True Positive (TP)   : "
    f"{tp}"
)

print(
    f"False Negative (FN)  : "
    f"{fn}"
)

print(
    f"True Negative (TN)   : "
    f"{tn}"
)

print(
    f"False Positive (FP)  : "
    f"{fp}"
)


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


print("\n--- ATTACK-WISE DETECTION ---")

print(
    f"X Detection Rate     : "
    f"{x_detection_rate:.2f}%"
)

print(
    f"Z Detection Rate     : "
    f"{z_detection_rate:.2f}%"
)


print("\n" + "=" * 75)

if detection_rate >= 50:

    print(
        "FINAL DECISION: "
        "ATTACK DETECTION SUCCESSFUL"
    )

else:

    print(
        "FINAL DECISION: "
        "FURTHER PROTOCOL IMPROVEMENT REQUIRED"
    )

print("=" * 75)