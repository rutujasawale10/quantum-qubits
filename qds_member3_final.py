from qiskit import QuantumCircuit
from qiskit.primitives import StatevectorSampler
import random
import math

# ============================================================
# MEMBER 3 - FINAL QDS THREAT DETECTION ENGINE
# ============================================================

ROUNDS = 100
COPIES = 200

# Number of independent verification qubits checked per round.
# A single qubit whose basis happens to match the attacker's Pauli
# operation is PHYSICALLY undetectable (0% info leaked - this is a
# real quantum-mechanical limit, not a bug). Checking K independent,
# randomly-basis qubits per round and flagging the round as an
# attack if ANY ONE of them shows disturbance raises the guaranteed
# per-round detection probability to 1 - 0.5^K, while keeping false
# alarms low (each qubit's own false-alarm chance is tiny).
K_SUBTESTS = 3

# Expected normal channel noise
BASELINE_NOISE = 0.02

# Error above this level is treated as a strong disturbance
ATTACK_THRESHOLD = 0.20

# Statistical significance threshold
Z_THRESHOLD = 3.0


# ============================================================
# 1. QUANTUM STATE CREATION
# ============================================================

def create_state(state):

    qc = QuantumCircuit(1)

    if state == "0":
        pass

    elif state == "1":
        qc.x(0)

    elif state == "+":
        qc.h(0)

    elif state == "-":
        qc.x(0)
        qc.h(0)

    return qc


# ============================================================
# 2. APPLY PAULI ATTACK
# ============================================================

def apply_attack(qc, attack):

    if attack == "X":
        qc.x(0)

    elif attack == "Z":
        qc.z(0)


# ============================================================
# 3. EXPECTED MEASUREMENT RESULT
# ============================================================

def expected_result(state):

    if state in ["0", "+"]:
        return "0"

    return "1"


# ============================================================
# 4. MEASURE MULTIPLE COPIES
# ============================================================

def measure_copies(state, attack, basis):

    counts = {
        "0": 0,
        "1": 0
    }

    noise_events = 0

    sampler = StatevectorSampler()

    for _ in range(COPIES):

        qc = create_state(state)

        # --------------------------------------------
        # Apply attacker operation
        # --------------------------------------------

        apply_attack(qc, attack)

        # --------------------------------------------
        # Simulate channel noise
        # --------------------------------------------

        if random.random() < BASELINE_NOISE:

            qc.x(0)
            noise_events += 1

        # --------------------------------------------
        # Select measurement basis
        # --------------------------------------------

        if basis == "X":
            qc.h(0)

        qc.measure_all()

        result = sampler.run(
            [qc],
            shots=1
        ).result()

        measured = list(
            result[0].data.meas.get_counts().keys()
        )[0]

        counts[measured] += 1

    return counts, noise_events


# ============================================================
# 5. CALCULATE ERROR RATE
# ============================================================

def calculate_error_rate(counts, expected):

    wrong_result = "1" if expected == "0" else "0"

    wrong_count = counts.get(wrong_result, 0)

    return wrong_count / COPIES


# ============================================================
# 6. CALCULATE Z-SCORE
# ============================================================

def calculate_z_score(error_rate):

    variance = (
        BASELINE_NOISE
        * (1 - BASELINE_NOISE)
        / COPIES
    )

    if variance <= 0:
        return 0

    standard_deviation = math.sqrt(variance)

    return (
        (error_rate - BASELINE_NOISE)
        / standard_deviation
    )


# ============================================================
# 7. CLASSIFY THREAT
# ============================================================

def classify_threat(error_rate, z_score, basis):

    # Strong disturbance
    if error_rate >= ATTACK_THRESHOLD:

        if basis == "Z":
            return "X / BIT-FLIP ATTACK"

        elif basis == "X":
            return "Z / PHASE-FLIP ATTACK"

    # Statistically unusual disturbance
    if z_score >= Z_THRESHOLD:

        return "STATISTICAL CHANNEL DISTURBANCE"

    # Small disturbance within expected range
    if error_rate < 0.10:

        return "NORMAL"

    return "POSSIBLE CHANNEL NOISE"


# ============================================================
# 8. INITIALIZE PERFORMANCE COUNTERS
# ============================================================

TP = 0
TN = 0
FP = 0
FN = 0

x_total = 0
x_detected = 0

z_total = 0
z_detected = 0

noise_detected = 0
disturbance_detected = 0


# ============================================================
# 9. START EXPERIMENT
# ============================================================

