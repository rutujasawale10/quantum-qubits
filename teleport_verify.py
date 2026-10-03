from qiskit import QuantumCircuit
from qiskit.quantum_info import Statevector

qc = QuantumCircuit(3)

# Original state |1> on q0
qc.x(0)

# Create Bell pair q1-q2
qc.h(1)
qc.cx(1, 2)

# Alice's operations
qc.cx(0, 1)
qc.h(0)

# Bob's corrections
qc.cx(1, 2)
qc.cz(0, 2)

# Final state
state = Statevector.from_instruction(qc)

print("Final Statevector:")
print(state)

print("\nFinal Probabilities:")
print(state.probabilities_dict())

print("\nTeleportation circuit:")
print(qc)