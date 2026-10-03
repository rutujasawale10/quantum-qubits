from qiskit import QuantumCircuit
from qiskit.primitives import StatevectorSampler

qc = QuantumCircuit(3, 1)

# 1. Original state |+> on q0
qc.h(0)

# 2. Create Bell pair
qc.h(1)
qc.cx(1, 2)

# 3. Alice's operations
qc.cx(0, 1)
qc.h(0)

# 4. Bob's corrections
qc.cx(1, 2)
qc.cz(0, 2)

# 5. Measure Bob's qubit q2
qc.measure(2, 0)

sampler = StatevectorSampler()

result = sampler.run([qc], shots=1000).result()

counts = result[0].data.c.get_counts()

print("Bob's Measurement Results:")
print(counts)

print("\nTeleportation Circuit:")
print(qc)