states = [
    "0",
    "1",
    "+",
    "-"
]

print("=" * 90)
print("MEMBER 3 - FINAL QDS THREAT DETECTION ENGINE")
print("=" * 90)

print(f"Total Rounds       : {ROUNDS}")
print(f"Copies per Round   : {COPIES}")
print(f"Verify Qubits/Round: {K_SUBTESTS}")
print(f"Baseline Noise     : {BASELINE_NOISE * 100:.1f}%")
print()

ATTACK_LABELS = [
    "X / BIT-FLIP ATTACK",
    "Z / PHASE-FLIP ATTACK",
    "STATISTICAL CHANNEL DISTURBANCE"
]


# ============================================================
# 10. MULTI-ROUND EXPERIMENT (K independent qubits per round)
# ============================================================

for round_number in range(1, ROUNDS + 1):

    # Random genuine / attack condition for this round
    scenario = random.choice([
        "NONE",
        "NONE",
        "X",
        "Z",
        "NOISE"
    ])

    # NOISE means no deliberate attacker operation
    if scenario == "NOISE":
        attack = "NONE"
    else:
        attack = scenario

    # Count actual attacks
    if scenario == "X":
        x_total += 1

    elif scenario == "Z":
        z_total += 1

    actual_attack = scenario in ["X", "Z"]

    round_detected = False
    round_labels = []
    sub_results = []

    # --------------------------------------------------------
    # Check K independent, randomly-basis verification qubits.
    # Round is flagged as an attack if ANY ONE of them shows
    # disturbance - a same-basis Pauli attack is invisible on a
    # single qubit, but statistically very unlikely to stay
    # invisible on all K independently random-basis qubits.
    # --------------------------------------------------------

    for sub in range(K_SUBTESTS):

        state = random.choice(states)

        if state in ["0", "1"]:
            basis = "Z"
        else:
            basis = "X"

        counts, noise_events = measure_copies(
            state,
            attack,
            basis
        )

        expected = expected_result(state)

        error_rate = calculate_error_rate(
            counts,
            expected
        )

        noise_rate = noise_events / COPIES

        z_score = calculate_z_score(
            error_rate
        )

        detected = classify_threat(
            error_rate,
            z_score,
            basis
        )

        sub_results.append(
            (state, basis, error_rate, noise_rate, z_score, detected)
        )

        round_labels.append(detected)

        if detected in ATTACK_LABELS:
            round_detected = True

    # ========================================================
    # CONFUSION MATRIX (decision is per ROUND, via OR across K)
    # ========================================================

    if actual_attack and round_detected:

        TP += 1

    elif actual_attack and not round_detected:

        FN += 1

    elif not actual_attack and round_detected:

        FP += 1

    else:

        TN += 1

    # ========================================================
    # ATTACK-WISE RESULTS
    # ========================================================

    if scenario == "X" and "X / BIT-FLIP ATTACK" in round_labels:

        x_detected += 1

    if scenario == "Z" and "Z / PHASE-FLIP ATTACK" in round_labels:

        z_detected += 1

    if "POSSIBLE CHANNEL NOISE" in round_labels:

        noise_detected += 1

    if "STATISTICAL CHANNEL DISTURBANCE" in round_labels:

        disturbance_detected += 1

    # ========================================================
    # ROUND OUTPUT
    # ========================================================

    sub_summary = " || ".join(
        f"[{s} Basis={b} Err={e:.2f} Z={z:6.2f} => {d}]"
        for s, b, e, n, z, d in sub_results
    )

    final_verdict = "ATTACK DETECTED" if round_detected else "NORMAL"

    print(
        f"Round {round_number:03d} | Actual={scenario:5} | "
        f"{sub_summary} | RoundVerdict={final_verdict}"
    )


# ============================================================
# 11. PERFORMANCE METRICS
# ============================================================

attack_rounds = TP + FN
normal_rounds = TN + FP

# Detection Rate
if attack_rounds > 0:

    detection_rate = (
        TP / attack_rounds
    ) * 100

else:

    detection_rate = 0


# False Acceptance Rate
# Attack accepted as genuine
if attack_rounds > 0:

    false_acceptance_rate = (
        FN / attack_rounds
    ) * 100

else:

    false_acceptance_rate = 0


# False Rejection Rate
# Genuine condition rejected
if normal_rounds > 0:

    false_rejection_rate = (
        FP / normal_rounds
    ) * 100

else:

    false_rejection_rate = 0


