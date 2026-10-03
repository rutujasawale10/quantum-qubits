from qiskit import QuantumCircuit
from qiskit.primitives import StatevectorSampler
import random
import math

# ============================================================
# MEMBER 3 - QDS THREAT DETECTION ON TELEPORTATION CIRCUIT
# Clean Teleportation + X/Z Attack Detection
# ============================================================

# Reproducible experiment
random.seed(42)

ROUNDS = 100
COPIES = 200

# Independent verification tests per round
K_SUBTESTS = 3

# Normal channel noise probability
BASELINE_NOISE = 0.02

# Error rate above this value is considered a strong attack signal
ATTACK_THRESHOLD = 0.20

# Statistical threshold
Z_THRESHOLD = 3.0

states = ["0", "1", "+", "-"]


# ============================================================
# 1. BUILD TELEPORTATION CIRCUIT
# ============================================================

def build_teleport_circuit(state, attack):

    # 3 qubits:
    # q0 = message qubit
    # q1 = Alice's entangled qubit
    # q2 = Bob's qubit / quantum channel

    qc = QuantumCircuit(3, 1)

    # --------------------------------------------------------
    # Prepare message state on q0
    # --------------------------------------------------------

    if state == "0":
        pass

    elif state == "1":
        qc.x(0)

    elif state == "+":
        qc.h(0)

    elif state == "-":
        qc.x(0)
        qc.h(0)

    # --------------------------------------------------------
    # Create Bell pair q1-q2
    # --------------------------------------------------------

    qc.h(1)
    qc.cx(1, 2)

    # --------------------------------------------------------
    # ATTACK INJECTION
    #
    # q2 represents the travelling quantum channel.
    # X = bit-flip attack
    # Z = phase-flip attack
    # --------------------------------------------------------

    if attack == "X":
        qc.x(2)

    elif attack == "Z":
        qc.z(2)

    # --------------------------------------------------------
    # Ordinary channel noise
    # --------------------------------------------------------

    if random.random() < BASELINE_NOISE:
        qc.x(2)

    # --------------------------------------------------------
    # Alice's teleportation operations
    # --------------------------------------------------------

    qc.cx(0, 1)
    qc.h(0)

    # --------------------------------------------------------
    # Bob's coherent corrections
    # --------------------------------------------------------

    qc.cx(1, 2)
    qc.cz(0, 2)

    return qc


# ============================================================
# 2. EXPECTED MEASUREMENT RESULT
# ============================================================

def expected_result(state):

    # Z basis:
    # |0> -> 0
    # |1> -> 1

    # X basis:
    # |+> -> 0
    # |-> -> 1

    if state in ["0", "+"]:
        return "0"

    return "1"


# ============================================================
# 3. SELECT VERIFICATION BASIS
# ============================================================

def verification_basis(state):

    # Computational/Z basis for |0>, |1>
    if state in ["0", "1"]:
        return "Z"

    # X basis for |+>, |->
    return "X"


# ============================================================
# 4. MEASURE TELEPORTED QUBIT
# ============================================================

def measure_teleported_qubit(state, attack, basis):

    counts = {
        "0": 0,
        "1": 0
    }

    sampler = StatevectorSampler()

    for _ in range(COPIES):

        # Build fresh teleportation circuit
        qc = build_teleport_circuit(
            state,
            attack
        )

        # ----------------------------------------------------
        # X-basis measurement
        #
        # H converts X-basis measurement into
        # computational-basis measurement.
        # ----------------------------------------------------

        if basis == "X":
            qc.h(2)

        # Measure Bob's teleported qubit
        qc.measure(2, 0)

        # Run one shot
        result = sampler.run(
            [qc],
            shots=1
        ).result()

        measured = list(
            result[0].data.c.get_counts().keys()
        )[0]

        counts[measured] += 1

    return counts


# ============================================================
# 5. CALCULATE ERROR RATE
# ============================================================

def calculate_error_rate(counts, expected):

    if expected == "0":
        wrong_result = "1"
    else:
        wrong_result = "0"

    errors = counts.get(
        wrong_result,
        0
    )

    return errors / COPIES


