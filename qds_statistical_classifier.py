from qiskit import QuantumCircuit
from qiskit.primitives import StatevectorSampler
import random
import math

# ==============================
# PARAMETERS
# ==============================

ROUNDS = 30
COPIES = 200

# Normal channel noise
NOISE_PROBABILITY = 0.05

# Statistical thresholds
NORMAL_ERROR_LIMIT = 0.10
ATTACK_ERROR_LIMIT = 0.50

# ==============================
# STATE CREATION
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
    if attack == "X":
        qc.x(0)

    elif attack == "Z":
        qc.z(0)

    return qc


# ==============================
# APPLY RANDOM CHANNEL NOISE
# ==============================

def apply_noise(qc):
    noise_happened = False

    if random.random() < NOISE_PROBABILITY:
        qc.x(0)
        noise_happened = True

    return noise_happened


# ==============================
# MEASUREMENT
# ==============================

def measure_state(state_name, attack, basis, copies):

    counts = {"0": 0, "1": 0}
    noise_count = 0

    for _ in range(copies):

        qc = create_state(state_name)

        # Apply actual attack
        apply_attack(qc, attack)

        # Apply channel noise
        if apply_noise(qc):
            noise_count += 1

        # Measurement basis
        if basis == "X":
            qc.h(0)

        qc.measure_all()

        sampler = StatevectorSampler()
        result = sampler.run([qc], shots=1).result()

        measured = list(
            result[0].data.meas.get_counts().keys()
        )[0]

        counts[measured] += 1

    return counts, noise_count


# ==============================
# EXPECTED RESULT
# ==============================

def expected_result(state_name):
    if state_name in ["0", "+"]:
        return "0"

    elif state_name in ["1", "-"]:
        return "1"


# ==============================
# STATISTICAL ERROR
# ==============================

def calculate_error(counts, expected, copies):

    wrong_result = "1" if expected == "0" else "0"

    wrong_count = counts.get(wrong_result, 0)

    return wrong_count / copies


# ==============================
# BINOMIAL Z-SCORE
# ==============================

def calculate_z_score(error_rate, baseline, copies):

    # Standard deviation of binomial distribution
    variance = baseline * (1 - baseline) / copies

    if variance == 0:
        return 0

    std = math.sqrt(variance)

    return (error_rate - baseline) / std


# ==============================
# CLASSIFICATION
# ==============================

def classify(error_rate, noise_rate, z_score, basis):

    # Strong disturbance
    if error_rate >= ATTACK_ERROR_LIMIT:

        if basis == "Z":
            return "X / BIT-FLIP ATTACK"

        elif basis == "X":
            return "Z / PHASE-FLIP ATTACK"

    # Compare with normal noise level
    if z_score > 3:

        return "ABNORMAL CHANNEL DISTURBANCE"

    # Normal condition
    if error_rate < NORMAL_ERROR_LIMIT:

        return "NORMAL"

    return "POSSIBLE CHANNEL NOISE"


# ==============================
# MAIN EXPERIMENT
# ==============================

states = ["0", "1", "+", "-"]
attacks = ["NONE", "X", "Z", "NOISE"]

normal_count = 0
x_attack_count = 0
z_attack_count = 0
noise_count_total = 0
disturbance_count = 0

print("=" * 75)
print("QDS STATISTICAL THREAT CLASSIFIER")
print("=" * 75)

for round_no in range(1, ROUNDS + 1):

    # Random quantum state
    state = random.choice(states)

    # Correct verification basis
    if state in ["0", "1"]:
        basis = "Z"
    else:
        basis = "X"

    # Actual scenario
    actual = random.choice(attacks)

    # Convert NOISE scenario into no explicit Pauli attack
    if actual == "NOISE":
        applied_attack = "NONE"
    else:
        applied_attack = actual

    # Measurement
    counts, noise_count = measure_state(
        state,
        applied_attack,
        basis,
        COPIES
    )

    expected = expected_result(state)

    # Error rate
    error_rate = calculate_error(
        counts,
        expected,
        COPIES
    )

    # Noise rate
    observed_noise_rate = noise_count / COPIES

    # Statistical z-score
    z_score = calculate_z_score(
        error_rate,
        NOISE_PROBABILITY,
        COPIES
    )

    # Classification
    detected = classify(
        error_rate,
        observed_noise_rate,
        z_score,
        basis
    )

    # Count classifications
    if detected == "NORMAL":
        normal_count += 1

    elif detected == "X / BIT-FLIP ATTACK":
        x_attack_count += 1

    elif detected == "Z / PHASE-FLIP ATTACK":
        z_attack_count += 1

    elif detected == "POSSIBLE CHANNEL NOISE":
        noise_count_total += 1

    elif detected == "ABNORMAL CHANNEL DISTURBANCE":
        disturbance_count += 1

    print(
        f"Round {round_no:02d} | "
        f"State={state} | "
        f"Basis={basis} | "
        f"Actual={actual:5} | "
        f"Error={error_rate:.2f} | "
        f"Noise={observed_noise_rate:.2f} | "
        f"Z-score={z_score:6.2f} | "
        f"Detected={detected}"
    )


# ==============================
# FINAL REPORT
# ==============================

print("\n" + "=" * 75)
print("FINAL STATISTICAL REPORT")
print("=" * 75)

print(f"Total Rounds              : {ROUNDS}")
print(f"Copies per Round          : {COPIES}")

print(f"\nNormal Conditions          : {normal_count}")
print(f"X / Bit-Flip Detection    : {x_attack_count}")
print(f"Z / Phase-Flip Detection  : {z_attack_count}")
print(f"Channel Noise             : {noise_count_total}")
print(f"Other Disturbances        : {disturbance_count}")

total_threats = (
    x_attack_count
    + z_attack_count
    + disturbance_count
)

print(f"\nTotal Threat/Disturbance Rounds : {total_threats}")

if total_threats > 0:
    print("\nFINAL DECISION: QUANTUM THREAT DETECTED")
else:
    print("\nFINAL DECISION: CHANNEL CONDITION NORMAL")