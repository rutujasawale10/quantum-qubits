from qiskit import QuantumCircuit
from qiskit.primitives import StatevectorSampler
import random


# =========================================================
# QDS THREAT MODEL
# Partial Interception + Channel Noise + Threat Score
# =========================================================

ROUNDS = 30
COPIES = 100

INTERCEPTION_PROBABILITY = 0.30
NOISE_PROBABILITY = 0.05

LOW_THRESHOLD = 0.10
HIGH_THRESHOLD = 0.25

STATES = ["0", "1", "+", "-"]


# =========================================================
# CREATE QUANTUM SIGNATURE
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
# SELECT CORRECT BASIS
# =========================================================

def get_basis(state_name):

    if state_name in ["0", "1"]:
        return "Z"

    return "X"


# =========================================================
# EXPECTED RESULT
# =========================================================

def get_expected_result(state_name):

    if state_name == "0":
        return "0"

    elif state_name == "1":
        return "1"

    elif state_name == "+":
        return "0"

    elif state_name == "-":
        return "1"


# =========================================================
# PARTIAL INTERCEPTION ATTACK
# =========================================================

def apply_partial_attack(qc):

    attacked = qc.copy()

    intercepted = False

    if random.random() < INTERCEPTION_PROBABILITY:

        intercepted = True

        attack = random.choice(["X", "Z"])

        if attack == "X":
            attacked.x(0)

        elif attack == "Z":
            attacked.z(0)

    return attacked, intercepted


# =========================================================
# CHANNEL NOISE
# =========================================================

def apply_noise(qc):

    noisy = qc.copy()

    noisy_state = False

    if random.random() < NOISE_PROBABILITY:

        noisy_state = True

        noise = random.choice(["X", "Z"])

        if noise == "X":
            noisy.x(0)

        elif noise == "Z":
            noisy.z(0)

    return noisy, noisy_state


# =========================================================
# MEASURE ONE COPY
# =========================================================

def measure_copy(state_name, basis):

    qc = create_state(state_name)

    # Partial interception
    qc, intercepted = apply_partial_attack(qc)

    # Channel noise
    qc, noisy = apply_noise(qc)

    # X-basis measurement
    if basis == "X":
        qc.h(0)

    qc.measure_all()

    sampler = StatevectorSampler()

    result = sampler.run(
        [qc],
        shots=1
    ).result()

    counts = result[0].data.meas.get_counts()

    measured_value = list(counts.keys())[0]

    return measured_value, intercepted, noisy


# =========================================================
# RUN ONE VERIFICATION ROUND
# =========================================================

def run_round(state_name):

    basis = get_basis(state_name)

    expected = get_expected_result(state_name)

    correct = 0
    errors = 0

    intercepted_count = 0
    noise_count = 0

    for _ in range(COPIES):

        measured, intercepted, noisy = measure_copy(
            state_name,
            basis
        )

        if measured == expected:
            correct += 1
        else:
            errors += 1

        if intercepted:
            intercepted_count += 1

        if noisy:
            noise_count += 1

    error_rate = errors / COPIES

    interception_rate = intercepted_count / COPIES

    noise_rate = noise_count / COPIES

    return (
        basis,
        expected,
        correct,
        errors,
        error_rate,
        interception_rate,
        noise_rate
    )


# =========================================================
# THREAT SCORE
# =========================================================

def calculate_threat_score(
    error_rate,
    interception_rate,
    noise_rate
):

    # Weighted score
    score = (
        0.60 * error_rate
        + 0.30 * interception_rate
        + 0.10 * noise_rate
    )

    return score


# =========================================================
# THREAT LEVEL
# =========================================================

def get_threat_level(score):

    if score >= HIGH_THRESHOLD:

        return "HIGH"

    elif score >= LOW_THRESHOLD:

        return "MEDIUM"

    else:

        return "LOW"


# =========================================================
# MAIN EXPERIMENT
# =========================================================

print("=" * 85)
print("QUANTUM DIGITAL SIGNATURE CYBER THREAT MODEL")
print("=" * 85)

print("Rounds                  :", ROUNDS)
print("Copies per Round       :", COPIES)
print(
    "Interception Probability:",
    INTERCEPTION_PROBABILITY
)
print(
    "Channel Noise Probability:",
    NOISE_PROBABILITY
)

print("=" * 85)


total_error = 0
total_interception = 0
total_noise = 0

high_threat = 0
medium_threat = 0
low_threat = 0


# =========================================================
# RUN MULTIPLE ROUNDS
# =========================================================

for round_no in range(1, ROUNDS + 1):

    state = random.choice(STATES)

    (
        basis,
        expected,
        correct,
        errors,
        error_rate,
        interception_rate,
        noise_rate
    ) = run_round(state)


    score = calculate_threat_score(
        error_rate,
        interception_rate,
        noise_rate
    )

    threat_level = get_threat_level(score)


    total_error += error_rate
    total_interception += interception_rate
    total_noise += noise_rate


    if threat_level == "HIGH":
        high_threat += 1

    elif threat_level == "MEDIUM":
        medium_threat += 1

    else:
        low_threat += 1


    print(
        f"Round {round_no:02d} | "
        f"State={state:>2} | "
        f"Basis={basis} | "
        f"Error={error_rate:.2f} | "
        f"Intercept={interception_rate:.2f} | "
        f"Noise={noise_rate:.2f} | "
        f"Score={score:.2f} | "
        f"Threat={threat_level}"
    )


# =========================================================
# AVERAGES
# =========================================================

average_error = total_error / ROUNDS

average_interception = (
    total_interception / ROUNDS
)

average_noise = (
    total_noise / ROUNDS
)

average_score = (
    0.60 * average_error
    + 0.30 * average_interception
    + 0.10 * average_noise
)


# =========================================================
# FINAL REPORT
# =========================================================

print("\n")

print("=" * 85)
print("FINAL QUANTUM THREAT ANALYSIS")
print("=" * 85)

print("\n--- AVERAGE CHANNEL STATISTICS ---")

print(
    f"Average Error Rate       : "
    f"{average_error:.2%}"
)

print(
    f"Average Interception Rate: "
    f"{average_interception:.2%}"
)

print(
    f"Average Noise Rate       : "
    f"{average_noise:.2%}"
)

print(
    f"Average Threat Score     : "
    f"{average_score:.2f}"
)


print("\n--- THREAT DISTRIBUTION ---")

print(
    "HIGH Threat Rounds       :",
    high_threat
)

print(
    "MEDIUM Threat Rounds     :",
    medium_threat
)

print(
    "LOW Threat Rounds        :",
    low_threat
)


print("\n" + "=" * 85)


if average_score >= HIGH_THRESHOLD:

    print(
        "FINAL DECISION: "
        "HIGH QUANTUM CYBER THREAT DETECTED"
    )

elif average_score >= LOW_THRESHOLD:

    print(
        "FINAL DECISION: "
        "MEDIUM QUANTUM CYBER THREAT DETECTED"
    )

else:

    print(
        "FINAL DECISION: "
        "LOW THREAT / CHANNEL ACCEPTABLE"
    )


print("=" * 85)