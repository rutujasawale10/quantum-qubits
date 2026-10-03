from qiskit import QuantumCircuit
from qiskit.primitives import StatevectorSampler


# ============================================================
# QUANTUM DIGITAL SIGNATURE THREAT DETECTION ENGINE
# ============================================================

SHOTS = 1000
THRESHOLD = 10

STATES = ["0", "1", "+", "-"]
ATTACKS = ["NONE", "X", "Z"]


# ============================================================
# CREATE QUANTUM STATE
# ============================================================

def create_state(state_name):

    qc = QuantumCircuit(1)

    if state_name == "0":
        # |0>
        pass

    elif state_name == "1":
        # |1>
        qc.x(0)

    elif state_name == "+":
        # |+> = H|0>
        qc.h(0)

    elif state_name == "-":
        # |-> = H|1>
        qc.x(0)
        qc.h(0)

    return qc


# ============================================================
# APPLY PAULI ATTACK
# ============================================================

def apply_attack(qc, attack):

    if attack == "NONE":
        pass

    elif attack == "X":
        # Bit Flip Attack
        qc.x(0)

    elif attack == "Z":
        # Phase Flip Attack
        qc.z(0)

    return qc


# ============================================================
# MEASURE QUANTUM STATE
# ============================================================

def measure_state(state_name, attack, basis):

    qc = create_state(state_name)

    # Apply attack
    qc = apply_attack(qc, attack)

    # X-basis measurement
    if basis == "X":
        qc.h(0)

    # Measurement
    qc.measure_all()

    sampler = StatevectorSampler()

    result = sampler.run(
        [qc],
        shots=SHOTS
    ).result()

    counts = result[0].data.meas.get_counts()

    return counts


# ============================================================
# CHI-SQUARE CALCULATION
# ============================================================

def chi_square(expected, observed):

    value = 0.0

    for bit in ["0", "1"]:

        expected_count = expected.get(bit, 0)
        observed_count = observed.get(bit, 0)

        if expected_count > 0:

            value += (
                (observed_count - expected_count) ** 2
            ) / expected_count

        elif observed_count > 0:

            value += observed_count

    return value


# ============================================================
# DETECT ONE STATE + ONE ATTACK
# ============================================================

def detect_attack(state, attack):

    # Original state measurements
    original_z = measure_state(
        state,
        "NONE",
        "Z"
    )

    original_x = measure_state(
        state,
        "NONE",
        "X"
    )

    # Received state measurements
    received_z = measure_state(
        state,
        attack,
        "Z"
    )

    received_x = measure_state(
        state,
        attack,
        "X"
    )

    # Statistical analysis
    chi_z = chi_square(
        original_z,
        received_z
    )

    chi_x = chi_square(
        original_x,
        received_x
    )

    z_detected = chi_z > THRESHOLD
    x_detected = chi_x > THRESHOLD

    threat = z_detected or x_detected

    return (
        original_z,
        original_x,
        received_z,
        received_x,
        chi_z,
        chi_x,
        z_detected,
        x_detected,
        threat
    )


# ============================================================
# MAIN ENGINE
# ============================================================

print("=" * 70)
print("      QUANTUM DIGITAL SIGNATURE SECURITY")
print("             THREAT DETECTION ENGINE")
print("=" * 70)

print("\nMeasurement Shots:", SHOTS)
print("Detection Threshold:", THRESHOLD)

print("\nQuantum States:")
print("|0>  |1>  |+>  |->")

print("\nAttacks:")
print("NONE  X(Bit Flip)  Z(Phase Flip)")

print("\nMeasurement Bases:")
print("Z-Basis  X-Basis")


# ============================================================
# TEST ALL STATES
# ============================================================

