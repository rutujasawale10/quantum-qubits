from qiskit import QuantumCircuit
from qiskit.primitives import StatevectorSampler
import random


# ============================================================
# MULTI-ROUND QUANTUM DIGITAL SIGNATURE DETECTION
# ============================================================

ROUNDS = 100
SHOTS = 100
THRESHOLD = 10

STATES = ["0", "1", "+", "-"]
ATTACKS = ["NONE", "X", "Z"]
BASES = ["Z", "X"]


# ============================================================
# CREATE QUANTUM STATE
# ============================================================

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


# ============================================================
# APPLY ATTACK
# ============================================================

def apply_attack(qc, attack):

    if attack == "X":
        qc.x(0)

    elif attack == "Z":
        qc.z(0)

    return qc


# ============================================================
# MEASURE QUANTUM STATE
# ============================================================

def measure_state(state, attack, basis):

    qc = create_state(state)

    # Apply attack
    apply_attack(qc, attack)

    # X-basis measurement
    if basis == "X":
        qc.h(0)

    qc.measure_all()

    sampler = StatevectorSampler()

    result = sampler.run(
        [qc],
        shots=SHOTS
    ).result()

    return result[0].data.meas.get_counts()


# ============================================================
# CHI-SQUARE
# ============================================================

def calculate_chi_square(expected, observed):

    chi = 0.0

    for bit in ["0", "1"]:

        e = expected.get(bit, 0)
        o = observed.get(bit, 0)

        if e > 0:

            chi += ((o - e) ** 2) / e

        elif o > 0:

            chi += o

    return chi


# ============================================================
# START ENGINE
# ============================================================

print("=" * 70)
print("       MULTI-ROUND QUANTUM DIGITAL SIGNATURE")
print("              THREAT DETECTION ENGINE")
print("=" * 70)

print("\nTotal Rounds:", ROUNDS)
print("Shots per Round:", SHOTS)
print("Detection Threshold:", THRESHOLD)

print("\nStates:", STATES)
print("Attacks:", ATTACKS)
print("Bases:", BASES)


# ============================================================
# RANDOM ATTACK MODE
# ============================================================

print("\n")
print("=" * 70)
print("                 RANDOMIZED TESTING")
print("=" * 70)


# Change this value:
# NONE = no attack
# X    = bit flip attack
# Z    = phase flip attack

ATTACK_MODE = "Z"


print("\nAttack Mode:", ATTACK_MODE)


# ============================================================
# COUNTERS
# ============================================================

threat_rounds = 0
normal_rounds = 0
invisible_rounds = 0

total_chi_square = 0.0

x_detected = 0
z_detected = 0


# ============================================================
# RUN MULTIPLE ROUNDS
# ============================================================

for round_number in range(1, ROUNDS + 1):

    # Random quantum state
    state = random.choice(STATES)

    # Random measurement basis
    basis = random.choice(BASES)

    # Original measurement
    original = measure_state(
        state,
        "NONE",
        basis
    )

    # Received measurement
    received = measure_state(
        state,
        ATTACK_MODE,
        basis
    )

    # Chi-square
    chi = calculate_chi_square(
        original,
        received
    )

    total_chi_square += chi

    # Detect
    detected = chi > THRESHOLD


    # --------------------------------------------------------
    # Store result
    # --------------------------------------------------------

    if detected:

        threat_rounds += 1

        if ATTACK_MODE == "X":
            x_detected += 1

        elif ATTACK_MODE == "Z":
            z_detected += 1

    else:

        # Determine whether attack is theoretically invisible
        invisible = False

        if ATTACK_MODE == "X" and state in ["+", "-"]:
            invisible = True

        if ATTACK_MODE == "Z" and state in ["0", "1"]:
            invisible = True

        if invisible:
            invisible_rounds += 1

        else:
            normal_rounds += 1


    # --------------------------------------------------------
    # Print selected rounds
    # --------------------------------------------------------

    if round_number <= 10 or round_number % 10 == 0:

        print(
            f"\nRound {round_number:03d}"
        )

        print(
            "State:",
            "|" + state + ">"
        )

        print(
            "Basis:",
            basis
        )

        print(
            "Original:",
            original
        )

        print(
            "Received:",
            received
        )

        print(
            "Chi-Square:",
            round(chi, 2)
        )

        if detected:

            print(
                "Result: 🚨 THREAT DETECTED"
            )

        elif invisible:

            print(
                "Result: ⚪ ATTACK NOT OBSERVABLE"
            )

        else:

            print(
                "Result: ✅ NORMAL"
            )


