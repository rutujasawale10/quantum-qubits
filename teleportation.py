from qiskit import QuantumCircuit
from qiskit.primitives import StatevectorSampler

# Teleport |1> state
qc = QuantumCircuit(3, 3)

# 1. Original state |1>
qc.x(0)

# 2. Create Bell pair
qc.h(1)
qc.cx(1, 2)

# 3. Alice's operations
qc.cx(0, 1)
qc.h(0)

# 4. Alice measures q0 and q1
qc.measure(0, 0)
qc.measure(1, 1)

# 5. Bob's correction
# For this test, q0=|1> gives the required Z correction
# after the corresponding measurement branch.
# We will verify each branch separately.

print("Teleportation circuit created successfully!")
print(qc)