from qiskit import QuantumCircuit
from qiskit.primitives import StatevectorSampler


# ============================================
# MEASURE IN Z-BASIS
# ============================================

def measure_z_basis(state, shots=1000):

    qc = QuantumCircuit(1, 1)

    if state == "+":
        qc.h(0)

    elif state == "-":
        qc.x(0)
        qc.h(0)

    qc.measure(0, 0)

    sampler = StatevectorSampler()

    result = sampler.run(
        [qc],
        shots=shots
    ).result()

    return result[0].data.c.get_counts()


# ============================================
# MEASURE IN X-BASIS
# ============================================

def measure_x_basis(state, shots=1000):

    qc = QuantumCircuit(1, 1)

    if state == "+":
        qc.h(0)

    elif state == "-":
        qc.x(0)
        qc.h(0)

    # H converts X-basis measurement to Z-basis
    qc.h(0)

    qc.measure(0, 0)

    sampler = StatevectorSampler()

    result = sampler.run(
        [qc],
        shots=shots
    ).result()

    return result[0].data.c.get_counts()


# ============================================
# CHI-SQUARE
# ============================================

def chi_square(observed, expected):

    value = 0

    for i in range(2):

        if expected[i] > 0:
            value += ((observed[i] - expected[i]) ** 2) / expected[i]

    return value


# ============================================
# ORIGINAL SIGNATURE
# ============================================

original_state = "+"


# Original measurements
original_z = measure_z_basis(original_state)
original_x = measure_x_basis(original_state)


print("=" * 65)
print("DUAL-BASIS QUANTUM SIGNATURE DETECTION")
print("=" * 65)

print("\nOriginal Signature: |+>")

print("\nOriginal Z-Basis:")
print(original_z)

print("\nOriginal X-Basis:")
print(original_x)


# ============================================
# EXPECTED VALUES
# ============================================

expected_z = [
    original_z.get("0", 0),
    original_z.get("1", 0)
]

expected_x = [
    original_x.get("0", 0),
    original_x.get("1", 0)
]


# ============================================
# ATTACK STATES
# ============================================

attacks = {

    "NONE": "+",

    # X|+> = |+>
    "X": "+",

    # Z|+> = |->
    "Z": "-"
}


# ============================================
# DETECTION
# ============================================

threshold = 10


print("\n" + "-" * 65)
print("ATTACK ANALYSIS")
print("-" * 65)


for attack, received_state in attacks.items():

    received_z = measure_z_basis(
        received_state,
        1000
    )

    received_x = measure_x_basis(
        received_state,
        1000
    )


    # Received Z values
    observed_z = [
        received_z.get("0", 0),
        received_z.get("1", 0)
    ]


    # Received X values
    observed_x = [
        received_x.get("0", 0),
        received_x.get("1", 0)
    ]


    # Calculate Chi-Square
    chi_z = chi_square(
        observed_z,
        expected_z
    )

    chi_x = chi_square(
        observed_x,
        expected_x
    )


    print("\nAttack:", attack)

    print("Z-Basis Measurement:")
    print(received_z)

    print("X-Basis Measurement:")
    print(received_x)

    print("\nZ-Basis Chi-Square:",
          round(chi_z, 2))

    print("X-Basis Chi-Square:",
          round(chi_x, 2))


    # ========================================
    # FINAL DECISION
    # ========================================

    if chi_z > threshold or chi_x > threshold:

        print("\n🚨 THREAT DETECTED")

        if chi_z > threshold:
            print("Detected through: Z-Basis")

        if chi_x > threshold:
            print("Detected through: X-Basis")

        print("Signature Status: FORGED")

    else:

        print("\n✅ NO SIGNIFICANT THREAT")

        print("Signature Status: VALID")


print("\n" + "=" * 65)
print("Detection Threshold:", threshold)
print("=" * 65)