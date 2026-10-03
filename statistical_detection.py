from qiskit import QuantumCircuit
from qiskit.primitives import StatevectorSampler


# ---------------------------------
# FUNCTION: Create quantum state
# ---------------------------------

def create_state(state_name):

    qc = QuantumCircuit(1, 1)

    if state_name == "0":
        # |0> is the default state
        pass

    elif state_name == "1":
        # Create |1>
        qc.x(0)

    elif state_name == "+":
        # Create |+>
        qc.h(0)

    elif state_name == "-":
        # Create |->
        qc.x(0)
        qc.h(0)

    # Measure the qubit
    qc.measure(0, 0)

    return qc


# ---------------------------------
# FUNCTION: Run measurements
# ---------------------------------

def get_measurements(state_name, shots=1000):

    qc = create_state(state_name)

    sampler = StatevectorSampler()

    result = sampler.run([qc], shots=shots).result()

    counts = result[0].data.c.get_counts()

    return counts


# ---------------------------------
# ORIGINAL SIGNATURE
# ---------------------------------

original_counts = get_measurements("+", 1000)


# ---------------------------------
# RECEIVED SIGNATURE
# ---------------------------------

received_counts = get_measurements("+", 1000)


# ---------------------------------
# DISPLAY RESULTS
# ---------------------------------

print("=" * 50)
print("QUANTUM SIGNATURE STATISTICAL DETECTION")
print("=" * 50)

print("\nOriginal Signature: |+>")
print("Original Measurements:")
print(original_counts)

print("\nReceived Signature: |+>")
print("Received Measurements:")
print(received_counts)


# ---------------------------------
# CALCULATE PERCENTAGES
# ---------------------------------

original_0 = original_counts.get("0", 0)
original_1 = original_counts.get("1", 0)

received_0 = received_counts.get("0", 0)
received_1 = received_counts.get("1", 0)


print("\nOriginal Distribution:")
print("0 =", original_0 / 10, "%")
print("1 =", original_1 / 10, "%")

print("\nReceived Distribution:")
print("0 =", received_0 / 10, "%")
print("1 =", received_1 / 10, "%")


# ---------------------------------
# BASIC THRESHOLD CHECK
# ---------------------------------

difference_0 = abs(original_0 - received_0)
difference_1 = abs(original_1 - received_1)

threshold = 100

print("\nDifference:")
print("Difference in 0 =", difference_0)
print("Difference in 1 =", difference_1)

print("\nThreshold =", threshold)


# ---------------------------------
# VERIFICATION
# ---------------------------------

if difference_0 <= threshold and difference_1 <= threshold:

    print("\nDetection Result: NORMAL")
    print("Signature Status: VALID")

else:

    print("\nDetection Result: ANOMALY DETECTED")
    print("Signature Status: POSSIBLE FORGERY")


print("\n" + "=" * 50)