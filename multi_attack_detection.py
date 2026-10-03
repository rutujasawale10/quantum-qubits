from qiskit import QuantumCircuit
from qiskit.primitives import StatevectorSampler


# ============================================
# MEASURE STATE IN X-BASIS
# ============================================

def measure_state(state, shots=1000):

    qc = QuantumCircuit(1, 1)

    # Create the required state
    if state == "+":
        qc.h(0)

    elif state == "-":
        qc.x(0)
        qc.h(0)

    # X-basis measurement
    qc.h(0)
    qc.measure(0, 0)

    sampler = StatevectorSampler()

    result = sampler.run(
        [qc],
        shots=shots
    ).result()

    return result[0].data.c.get_counts()


# ============================================
# CHI-SQUARE CALCULATION
# ============================================

def calculate_chi_square(observed, expected):

    chi = 0

    for i in range(2):

        if expected[i] > 0:
            chi += ((observed[i] - expected[i]) ** 2) / expected[i]

    return chi


# ============================================
# ORIGINAL SIGNATURE
# ============================================

original_counts = measure_state("+", 1000)

original_0 = original_counts.get("0", 0)
original_1 = original_counts.get("1", 0)

expected = [original_0, original_1]


print("=" * 65)
print("QUANTUM DIGITAL SIGNATURE MULTI-ATTACK DETECTOR")
print("=" * 65)

print("\nOriginal Signature: |+>")
print("Measurement:", original_counts)


# ============================================
# ATTACK DEFINITIONS
# ============================================

attacks = {
    "NONE": "+",
    "X": "+",
    "Z": "-"
}


# ============================================
# TEST EACH ATTACK
# ============================================

threshold = 10

print("\n" + "-" * 65)
print("ATTACK ANALYSIS")
print("-" * 65)


for attack, received_state in attacks.items():

    received_counts = measure_state(received_state, 1000)

    received_0 = received_counts.get("0", 0)
    received_1 = received_counts.get("1", 0)

    observed = [received_0, received_1]

    chi_value = calculate_chi_square(
        observed,
        expected
    )

    print("\nAttack:", attack)

    print("Received Measurement:", received_counts)

    print("Chi-Square Value:",
          round(chi_value, 2))

    if chi_value > threshold:

        print("Result: THREAT DETECTED")
        print("Signature Status: FORGED")

    else:

        print("Result: NORMAL")
        print("Signature Status: VALID")


# ============================================
# FINAL INFORMATION
# ============================================

print("\n" + "=" * 65)
print("Detection Threshold:", threshold)
print("=" * 65)