for state in STATES:

    print("\n")
    print("=" * 70)
    print("ORIGINAL QUANTUM STATE:", "|" + state + ">")
    print("=" * 70)

    for attack in ATTACKS:

        print("\n" + "-" * 70)
        print("ATTACK:", attack)
        print("-" * 70)

        (
            original_z,
            original_x,
            received_z,
            received_x,
            chi_z,
            chi_x,
            z_detected,
            x_detected,
            threat
        ) = detect_attack(state, attack)

        # ----------------------------------------------------
        # ORIGINAL
        # ----------------------------------------------------

        print("\nORIGINAL MEASUREMENTS")

        print("Z-Basis:", original_z)
        print("X-Basis:", original_x)

        # ----------------------------------------------------
        # RECEIVED
        # ----------------------------------------------------

        print("\nRECEIVED MEASUREMENTS")

        print("Z-Basis:", received_z)
        print("X-Basis:", received_x)

        # ----------------------------------------------------
        # STATISTICAL ANALYSIS
        # ----------------------------------------------------

        print("\nSTATISTICAL ANALYSIS")

        print(
            "Z-Basis Chi-Square:",
            round(chi_z, 2)
        )

        print(
            "X-Basis Chi-Square:",
            round(chi_x, 2)
        )

        print(
            "Detection Threshold:",
            THRESHOLD
        )

        # ----------------------------------------------------
        # FINAL DECISION
        # ----------------------------------------------------

        print("\nFINAL SECURITY DECISION")

        if attack == "NONE":

            if threat:

                print("⚠ UNEXPECTED DISTURBANCE")

            else:

                print("✅ NO THREAT")
                print("Security Status: VALID / NORMAL")

        else:

            if threat:

                print("🚨 THREAT DETECTED")
                print("Security Status: FORGED")

                if z_detected:
                    print("Detection Basis: Z-Basis")

                if x_detected:
                    print("Detection Basis: X-Basis")

            else:

                print("⚪ ATTACK NOT OBSERVABLE")
                print("Security Status: NOT DISTURBED")

        # ----------------------------------------------------
        # QUANTUM EXPLANATION
        # ----------------------------------------------------

        print("\nQUANTUM EXPLANATION")

        if attack == "NONE":

            print(
                "No attack was applied."
            )

        elif attack == "X":

            if state in ["0", "1"]:

                print(
                    "X attack flips |0> and |1>."
                )

                print(
                    "Therefore it is detectable in Z-Basis."
                )

            else:

                print(
                    "X attack does not change the"
                )

                print(
                    "physical state of |+> and |->."
                )

                print(
                    "Therefore it is not observable here."
                )

        elif attack == "Z":

            if state in ["0", "1"]:

                print(
                    "Z attack changes phase only."
                )

                print(
                    "For |0> and |1>, this phase"
                )

                print(
                    "is not observable in Z-Basis."
                )

            else:

                print(
                    "Z attack changes |+> into |->"
                )

                print(
                    "and |-> into |+>."
                )

                print(
                    "Therefore it is detectable in X-Basis."
                )


# ============================================================
# FINAL DETECTION MATRIX
# ============================================================

print("\n\n")
print("=" * 70)
print("                 FINAL DETECTION MATRIX")
print("=" * 70)

print("\nState       Attack       Result")
print("-" * 70)

print("|0>         NONE         NORMAL")
print("|0>         X            DETECTED - Z-Basis")
print("|0>         Z            NOT OBSERVABLE")

print("|1>         NONE         NORMAL")
print("|1>         X            DETECTED - Z-Basis")
print("|1>         Z            NOT OBSERVABLE")

print("|+>         NONE         NORMAL")
print("|+>         X            NOT OBSERVABLE")
print("|+>         Z            DETECTED - X-Basis")

print("|->         NONE         NORMAL")
print("|->         X            NOT OBSERVABLE")
print("|->         Z            DETECTED - X-Basis")


# ============================================================
# PROJECT SUMMARY
# ============================================================

print("\n")
print("=" * 70)
print("                 PROJECT SUMMARY")
print("=" * 70)

print("""
This engine demonstrates quantum digital signature
threat detection using:

1. Quantum states
2. Pauli X attack
3. Pauli Z attack
4. Z-Basis measurement
5. X-Basis measurement
6. Chi-square statistical analysis
7. Threshold-based detection
8. Forgery detection
""")

print("=" * 70)
print("        QUANTUM DETECTION ENGINE COMPLETED")
print("=" * 70)