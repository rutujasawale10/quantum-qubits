from qiskit import QuantumCircuit
from qiskit.quantum_info import Statevector
from qiskit.primitives import StatevectorSampler


# ============================================
# CREATE ORIGINAL QUANTUM SIGNATURE
# ============================================

original_circuit = QuantumCircuit(1)

# Original state = |+>
original_circuit.h(0)

original_state = Statevector.from_instruction(original_circuit)


# ============================================
# SELECT ATTACK
# ============================================

attack = "Z"
# Options:
# "NONE"
# "X"
# "Z"


# ============================================
# APPLY ATTACK
# ============================================

attack_circuit = QuantumCircuit(1)

if attack == "X":
    attack_circuit.x(0)

elif attack == "Z":
    attack_circuit.z(0)

elif attack == "NONE":
    pass

received_state = original_state.evolve(attack_circuit)


# ============================================
# DISPLAY STATES
# ============================================

print("=" * 55)
print("QUANTUM DIGITAL SIGNATURE ATTACK SIMULATOR")
print("=" * 55)

print("\nOriginal State:")
print(original_state)

print("\nAttack Applied:")
print(attack)

print("\nReceived State:")
print(received_state)


# ============================================
# X-BASIS MEASUREMENT
# ============================================

def x_basis_measurement(state, shots=1000):

    qc = QuantumCircuit(1, 1)

    qc.initialize(state.data, 0)

    # Convert X-basis measurement to Z-basis
    qc.h(0)

    qc.measure(0, 0)

    sampler = StatevectorSampler()

    result = sampler.run(
        [qc],
        shots=shots
    ).result()

    counts = result[0].data.c.get_counts()

    return counts


# ============================================
# MEASURE ORIGINAL AND RECEIVED STATES
# ============================================

original_counts = x_basis_measurement(original_state)

received_counts = x_basis_measurement(received_state)


print("\nOriginal X-Basis Measurement:")
print(original_counts)

print("\nReceived X-Basis Measurement:")
print(received_counts)


# ============================================
# THREAT DETECTION
# ============================================

original_0 = original_counts.get("0", 0)
original_1 = original_counts.get("1", 0)

received_0 = received_counts.get("0", 0)
received_1 = received_counts.get("1", 0)


print("\n" + "-" * 55)
print("THREAT ANALYSIS")
print("-" * 55)

print("Original  | 0 =", original_0, "| 1 =", original_1)
print("Received  | 0 =", received_0, "| 1 =", received_1)


# ============================================
# DECISION
# ============================================

if attack == "NONE":

    print("\nNo Attack Applied")
    print("Signature Status: VALID")

elif attack == "Z":

    if received_1 > 900:
        print("\nTHREAT DETECTED!")
        print("Attack Type: Z Attack")
        print("Signature Status: FORGED")

    else:
        print("\nNo Significant Threat Detected")

elif attack == "X":

    print("\nX Attack Applied")

    if received_1 > 900:
        print("THREAT DETECTED!")
        print("Signature Status: FORGED")

    else:
        print("No Significant Threat Detected")


print("\n" + "=" * 55)