# ============================================================
# 6. CALCULATE STATISTICAL Z-SCORE
# ============================================================

def calculate_z_score(error_rate):

    variance = (
        BASELINE_NOISE *
        (1 - BASELINE_NOISE)
        / COPIES
    )

    standard_deviation = math.sqrt(
        variance
    )

    if standard_deviation == 0:
        return 0

    z_score = (
        error_rate - BASELINE_NOISE
    ) / standard_deviation

    return z_score


# ============================================================
# 7. THREAT CLASSIFICATION
# ============================================================

def classify_threat(error_rate, z_score):

    # Strong disturbance
    if error_rate >= ATTACK_THRESHOLD:
        return "ATTACK DETECTED"

    # Statistically significant disturbance
    if z_score >= Z_THRESHOLD:
        return "STATISTICAL DISTURBANCE"

    # Small error compatible with normal noise
    if error_rate < 0.10:
        return "NORMAL"

    # Intermediate disturbance
    return "POSSIBLE NOISE"


# ============================================================
# 8. RUN ONE VERIFICATION TEST
# ============================================================

def run_verification(state, attack):

    # Select correct basis
    basis = verification_basis(
        state
    )

    # Measure teleported qubit
    counts = measure_teleported_qubit(
        state,
        attack,
        basis
    )

    # Expected result
    expected = expected_result(
        state
    )

    # Calculate error
    error_rate = calculate_error_rate(
        counts,
        expected
    )

    # Calculate z-score
    z_score = calculate_z_score(
        error_rate
    )

    # Classify
    classification = classify_threat(
        error_rate,
        z_score
    )

    return {
        "state": state,
        "basis": basis,
        "counts": counts,
        "expected": expected,
        "error_rate": error_rate,
        "z_score": z_score,
        "classification": classification
    }


# ============================================================
# 9. INITIALIZE PERFORMANCE COUNTERS
# ============================================================

TP = 0
TN = 0
FP = 0
FN = 0

x_total = 0
x_detected = 0

z_total = 0
z_detected = 0

noise_total = 0
noise_detected = 0


# ============================================================
# 10. START EXPERIMENT
# ============================================================

print("=" * 90)
print(
    "MEMBER 3 - TELEPORTATION-INTEGRATED "
    "QDS THREAT DETECTION"
)
print("=" * 90)

print(
    f"Total Rounds        : {ROUNDS}"
)

print(
    f"Copies per subtest  : {COPIES}"
)

print(
    f"Verify tests/round  : {K_SUBTESTS}"
)

print(
    f"Baseline Noise      : "
    f"{BASELINE_NOISE * 100:.1f}%"
)

print()


# ============================================================
# 11. RUN 100 ROUNDS
# ============================================================

for round_number in range(
    1,
    ROUNDS + 1
):

    # --------------------------------------------------------
    # Scenario selection
    #
    # NONE  = genuine communication
    # X     = bit-flip attack
    # Z     = phase-flip attack
    # NOISE = ordinary channel-noise condition
    # --------------------------------------------------------

    scenario = random.choice(
        [
            "NONE",
            "NONE",
            "X",
            "Z",
            "NOISE"
        ]
    )

    # NOISE is not considered a malicious attack
    if scenario in ["X", "Z"]:
        attack = scenario
    else:
        attack = "NONE"

    # --------------------------------------------------------
    # Count attack types
    # --------------------------------------------------------

    if scenario == "X":
        x_total += 1

    elif scenario == "Z":
        z_total += 1

    elif scenario == "NOISE":
        noise_total += 1

    # --------------------------------------------------------
    # Ground truth
    # --------------------------------------------------------

    actual_attack = scenario in [
        "X",
        "Z"
    ]

    round_detected = False

    round_results = []


    # ========================================================
    # MULTIPLE INDEPENDENT VERIFICATION TESTS
    # ========================================================

    for sub in range(
        K_SUBTESTS
    ):

        # Random quantum signature state
        state = random.choice(
            states
        )

        # Run verification
        result = run_verification(
            state,
            attack
        )

        round_results.append(
            result
        )

        # ----------------------------------------------------
        # If any independent verification detects disturbance,
        # classify the round as detected.
        # ----------------------------------------------------

        if result["classification"] in [
            "ATTACK DETECTED",
            "STATISTICAL DISTURBANCE"
        ]:

            round_detected = True


    # ========================================================
    # CONFUSION MATRIX
    # ========================================================

    if actual_attack:

        if round_detected:
            TP += 1
        else:
            FN += 1

    else:

        if round_detected:
            FP += 1
        else:
            TN += 1


    # ========================================================
    # X ATTACK PERFORMANCE
    # ========================================================

    if scenario == "X":

        if round_detected:
            x_detected += 1


    # ========================================================
    # Z ATTACK PERFORMANCE
    # ========================================================

    elif scenario == "Z":

        if round_detected:
            z_detected += 1


    # ========================================================
    # NOISE PERFORMANCE
    # ========================================================

    elif scenario == "NOISE":

        if round_detected:
            noise_detected += 1


    # ========================================================
    # ROUND VERDICT
    # ========================================================

    if round_detected:
        verdict = "ATTACK DETECTED"
    else:
        verdict = "NORMAL"

    print(
        f"Round {round_number:03d} | "
        f"Actual={scenario:5} | "
        f"RoundVerdict={verdict}"
    )


