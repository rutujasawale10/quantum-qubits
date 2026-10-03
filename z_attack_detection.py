from qiskit import QuantumCircuit
from qiskit.quantum_info import Statevector
from qiskit.primitives import StatevectorSampler


# -----------------------------------------
# Create original |+> state
# -----------------------------------------

original_circuit = QuantumCircuit(1)

original_circuit.h(0)

original_state = Statevector.from_instruction(original_circuit)


# -----------------------------------------
# Attacker applies Z gate
# -----------------------------------------

attack_circuit = QuantumCircuit(1)

attack_circuit.z(0)

received_state = original_state.evolve(attack_circuit)


# -----------------------------------------
# Display states
# -----------------------------------------

print("=" * 50)
print("QUANTUM Z-ATTACK DETECTION")
print("=" * 50)

print("\nOriginal State |+>:")
print(original_state)

print("\nAttack Applied:")
print("Z Gate")

print("\nReceived State:")
print(received_state)


# -----------------------------------------
# X-Basis measurement function
# -----------------------------------------

def x_basis_measurement(state, shots=1000):

    qc = QuantumCircuit(1, 1)

    # Convert statevector into circuit
    qc.initialize(state.data, 0)

    # X-basis measurement
    qc.h(0)

    qc.measure(0, 0)

    sampler = StatevectorSampler()

    result = sampler.run(
        [qc],
        shots=shots
    ).result()

    counts = result[0].data.c.get_counts()

    return counts


# -----------------------------------------
# Measure original and received states
# -----------------------------------------

original_counts = x_basis_measurement(original_state)

received_counts = x_basis_measurement(received_state)


# -----------------------------------------
# Display measurement results
# -----------------------------------------

print("\nOriginal X-Basis Measurement:")
print(original_counts)

print("\nReceived X-Basis Measurement:")
print(received_counts)


# -----------------------------------------
# Detection
# -----------------------------------------

original_0 = original_counts.get("0", 0)
received_1 = received_counts.get("1", 0)


if original_0 > 900 and received_1 > 900:

    print("\nTHREAT DETECTED!")
    print("Signature Status: FORGED")

else:

    print("\nNo Significant Threat Detected")


print("\n" + "=" * 50)