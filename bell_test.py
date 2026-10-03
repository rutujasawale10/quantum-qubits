from qiskit import QuantumCircuit
from qiskit.primitives import StatevectorSampler

qc = QuantumCircuit(2, 2)

# Create Bell State
qc.h(0)
qc.cx(0, 1)

# Measure both qubits
qc.measure(0, 0)
qc.measure(1, 1)

sampler = StatevectorSampler()
result = sampler.run([qc], shots=1000).result()

counts = result[0].data.c.get_counts()

print("Bell State Results:")
print(counts)