# ============================================================
# FINAL STATISTICS
# ============================================================

average_chi = total_chi_square / ROUNDS

threat_percentage = (
    threat_rounds / ROUNDS
) * 100

invisible_percentage = (
    invisible_rounds / ROUNDS
) * 100


# ============================================================
# FINAL REPORT
# ============================================================

print("\n\n")
print("=" * 70)
print("                 FINAL SECURITY REPORT")
print("=" * 70)

print("\nTotal Rounds:", ROUNDS)

print(
    "Threat Detected Rounds:",
    threat_rounds
)

print(
    "Attack Not Observable Rounds:",
    invisible_rounds
)

print(
    "Normal Rounds:",
    normal_rounds
)

print(
    "\nThreat Detection Rate:",
    round(threat_percentage, 2),
    "%"
)

print(
    "Invisible Attack Rate:",
    round(invisible_percentage, 2),
    "%"
)

print(
    "Average Chi-Square:",
    round(average_chi, 2)
)


# ============================================================
# ATTACK INFORMATION
# ============================================================

print("\n")
print("=" * 70)
print("                  ATTACK ANALYSIS")
print("=" * 70)

if ATTACK_MODE == "X":

    print("\nAttack Type: X / Bit Flip")

    print(
        "X attack changes |0> <-> |1>."
    )

    print(
        "It is detectable when Z-Basis is used"
    )

    print(
        "for computational-basis states."
    )

elif ATTACK_MODE == "Z":

    print("\nAttack Type: Z / Phase Flip")

    print(
        "Z attack changes |+> <-> |->."
    )

    print(
        "It is detectable when X-Basis is used"
    )

    print(
        "for phase-sensitive states."
    )

elif ATTACK_MODE == "NONE":

    print("\nNo attack applied.")


# ============================================================
# SECURITY DECISION
# ============================================================

print("\n")
print("=" * 70)
print("                 FINAL DECISION")
print("=" * 70)


if ATTACK_MODE == "NONE":

    if threat_rounds == 0:

        print("\n✅ SYSTEM NORMAL")
        print("No significant disturbance detected.")

    else:

        print("\n⚠ POSSIBLE NOISE / DISTURBANCE")


else:

    if threat_rounds > 0:

        print("\n🚨 QUANTUM THREAT DETECTED")

        print(
            "The measurement statistics show"
        )

        print(
            "significant disturbance in multiple rounds."
        )

    else:

        print(
            "\n⚪ NO OBSERVABLE THREAT"
        )

        print(
            "The selected attack was not detectable"
        )

        print(
            "for the sampled states/bases."
        )


# ============================================================
# PROJECT SUMMARY
# ============================================================

print("\n")
print("=" * 70)
print("                  PROJECT SUMMARY")
print("=" * 70)

print("""
The multi-round engine performs:

1. Random quantum state selection
2. Random measurement-basis selection
3. Quantum signature measurement
4. Pauli attack simulation
5. Received-state measurement
6. Chi-square statistical analysis
7. Multi-round aggregation
8. Threat detection
9. Invisible-attack analysis
10. Final security decision
""")

print("=" * 70)
print("          MULTI-ROUND DETECTION COMPLETED")
print("=" * 70)