# False Alarm Rate
if normal_rounds > 0:

    false_alarm_rate = (
        FP / normal_rounds
    ) * 100

else:

    false_alarm_rate = 0


# X Attack Detection Rate
if x_total > 0:

    x_detection_rate = (
        x_detected / x_total
    ) * 100

else:

    x_detection_rate = 0


# Z Attack Detection Rate
if z_total > 0:

    z_detection_rate = (
        z_detected / z_total
    ) * 100

else:

    z_detection_rate = 0


# ============================================================
# 12. FINAL REPORT
# ============================================================

print("\n")
print("=" * 90)
print("FINAL PERFORMANCE REPORT")
print("=" * 90)

print(f"Total Rounds              : {ROUNDS}")
print(f"Copies per Round          : {COPIES}")

print("\nCONFUSION MATRIX")
print("-" * 50)

print(f"True Positives (TP)       : {TP}")
print(f"True Negatives (TN)       : {TN}")
print(f"False Positives (FP)      : {FP}")
print(f"False Negatives (FN)      : {FN}")

print("\nOVERALL PERFORMANCE")
print("-" * 50)

print(
    f"Detection Rate            : "
    f"{detection_rate:.2f}%"
)

print(
    f"False Acceptance Rate     : "
    f"{false_acceptance_rate:.2f}%"
)

print(
    f"False Rejection Rate      : "
    f"{false_rejection_rate:.2f}%"
)

print(
    f"False Alarm Rate          : "
    f"{false_alarm_rate:.2f}%"
)

print("\nX ATTACK PERFORMANCE")
print("-" * 50)

print(f"X Attack Rounds           : {x_total}")
print(f"X Attacks Detected        : {x_detected}")
print(
    f"X Detection Rate          : "
    f"{x_detection_rate:.2f}%"
)

print("\nZ ATTACK PERFORMANCE")
print("-" * 50)

print(f"Z Attack Rounds           : {z_total}")
print(f"Z Attacks Detected        : {z_detected}")
print(
    f"Z Detection Rate          : "
    f"{z_detection_rate:.2f}%"
)

print("\nCHANNEL ANALYSIS")
print("-" * 50)

print(
    f"Possible Noise Detection : "
    f"{noise_detected}"
)

print(
    f"Statistical Disturbance  : "
    f"{disturbance_detected}"
)

print("\nMULTI-QUBIT VERIFICATION (K_SUBTESTS) ANALYSIS")
print("-" * 50)

# ------------------------------------------------------------
# WHY THIS SECTION EXISTS:
# A single Pauli attack (X or Z) that happens to align with the
# verification basis produces ZERO measurable disturbance on
# THAT ONE qubit - a real quantum-mechanical limit (same as
# BB84), not a threshold problem. Checking K independent,
# randomly-basis qubits per round and flagging the round if ANY
# ONE shows disturbance raises the guaranteed detection floor to
# 1 - 0.5^K, since all K qubits landing on a matched (invisible)
# basis by chance becomes exponentially unlikely.
# ------------------------------------------------------------

theoretical_floor = (1 - 0.5 ** K_SUBTESTS) * 100

print(f"Verification qubits per round (K) : {K_SUBTESTS}")
print(f"Theoretical detection floor        : {theoretical_floor:.2f}%")
print(f"Measured Detection Rate            : {detection_rate:.2f}%")

print("\nSESSION-LEVEL CUMULATIVE SECURITY BOUND")
print("-" * 50)

p_per_round = detection_rate / 100

for n in [1, 5, 10, 20, 50, ROUNDS]:

    cumulative = 1 - (1 - p_per_round) ** n

    print(
        f"Rounds={n:4d}  ->  "
        f"P(persistent attacker caught at least once) = "
        f"{cumulative * 100:.4f}%"
    )

print(
    "\nNote: increasing K_SUBTESTS trades a small rise in false "
    "alarms for a large rise in guaranteed detection floor "
    "(K=3 -> ~87.5%, K=4 -> ~93.75%, K=5 -> ~96.9%)."
)

print("\nFINAL DECISION")
print("-" * 50)

if detection_rate >= 80 and false_alarm_rate <= 5:

    print("QUANTUM THREAT DETECTION COMPLETED - TARGET ACCURACY MET")

elif detection_rate >= 50:

    print("PARTIAL DETECTION - CONSIDER INCREASING K_SUBTESTS")

else:

    print("FURTHER PROTOCOL IMPROVEMENT REQUIRED")

print("=" * 90)