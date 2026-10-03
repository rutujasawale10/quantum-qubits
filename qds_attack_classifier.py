from qiskit import QuantumCircuit
from qiskit.primitives import StatevectorSampler
import random


# =========================================================
# QDS ATTACK CLASSIFIER
# =========================================================

ROUNDS = 30
COPIES = 100

NOISE_PROBABILITY = 0.05

STATES = ["0", "1", "+", "-"]
ATTACKS = ["NONE", "X", "Z", "NOISE"]


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
# CORRECT BASIS
# =========================================================

def get_basis(state_name):

    if state_name in ["0", "1"]:
        return "Z"

    return "X"


# =========================================================
# EXPECTED RESULT
# =========================================================

def get_expected(state_name):

    if state_name == "0":
        return "0"

    elif state_name == "1":
        return "1"

    elif state_name == "+":
        return "0"

    elif state_name == "-":
        return "1"


# =========================================================
# APPLY X ATTACK
# =========================================================

def apply_x_attack(qc):

    attacked = qc.copy()
    attacked.x(0)

    return attacked


# =========================================================
# APPLY Z ATTACK
# =========================================================

def apply_z_attack(qc):

    attacked = qc.copy()
    attacked.z(0)

    return attacked


# =========================================================
# APPLY NOISE
# =========================================================

def apply_noise(qc):

    noisy = qc.copy()

    noise_applied = False

    if random.random() < NOISE_PROBABILITY:

        noise_applied = True

        noise = random.choice(["X", "Z"])

        if noise == "X":
            noisy.x(0)

        elif noise == "Z":
            noisy.z(0)

    return noisy, noise_applied


# =========================================================
# MEASURE ONE COPY
# =========================================================

def measure_copy(state_name, attack, basis):

    qc = create_state(state_name)

    attack_applied = False

    # Apply selected attack
    if attack == "X":

        qc = apply_x_attack(qc)
        attack_applied = True

    elif attack == "Z":

        qc = apply_z_attack(qc)
        attack_applied = True


    # Apply channel noise
    qc, noise_applied = apply_noise(qc)


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

    measured = list(counts.keys())[0]

    return measured, attack_applied, noise_applied


# =========================================================
# COLLECT VERIFICATION DATA
# =========================================================

def collect_data(state_name, attack, basis):

    expected = get_expected(state_name)

    correct = 0
    errors = 0

    attack_count = 0
    noise_count = 0


    for _ in range(COPIES):

        measured, attack_applied, noise_applied = measure_copy(
            state_name,
            attack,
            basis
        )


        if measured == expected:
            correct += 1
        else:
            errors += 1


        if attack_applied:
            attack_count += 1


        if noise_applied:
            noise_count += 1


    error_rate = errors / COPIES

    attack_rate = attack_count / COPIES

    noise_rate = noise_count / COPIES


    return (
        error_rate,
        attack_rate,
        noise_rate
    )


# =========================================================
# ATTACK CLASSIFICATION
# =========================================================

def classify_attack(
    state,
    basis,
    error_rate,
    attack_rate,
    noise_rate
):

    # Very small disturbance
    if error_rate < 0.10:

        return "NORMAL", 90.0


    # Strong disturbance
    if error_rate >= 0.50:

        # X-sensitive states
        if basis == "Z":

            return "X / BIT-FLIP ATTACK", min(
                99.0,
                70.0 + error_rate * 30
            )

        # Z-sensitive states
        if basis == "X":

            return "Z / PHASE-FLIP ATTACK", min(
                99.0,
                70.0 + error_rate * 30
            )


    # Moderate disturbance
    if noise_rate > 0.08:

        return "CHANNEL NOISE", 70.0


    if error_rate >= 0.10:

        return "POSSIBLE CHANNEL DISTURBANCE", 60.0


    return "NORMAL", 85.0


# =========================================================
# MAIN
# =========================================================

print("=" * 90)
print("QUANTUM DIGITAL SIGNATURE ATTACK CLASSIFIER")
print("=" * 90)

print("Rounds              :", ROUNDS)
print("Copies per Round    :", COPIES)
print("Noise Probability   :", NOISE_PROBABILITY)

print("=" * 90)


normal_count = 0
x_count = 0
z_count = 0
noise_count = 0
disturbance_count = 0


# =========================================================
# MULTI-ROUND EXPERIMENT
# =========================================================

for round_no in range(1, ROUNDS + 1):

    state = random.choice(STATES)

    basis = get_basis(state)


    # Random attack scenario
    attack = random.choice(ATTACKS)


    (
        error_rate,
        attack_rate,
        noise_rate
    ) = collect_data(
        state,
        attack,
        basis
    )


    (
        classification,
        confidence
    ) = classify_attack(
        state,
        basis,
        error_rate,
        attack_rate,
        noise_rate
    )


    # Count classifications
    if classification == "NORMAL":

        normal_count += 1

    elif classification == "X / BIT-FLIP ATTACK":

        x_count += 1

    elif classification == "Z / PHASE-FLIP ATTACK":

        z_count += 1

    elif classification == "CHANNEL NOISE":

        noise_count += 1

    else:

        disturbance_count += 1


    print(
        f"Round {round_no:02d} | "
        f"State={state:>2} | "
        f"Basis={basis} | "
        f"Actual={attack:>5} | "
        f"Error={error_rate:.2f} | "
        f"Noise={noise_rate:.2f} | "
        f"Detected={classification:<25} | "
        f"Confidence={confidence:.1f}%"
    )


# =========================================================
# FINAL REPORT
# =========================================================

print("\n")

print("=" * 90)
print("ATTACK CLASSIFICATION REPORT")
print("=" * 90)


print("\n--- CLASSIFICATION SUMMARY ---")

print(
    "Normal Conditions       :",
    normal_count
)

print(
    "X / Bit-Flip Detection  :",
    x_count
)

print(
    "Z / Phase-Flip Detection:",
    z_count
)

print(
    "Channel Noise Detection :",
    noise_count
)

print(
    "Other Disturbances      :",
    disturbance_count
)


print("\n--- DETECTION PIPELINE ---")

print("Quantum State")
print("      ↓")
print("Verification Basis")
print("      ↓")
print("Multiple Measurements")
print("      ↓")
print("Error / Disturbance Rate")
print("      ↓")
print("Attack Classification")
print("      ↓")
print("Threat Confidence")
print("      ↓")
print("NORMAL / X / Z / NOISE")


print("\n" + "=" * 90)

print(
    "FINAL DECISION: "
    "QUANTUM ATTACK CLASSIFICATION COMPLETED"
)

print("=" * 90)