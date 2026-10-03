from qiskit import QuantumCircuit
from qiskit.quantum_info import Statevector
from qiskit.primitives import StatevectorSampler
import random
import math


# =========================================================
# CONFIGURATION
# =========================================================

ROUNDS = 100
COPIES = 100

# Error threshold
ERROR_THRESHOLD = 0.15

# Chi-square threshold
CHI_THRESHOLD = 3.84

STATES = ["0", "1", "+", "-"]
BASES = ["Z", "X"]
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
# GET THEORETICAL PROBABILITY
# =========================================================

def get_probabilities(state_circuit, basis):

    state = Statevector.from_instruction(state_circuit)

    if basis == "X":

        transform = QuantumCircuit(1)
        transform.h(0)

        state = state.evolve(transform)

    probabilities = state.probabilities()

    return probabilities


# =========================================================
# MEASURE QUANTUM STATE
# =========================================================

def measure_state(state_circuit, attack, basis, shots):

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
# CHI-SQUARE TEST
# =========================================================

def calculate_chi_square(
    observed,
    expected_probabilities,
    shots
):

    chi = 0.0

    for i in range(2):

        key = str(i)

        observed_value = observed.get(
            key,
            0
        )

        expected_value = (
            expected_probabilities[i] * shots
        )

        # Avoid division by zero
        if expected_value > 0.000001:

            chi += (
                (observed_value - expected_value) ** 2
            ) / expected_value

    return chi


# =========================================================
# ERROR RATE
# =========================================================

def calculate_error_rate(
    observed,
    expected_probabilities,
    shots
):

    observed_probability_0 = (
        observed.get("0", 0) / shots
    )

    observed_probability_1 = (
        observed.get("1", 0) / shots
    )

    error = (
        abs(
            observed_probability_0
            - expected_probabilities[0]
        )
        +
        abs(
            observed_probability_1
            - expected_probabilities[1]
        )
    ) / 2

    return error


# =========================================================
# MAIN ENGINE
# =========================================================

tp = 0
tn = 0
fp = 0
fn = 0

total_error = 0
total_chi = 0

x_total = 0
z_total = 0

x_detected = 0
z_detected = 0


print("=" * 75)
print("ROBUST MULTI-COPY QDS THREAT DETECTION ENGINE")
print("=" * 75)

print("Rounds           :", ROUNDS)
print("Copies/Round     :", COPIES)
print("Error Threshold  :", ERROR_THRESHOLD)
print("Chi-Square Limit :", CHI_THRESHOLD)

print("=" * 75)


# =========================================================
# RUN EXPERIMENTS
# =========================================================

for round_no in range(1, ROUNDS + 1):

    # -----------------------------------------------------
    # Choose quantum state
    # -----------------------------------------------------

    state_name = random.choice(STATES)

    state_circuit = create_state(
        state_name
    )


    # -----------------------------------------------------
    # Choose verification basis
    # -----------------------------------------------------

    basis = random.choice(BASES)


    # -----------------------------------------------------
    # Choose attack
    # -----------------------------------------------------

    if random.random() < 0.50:

        attack = random.choice(
            ["X", "Z"]
        )

    else:

        attack = "NONE"


    # -----------------------------------------------------
    # Expected distribution
    # -----------------------------------------------------

    expected = get_probabilities(
        state_circuit,
        basis
    )


    # -----------------------------------------------------
    # Measurement
    # -----------------------------------------------------

    observed = measure_state(
        state_circuit,
        attack,
        basis,
        COPIES
    )


    # -----------------------------------------------------
    # Statistics
    # -----------------------------------------------------

    error_rate = calculate_error_rate(
        observed,
        expected,
        COPIES
    )

    chi = calculate_chi_square(
        observed,
        expected,
        COPIES
    )


    total_error += error_rate
    total_chi += chi


    # -----------------------------------------------------
    # Threat decision
    # -----------------------------------------------------

    threat_by_error = (
        error_rate > ERROR_THRESHOLD
    )

    threat_by_chi = (
        chi > CHI_THRESHOLD
    )

    threat = (
        threat_by_error
        or
        threat_by_chi
    )


    # -----------------------------------------------------
    # Attack statistics
    # -----------------------------------------------------

    if attack == "X":

        x_total += 1

    elif attack == "Z":

        z_total += 1


    # -----------------------------------------------------
    # Confusion Matrix
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
    # Display first 20 rounds
    # -----------------------------------------------------

    if round_no <= 20:

        result = (
            "THREAT"
            if threat
            else
            "NORMAL"
        )

        print(
            f"Round {round_no:03d} | "
            f"State={state_name:>2} | "
            f"Basis={basis} | "
            f"Attack={attack:>4} | "
            f"Error={error_rate:.3f} | "
            f"Chi={chi:.2f} | "
            f"{result}"
        )


# =========================================================
# PERFORMANCE METRICS
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


average_error = (
    total_error / ROUNDS
)

average_chi = (
    total_chi / ROUNDS
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
print("FINAL QDS SECURITY REPORT")
print("=" * 75)

print("\n--- EXPERIMENT ---")

print(
    f"Total Rounds        : {ROUNDS}"
)

print(
    f"Copies per Round   : {COPIES}"
)

print(
    f"Average Error Rate : {average_error:.2%}"
)

print(
    f"Average Chi-Square : {average_chi:.2f}"
)


print("\n--- CONFUSION MATRIX ---")

print(
    f"True Positive (TP)  : {tp}"
)

print(
    f"False Negative (FN) : {fn}"
)

print(
    f"True Negative (TN)  : {tn}"
)

print(
    f"False Positive (FP) : {fp}"
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


print("\n--- ATTACK ANALYSIS ---")

print(
    f"X Attack Rounds     : "
    f"{x_total}"
)

print(
    f"X Detection Rate    : "
    f"{x_detection_rate:.2f}%"
)

print(
    f"Z Attack Rounds     : "
    f"{z_total}"
)

print(
    f"Z Detection Rate    : "
    f"{z_detection_rate:.2f}%"
)


print("\n" + "=" * 75)

if tp > 0:

    print(
        "FINAL DECISION: "
        "QUANTUM THREAT ANALYSIS COMPLETED"
    )

else:

    print(
        "FINAL DECISION: "
        "NO THREAT DETECTED"
    )

print("=" * 75)