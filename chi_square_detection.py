from qiskit import QuantumCircuit
from qiskit.primitives import StatevectorSampler


# ============================================
# CREATE QUANTUM STATE
# ============================================

def create_state(state_name):

    qc = QuantumCircuit(1, 1)

    if state_name == "+":
        # |+> state
        qc.h(0)

    elif state_name == "-":
        # |-> state
        qc.x(0)
        qc.h(0)

    # X-basis measurement
    qc.h(0)
    qc.measure(0, 0)

    return qc


# ============================================
# GET MEASUREMENT COUNTS
# ============================================

def get_measurements(state_name, shots=1000):

    qc = create_state(state_name)

    sampler = StatevectorSampler()

    result = sampler.run(
        [qc],
        shots=shots
    ).result()

    counts = result[0].data.c.get_counts()

    return counts


# ============================================
# CHI-SQUARE CALCULATION
# ============================================

def chi_square(observed, expected):

    value = 0

    for i in range(len(observed)):

        if expected[i] != 0:
            value += ((observed[i] - expected[i]) ** 2) / expected[i]

    return value


# ============================================
# ORIGINAL SIGNATURE
# ============================================

original_counts = get_measurements("+", 1000)


# ============================================
# ATTACKED SIGNATURE
# ============================================

# Z attack changes |+> into |->
received_counts = get_measurements("-", 1000)


# ============================================
# DISPLAY RESULTS
# ============================================

print("=" * 55)
print("CHI-SQUARE QUANTUM SIGNATURE THREAT DETECTION")
print("=" * 55)

print("\nOriginal Signature |+>:")
print(original_counts)

print("\nReceived Signature after Z Attack |->:")
print(received_counts)


# ============================================
# OBSERVED VALUES
# ============================================

original_0 = original_counts.get("0", 0)
original_1 = original_counts.get("1", 0)

received_0 = received_counts.get("0", 0)
received_1 = received_counts.get("1", 0)


print("\nOriginal Distribution:")
print("0 =", original_0)
print("1 =", original_1)

print("\nReceived Distribution:")
print("0 =", received_0)
print("1 =", received_1)


# ============================================
# EXPECTED VALUES
# ============================================

expected = [original_0, original_1]

observed = [received_0, received_1]


# ============================================
# CHI-SQUARE TEST
# ============================================

chi_value = chi_square(observed, expected)


print("\n" + "-" * 55)

print("Chi-Square Value:")
print(round(chi_value, 2))


# ============================================
# THRESHOLD
# ============================================

threshold = 10

print("\nDetection Threshold:")
print(threshold)


# ============================================
# FINAL DECISION
# ============================================

print("\n" + "-" * 55)

if chi_value > threshold:

    print("THREAT DETECTED!")
    print("Statistical Result: ANOMALY")
    print("Signature Status: FORGED")

else:

    print("NO SIGNIFICANT THREAT")
    print("Statistical Result: NORMAL")
    print("Signature Status: VALID")


print("\n" + "=" * 55)