# ============================================================
# 12. CALCULATE FINAL METRICS
# ============================================================

attack_rounds = TP + FN

normal_rounds = TN + FP


# ------------------------------------------------------------
# True Positive Rate / Detection Rate
# ------------------------------------------------------------

TPR = (
    TP / attack_rounds * 100
    if attack_rounds > 0
    else 0
)


# ------------------------------------------------------------
# False Negative Rate / Miss Rate
# ------------------------------------------------------------

FNR = (
    FN / attack_rounds * 100
    if attack_rounds > 0
    else 0
)


# ------------------------------------------------------------
# False Positive Rate / False Alarm Rate
# ------------------------------------------------------------

FPR = (
    FP / normal_rounds * 100
    if normal_rounds > 0
    else 0
)


# ------------------------------------------------------------
# True Negative Rate / Specificity
# ------------------------------------------------------------

TNR = (
    TN / normal_rounds * 100
    if normal_rounds > 0
    else 0
)


# ------------------------------------------------------------
# X Attack Detection Rate
# ------------------------------------------------------------

X_RATE = (
    x_detected / x_total * 100
    if x_total > 0
    else 0
)


# ------------------------------------------------------------
# Z Attack Detection Rate
# ------------------------------------------------------------

Z_RATE = (
    z_detected / z_total * 100
    if z_total > 0
    else 0
)


# ============================================================
# 13. FINAL PERFORMANCE REPORT
# ============================================================

print("\n" + "=" * 90)

print(
    "FINAL PERFORMANCE REPORT"
)

print("=" * 90)

print(
    f"TP  (True Positive)       : {TP}"
)

print(
    f"TN  (True Negative)       : {TN}"
)

print(
    f"FP  (False Positive)      : {FP}"
)

print(
    f"FN  (False Negative)      : {FN}"
)

print()

print(
    f"Detection Rate / TPR      : "
    f"{TPR:.2f}%"
)

print(
    f"False Negative Rate / FNR : "
    f"{FNR:.2f}%"
)

print(
    f"False Alarm Rate / FPR    : "
    f"{FPR:.2f}%"
)

print(
    f"Specificity / TNR         : "
    f"{TNR:.2f}%"
)

print()

print(
    f"X Attack Detection Rate  : "
    f"{X_RATE:.2f}% "
    f"({x_detected}/{x_total})"
)

print(
    f"Z Attack Detection Rate  : "
    f"{Z_RATE:.2f}% "
    f"({z_detected}/{z_total})"
)

print()

print(
    f"Noise Rounds             : "
    f"{noise_total}"
)

print(
    f"Noise Detected as Threat : "
    f"{noise_detected}"
)

print("=" * 90)

print(
    "NOTE: Results are simulation results "
    "under the defined experimental parameters."
)

print(
    "They do not represent a production security guarantee."
)

print("=" * 90)