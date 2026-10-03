from qiskit import QuantumCircuit
from qiskit.primitives import StatevectorSampler


# -----------------------------------------
# Create quantum state
# -----------------------------------------

def create_state(state_name):

    qc = QuantumCircuit(1, 1)

    if state_name == "+":
        # |+> = H|0>
        qc.h(0)

    elif state_name == "-":
        # |-> = H|1>
        qc.x(0)
        qc.h(0)

    # -------------------------------------
    # X-basis measurement
    #
    # H before measurement converts:
    # |+> -> |0>
    # |-> -> |1>
    # -------------------------------------

    qc.h(0)

    qc.measure(0, 0)

    return qc


# -----------------------------------------
# Run measurements
# -----------------------------------------

def measure_state(state_name, shots=1000):

    qc = create_state(state_name)

    sampler = StatevectorSampler()

    result = sampler.run(
        [qc],
        shots=shots
    ).result()

    counts = result[0].data.c.get_counts()

    return counts


# -----------------------------------------
# Measure |+>
# -----------------------------------------

plus_counts = measure_state("+", 1000)


# -----------------------------------------
# Measure |->
# -----------------------------------------

minus_counts = measure_state("-", 1000)


# -----------------------------------------
# Display results
# -----------------------------------------

print("=" * 50)
print("QUANTUM SIGNATURE BASIS VERIFICATION")
print("=" * 50)

print("\nState |+> X-Basis Measurement:")
print(plus_counts)

print("\nState |-> X-Basis Measurement:")
print(minus_counts)


# -----------------------------------------
# Convert to percentages
# -----------------------------------------

plus_0 = plus_counts.get("0", 0)
plus_1 = plus_counts.get("1", 0)

minus_0 = minus_counts.get("0", 0)
minus_1 = minus_counts.get("1", 0)


print("\n|+> Distribution:")
print("0 =", plus_0 / 10, "%")
print("1 =", plus_1 / 10, "%")


print("\n|-> Distribution:")
print("0 =", minus_0 / 10, "%")
print("1 =", minus_1 / 10, "%")


# -----------------------------------------
# Verification
# -----------------------------------------

if plus_0 > plus_1 and minus_1 > minus_0:

    print("\nResult: STATES SUCCESSFULLY DISTINGUISHED")

else:

    print("\nResult: CHECK MEASUREMENT")