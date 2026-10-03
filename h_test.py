from qiskit import QuantumCircuit
from qiskit.primitives import StatevectorSampler

qc = QuantumCircuit(1, 1)

qc.h(0)
qc.measure(0, 0)

sampler = StatevectorSampler()
result = sampler.run([qc], shots=1000).result()

counts = result[0].data.c.get_counts()

print("Measurement Results:")
print(counts)