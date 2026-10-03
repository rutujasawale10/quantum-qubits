from qiskit import QuantumCircuit
from qiskit.quantum_info import Statevector
from qiskit.primitives import StatevectorSampler
import random
import math

# ==========================================
# CONFIGURATION
# ==========================================

ROUNDS = 100
COPIES = 20
THRESHOLD = 0.20

ATTACKS = ["NONE", "X", "Z"]


# ==========================================
# CREATE RANDOM QUANTUM STATE
# ==========================================

def create_random_state():

    theta = random.uniform(0, math.pi)
    phi = random.uniform(0, 2 * math.pi)

    qc = QuantumCircuit(1)

    qc.ry(theta, 0)
    qc.rz(phi, 0)

    return qc, theta, phi


# ==========================================
# APPLY ATTACK
# ==========================================

def apply_attack(state_circuit, attack):

    qc = state_circuit.copy()

    if attack == "X":
        qc.x(0)

    elif attack == "Z":
        qc.z(0)

    return qc


# ==========================================
# MEASURE QUANTUM STATE
# ==========================================

def measure_state(state_circuit, attack, basis, shots):

    qc = apply_attack(state_circuit, attack)

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


# ==========================================
# GET EXPECTED PROBABILITY
# ==========================================

def get_expected_probability(state_circuit, basis):

    state = Statevector.from_instruction(state_circuit)

    if basis == "X":

        # Convert state to X basis
        qc = QuantumCircuit(1)
        qc.h(0)

        x_state = state.evolve(qc)

        probabilities = x_state.probabilities()

    else:

        probabilities = state.probabilities()

    return probabilities


# ==========================================
# CHI-SQUARE TEST
# ==========================================

def chi_square(observed, expected, shots):

    chi = 0.0

    for i in range(2):

        key = str(i)

        observed_count = observed.get(key, 0)
        expected_count = expected[i] * shots

        if expected_count > 0:

            chi += (
                (observed_count - expected_count) ** 2
            ) / expected_count

    return chi


# ==========================================
# ERROR RATE
# ==========================================

def calculate_error(observed, expected, shots):

    error = 0.0

    for i in range(2):

        key = str(i)

        observed_probability = (
            observed.get(key, 0) / shots
        )

        error += abs(
            observed_probability - expected[i]
        )

    return error / 2


# ==========================================
# MAIN ENGINE
# ==========================================

tp = 0
tn = 0
fp = 0
fn = 0

total_error = 0
total_chi = 0

x_attacks = 0
z_attacks = 0

x_detected = 0
z_detected = 0


print("=" * 75)
print("RANDOM QUANTUM STATE QDS DETECTION ENGINE")
print("=" * 75)

print("Total Rounds :", ROUNDS)
print("Copies       :", COPIES)
print("Threshold    :", THRESHOLD)
print("Attacks      :", ATTACKS)

print("=" * 75)


# ==========================================
# RUN ROUNDS
# ==========================================

for round_no in range(1, ROUNDS + 1):

    # Create random quantum state
    state_circuit, theta, phi = create_random_state()

    # Random verification basis
    basis = random.choice(["Z", "X"])

    # Random attack
    if random.random() < 0.50:

        attack = random.choice(["X", "Z"])

    else:

        attack = "NONE"


    # Expected probability WITHOUT attack
    expected = get_expected_probability(
        state_circuit,
        basis
    )


    # Measure received state
    observed = measure_state(
        state_circuit,
        attack,
        basis,
        COPIES
    )


    # Calculate error
    error_rate = calculate_error(
        observed,
        expected,
        COPIES
    )


    # Calculate chi-square
    chi = chi_square(
        observed,
        expected,
        COPIES
    )


    total_error += error_rate
    total_chi += chi


    # Threat decision
    threat = error_rate > THRESHOLD


    # ======================================
    # ATTACK STATISTICS
    # ======================================

    if attack == "X":
        x_attacks += 1

    elif attack == "Z":
        z_attacks += 1


    # ======================================
    # CONFUSION MATRIX
    # ======================================

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


    # ======================================
    # PRINT FIRST 20 ROUNDS
    # ======================================

    if round_no <= 20:

        result = "THREAT" if threat else "NORMAL"

        print(
            f"Round {round_no:03d} | "
            f"Basis={basis} | "
            f"Attack={attack:>4} | "
            f"Error={error_rate:.3f} | "
            f"Chi={chi:.2f} | "
            f"{result}"
        )


# ==========================================
# CALCULATE METRICS
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
average_chi = total_chi / ROUNDS


if x_attacks > 0:

    x_detection_rate = (
        x_detected / x_attacks
    ) * 100

else:

    x_detection_rate = 0


if z_attacks > 0:

    z_detection_rate = (
        z_detected / z_attacks
    ) * 100

else:

    z_detection_rate = 0


# ==========================================
# FINAL REPORT
# ==========================================

print("\n")
print("=" * 75)
print("FINAL RANDOM-STATE QDS REPORT")
print("=" * 75)

print(f"Total Rounds           : {ROUNDS}")
print(f"Copies per Round      : {COPIES}")

print("\n--- CONFUSION MATRIX ---")

print(f"True Positive (TP)    : {tp}")
print(f"False Negative (FN)   : {fn}")
print(f"True Negative (TN)    : {tn}")
print(f"False Positive (FP)   : {fp}")

print("\n--- PERFORMANCE ---")

print(
    f"Detection Rate        : "
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
    f"Average Error Rate    : "
    f"{average_error:.2%}"
)

print(
    f"Average Chi-Square    : "
    f"{average_chi:.2f}"
)

print("\n--- ATTACK ANALYSIS ---")

print(
    f"X Attack Rounds       : "
    f"{x_attacks}"
)

print(
    f"X Detection Rate      : "
    f"{x_detection_rate:.2f}%"
)

print(
    f"Z Attack Rounds       : "
    f"{z_attacks}"
)

print(
    f"Z Detection Rate      : "
    f"{z_detection_rate:.2f}%"
)

print("=" * 75)

if detection_rate > 50:

    print("FINAL DECISION: QUANTUM THREAT DETECTED")

else:

    print("FINAL DECISION: MORE VERIFICATION REQUIRED")

print("=" * 75)