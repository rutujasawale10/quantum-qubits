from qiskit import QuantumCircuit
from qiskit.quantum_info import Statevector

qc = QuantumCircuit(3)

# 1. Create unknown/superposition state |+> on q0
qc.h(0)

# 2. Create Bell pair between q1 and q2
qc.h(1)
qc.cx(1, 2)

# 3. Alice's teleportation operations
qc.cx(0, 1)
qc.h(0)

# 4. Bob's corrections
qc.cx(1, 2)
qc.cz(0, 2)

# 5. Get final state
state = Statevector.from_instruction(qc)

print("Final Statevector:")
print(state)

print("\nFinal Probabilities:")
print(state.probabilities_dict())

print("\nTeleportation Circuit:")
print(qc)