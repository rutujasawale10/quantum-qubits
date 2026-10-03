from qiskit import QuantumCircuit
from qiskit.primitives import StatevectorSampler
import random

# ==========================================
# PARAMETERS
# ==========================================

ROUNDS = 100
COPIES = 200
NOISE_PROBABILITY = 0.02

ATTACK_ERROR_THRESHOLD = 0.50

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

def apply_attack(qc, attack):

    if attack == "X":
        qc.x(0)

    elif attack == "Z":
        qc.z(0)


# ==========================================
# MEASURE
# ==========================================

def measure_state(state, attack, basis):

    counts = {"0": 0, "1": 0}

    for _ in range(COPIES):

        qc = create_state(state)

        # Attack
        apply_attack(qc, attack)

        # Channel noise
        if random.random() < NOISE_PROBABILITY:
            qc.x(0)

        # X-basis measurement
        if basis == "X":
            qc.h(0)

        qc.measure_all()

        sampler = StatevectorSampler()

        result = sampler.run(
            [qc],
            shots=1
        ).result()

        measured = list(
            result[0].data.meas.get_counts().keys()
        )[0]

        counts[measured] += 1

    return counts


# ==========================================
# EXPECTED RESULT
# ==========================================

def expected_result(state):

    if state in ["0", "+"]:
        return "0"

    return "1"


# ==========================================
# ERROR RATE
# ==========================================

def calculate_error(counts, expected):

    wrong = "1" if expected == "0" else "0"

    return counts[wrong] / COPIES


# ==========================================
# EXPERIMENT
# ==========================================

states = ["0", "1", "+", "-"]

TP = 0
TN = 0
FP = 0
FN = 0

x_attack_total = 0
x_attack_detected = 0

z_attack_total = 0
z_attack_detected = 0

print("=" * 80)
print("FINAL QDS THREAT DETECTION EVALUATION")
print("=" * 80)

for round_no in range(1, ROUNDS + 1):

    state = random.choice(states)

    # Correct basis
    if state in ["0", "1"]:
        basis = "Z"
    else:
        basis = "X"

    # 50% genuine / 50% attack
    if random.random() < 0.50:
        actual = "NONE"
    else:
        actual = random.choice(["X", "Z"])

    # Count attacks
    if actual == "X":
        x_attack_total += 1

    elif actual == "Z":
        z_attack_total += 1

    counts = measure_state(
        state,
        actual,
        basis
    )

    expected = expected_result(state)

    error_rate = calculate_error(
        counts,
        expected
    )

    # ======================================
    # DETECTION
    # ======================================

    if error_rate >= ATTACK_ERROR_THRESHOLD:

        detected_attack = True

        if actual == "X":
            x_attack_detected += 1

        elif actual == "Z":
            z_attack_detected += 1

    else:

        detected_attack = False

    # ======================================
    # CONFUSION MATRIX
    # ======================================

    actual_attack = actual != "NONE"

    if actual_attack and detected_attack:

        TP += 1

    elif actual_attack and not detected_attack:

        FN += 1

    elif not actual_attack and detected_attack:

        FP += 1

    elif not actual_attack and not detected_attack:

        TN += 1

    print(
        f"Round {round_no:03d} | "
        f"State={state} | "
        f"Basis={basis} | "
        f"Actual={actual:4} | "
        f"Error={error_rate:.2f} | "
        f"Detected={'THREAT' if detected_attack else 'NORMAL'}"
    )


# ==========================================
# METRICS
# ==========================================

attack_rounds = TP + FN
normal_rounds = TN + FP

if attack_rounds > 0:
    detection_rate = TP / attack_rounds * 100
else:
    detection_rate = 0

if attack_rounds > 0:
    false_acceptance_rate = FN / attack_rounds * 100
else:
    false_acceptance_rate = 0

if normal_rounds > 0:
    false_alarm_rate = FP / normal_rounds * 100
else:
    false_alarm_rate = 0

if normal_rounds > 0:
    false_rejection_rate = FP / normal_rounds * 100
else:
    false_rejection_rate = 0

if x_attack_total > 0:
    x_detection_rate = (
        x_attack_detected / x_attack_total * 100
    )
else:
    x_detection_rate = 0

if z_attack_total > 0:
    z_detection_rate = (
        z_attack_detected / z_attack_total * 100
    )
else:
    z_detection_rate = 0


# ==========================================
# FINAL REPORT
# ==========================================

print("\n" + "=" * 80)
print("FINAL PERFORMANCE REPORT")
print("=" * 80)

print(f"Total Rounds              : {ROUNDS}")
print(f"Copies per Round          : {COPIES}")

print("\nCONFUSION MATRIX")
print("-" * 40)

print(f"True Positives (TP)       : {TP}")
print(f"True Negatives (TN)       : {TN}")
print(f"False Positives (FP)      : {FP}")
print(f"False Negatives (FN)      : {FN}")

print("\nPERFORMANCE METRICS")
print("-" * 40)

print(f"Detection Rate            : {detection_rate:.2f}%")
print(f"False Acceptance Rate     : {false_acceptance_rate:.2f}%")
print(f"False Rejection Rate      : {false_rejection_rate:.2f}%")
print(f"False Alarm Rate          : {false_alarm_rate:.2f}%")

print("\nATTACK-WISE PERFORMANCE")
print("-" * 40)

print(f"X Attack Rounds           : {x_attack_total}")
print(f"X Attacks Detected        : {x_attack_detected}")
print(f"X Detection Rate          : {x_detection_rate:.2f}%")

print(f"\nZ Attack Rounds           : {z_attack_total}")
print(f"Z Attacks Detected        : {z_attack_detected}")
print(f"Z Detection Rate          : {z_detection_rate:.2f}%")

print("\n" + "=" * 80)

if detection_rate >= 50:
    print("FINAL DECISION: QDS THREAT DETECTION SUCCESSFUL")
else:
    print("FINAL DECISION: FURTHER PROTOCOL IMPROVEMENT REQUIRED")

print("=" * 80)