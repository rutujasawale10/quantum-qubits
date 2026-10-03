from qiskit import QuantumCircuit
from qiskit.primitives import StatevectorSampler
import random

# ==============================
# CONFIGURATION
# ==============================

ROUNDS = 100
COPIES = 100
ERROR_THRESHOLD = 0.20

STATES = ["0", "1", "+", "-"]
ATTACKS = ["NONE", "X", "Z"]


# ==============================
# CREATE QUANTUM STATE
# ==============================

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


# ==============================
# APPLY ATTACK
# ==============================

def apply_attack(qc, attack):

    circuit = qc.copy()

    if attack == "X":
        circuit.x(0)

    elif attack == "Z":
        circuit.z(0)

    return circuit


# ==============================
# MEASUREMENT
# ==============================

def measure_state(qc, attack, basis, shots):

    circuit = apply_attack(qc, attack)

    # X basis measurement
    if basis == "X":
        circuit.h(0)

    circuit.measure_all()

    sampler = StatevectorSampler()

    result = sampler.run(
        [circuit],
        shots=shots
    ).result()

    counts = result[0].data.meas.get_counts()

    return counts


# ==============================
# EXPECTED RESULT
# ==============================

def expected_result(state):

    if state == "0":
        return "0"

    elif state == "1":
        return "1"

    elif state == "+":
        return "0"

    elif state == "-":
        return "1"


# ==============================
# CORRECT BASIS
# ==============================

def correct_basis(state):

    if state in ["0", "1"]:
        return "Z"

    else:
        return "X"


# ==============================
# MAIN EXPERIMENT
# ==============================

tp = 0
tn = 0
fp = 0
fn = 0

genuine_rounds = 0
attack_rounds = 0

x_total = 0
z_total = 0

x_detected = 0
z_detected = 0

total_error = 0


print("=" * 80)
print("ADVANCED QUANTUM DIGITAL SIGNATURE THREAT DETECTION")
print("=" * 80)

print("Total Rounds      :", ROUNDS)
print("Copies per Round :", COPIES)
print("Error Threshold  :", ERROR_THRESHOLD)

print("=" * 80)


# ==============================
# ROUND LOOP
# ==============================

for round_no in range(1, ROUNDS + 1):

    # Random quantum state
    state = random.choice(STATES)

    # Correct verification basis
    basis = correct_basis(state)

    # Half genuine, half attack
    if round_no % 2 == 0:

        attack = random.choice(["X", "Z"])
        attack_rounds += 1

    else:

        attack = "NONE"
        genuine_rounds += 1


    # Count attack types
    if attack == "X":
        x_total += 1

    elif attack == "Z":
        z_total += 1


    # Create original state
    state_circuit = create_state(state)

    # Expected measurement
    expected = expected_result(state)


    # Measure multiple copies
    counts = measure_state(
        state_circuit,
        attack,
        basis,
        COPIES
    )


    # Calculate disturbance
    correct = counts.get(expected, 0)

    errors = COPIES - correct

    error_rate = errors / COPIES

    total_error += error_rate


    # Threat decision
    if error_rate > ERROR_THRESHOLD:

        threat = True

    else:

        threat = False


    # ==============================
    # CONFUSION MATRIX
    # ==============================

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


    # ==============================
    # DISPLAY FIRST 30 ROUNDS
    # ==============================

    if round_no <= 30:

        result = "THREAT" if threat else "VALID"

        print(
            f"Round {round_no:03d} | "
            f"State={state:>2} | "
            f"Basis={basis} | "
            f"Attack={attack:>4} | "
            f"Error={error_rate:.2f} | "
            f"{result}"
        )


# ==============================
# PERFORMANCE
# ==============================

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
) * 100


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


# ==============================
# FINAL REPORT
# ==============================

print("\n")

print("=" * 80)
print("ADVANCED QDS DETECTION REPORT")
print("=" * 80)


print("\n--- ROUND SUMMARY ---")

print("Genuine Rounds       :", genuine_rounds)
print("Attack Rounds        :", attack_rounds)
print("X Attack Rounds      :", x_total)
print("Z Attack Rounds      :", z_total)


print("\n--- CONFUSION MATRIX ---")

print("True Positive (TP)   :", tp)
print("False Negative (FN)  :", fn)
print("True Negative (TN)   :", tn)
print("False Positive (FP)  :", fp)


print("\n--- PERFORMANCE ---")

print(
    f"Detection Rate       : {detection_rate:.2f}%"
)

print(
    f"False Acceptance Rate: {false_acceptance_rate:.2f}%"
)

print(
    f"False Rejection Rate : {false_rejection_rate:.2f}%"
)

print(
    f"Average Error Rate   : {average_error:.2f}%"
)


print("\n--- ATTACK-WISE DETECTION ---")

print(
    f"X Detection Rate     : {x_detection_rate:.2f}%"
)

print(
    f"Z Detection Rate     : {z_detection_rate:.2f}%"
)


print("\n" + "=" * 80)


if detection_rate >= 50:

    print(
        "FINAL DECISION: "
        "QUANTUM THREAT DETECTION SUCCESSFUL"
    )

else:

    print(
        "FINAL DECISION: "
        "FURTHER PROTOCOL IMPROVEMENT REQUIRED"
    )


print("=" * 80)