from qiskit import QuantumCircuit
from qiskit.primitives import StatevectorSampler
import random
import math

# ==============================
# CONFIGURATION
# ==============================

ROUNDS = 100
COPIES = 20
THRESHOLD = 0.20       # 20% error threshold
ATTACK_PROBABILITY = 0.50

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
# CHOOSE CORRECT BASIS
# ==============================

def get_basis(state_name):

    if state_name in ["0", "1"]:
        return "Z"

    return "X"


# ==============================
# APPLY ATTACK
# ==============================

def apply_attack(state_name, attack):

    qc = create_state(state_name)

    if attack == "X":
        qc.x(0)

    elif attack == "Z":
        qc.z(0)

    return qc


# ==============================
# MEASURE STATE
# ==============================

def measure_state(state_name, attack, basis, shots):

    qc = apply_attack(state_name, attack)

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


# ==============================
# EXPECTED RESULT
# ==============================

def expected_result(state_name):

    if state_name == "0":
        return "0"

    if state_name == "1":
        return "1"

    if state_name == "+":
        return "0"

    if state_name == "-":
        return "1"


# ==============================
# ERROR RATE
# ==============================

def calculate_error_rate(counts, expected, shots):

    wrong = 0

    for result, count in counts.items():

        if result != expected:
            wrong += count

    return wrong / shots


# ==============================
# MAIN QDS DETECTION
# ==============================

tp = 0
tn = 0
fp = 0
fn = 0

total_error = 0

x_attacks = 0
z_attacks = 0

x_detected = 0
z_detected = 0

print("=" * 70)
print("FINAL MULTI-COPY QDS STATISTICAL DETECTION ENGINE")
print("=" * 70)

print("Rounds       :", ROUNDS)
print("Copies/Round :", COPIES)
print("Threshold    :", THRESHOLD)
print("States       :", STATES)
print("Attacks      :", ATTACKS)

print("=" * 70)


# ==============================
# RUN ROUNDS
# ==============================

for round_no in range(1, ROUNDS + 1):

    # Random quantum signature state
    state = random.choice(STATES)

    # Correct verification basis
    basis = get_basis(state)

    # Random attack
    if random.random() < ATTACK_PROBABILITY:

        attack = random.choice(["X", "Z"])

    else:

        attack = "NONE"

    # Count attack types
    if attack == "X":
        x_attacks += 1

    elif attack == "Z":
        z_attacks += 1


    # Expected correct result
    expected = expected_result(state)


    # Measure multiple copies
    counts = measure_state(
        state,
        attack,
        basis,
        COPIES
    )


    # Calculate error
    error_rate = calculate_error_rate(
        counts,
        expected,
        COPIES
    )

    total_error += error_rate


    # Threat decision
    threat = error_rate > THRESHOLD


    # ==============================
    # CONFUSION MATRIX
    # ==============================

    if attack != "NONE":

        if threat:

            tp += 1

            if attack == "X":
                x_detected += 1

            elif attack == "Z":
                z_detected += 1

        else:

            fn += 1

    else:

        if threat:

            fp += 1

        else:

            tn += 1


    # ==============================
    # PRINT FIRST 20 ROUNDS
    # ==============================

    if round_no <= 20:

        print(
            f"Round {round_no:03d} | "
            f"State={state:>2} | "
            f"Basis={basis} | "
            f"Attack={attack:>4} | "
            f"Error={error_rate:.2f} | "
            f"{'THREAT' if threat else 'NORMAL'}"
        )


# ==============================
# METRICS
# ==============================

attack_rounds = tp + fn
genuine_rounds = tn + fp

if attack_rounds > 0:
    detection_rate = (tp / attack_rounds) * 100
    false_acceptance_rate = (fn / attack_rounds) * 100
else:
    detection_rate = 0
    false_acceptance_rate = 0


if genuine_rounds > 0:
    false_rejection_rate = (fp / genuine_rounds) * 100
    false_alarm_rate = (fp / genuine_rounds) * 100
else:
    false_rejection_rate = 0
    false_alarm_rate = 0


average_error = total_error / ROUNDS


if x_attacks > 0:
    x_detection_rate = (x_detected / x_attacks) * 100
else:
    x_detection_rate = 0


if z_attacks > 0:
    z_detection_rate = (z_detected / z_attacks) * 100
else:
    z_detection_rate = 0


# ==============================
# FINAL REPORT
# ==============================

print("\n")
print("=" * 70)
print("FINAL STATISTICAL REPORT")
print("=" * 70)

print(f"Total Rounds             : {ROUNDS}")
print(f"Copies per Round        : {COPIES}")
print(f"Average Error Rate      : {average_error:.2%}")

print("\n--- CONFUSION MATRIX ---")

print(f"TP (Threat Detected)    : {tp}")
print(f"FN (Attack Missed)      : {fn}")
print(f"TN (Genuine Accepted)   : {tn}")
print(f"FP (False Alarm)        : {fp}")

print("\n--- PERFORMANCE ---")

print(
    f"Detection Rate          : "
    f"{detection_rate:.2f}%"
)

print(
    f"False Acceptance Rate   : "
    f"{false_acceptance_rate:.2f}%"
)

print(
    f"False Rejection Rate    : "
    f"{false_rejection_rate:.2f}%"
)

print(
    f"False Alarm Rate        : "
    f"{false_alarm_rate:.2f}%"
)

print("\n--- ATTACK-WISE DETECTION ---")

print(f"X Attack Rounds         : {x_attacks}")
print(f"X Attack Detection     : {x_detection_rate:.2f}%")

print(f"Z Attack Rounds         : {z_attacks}")
print(f"Z Attack Detection     : {z_detection_rate:.2f}%")

print("\n" + "=" * 70)

if detection_rate >= 70:

    print("FINAL DECISION: 🚨 QUANTUM THREAT DETECTED")

else:

    print("FINAL DECISION: ⚠️ MORE VERIFICATION REQUIRED")

print("=" * 70)