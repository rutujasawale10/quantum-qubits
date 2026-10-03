from qiskit import QuantumCircuit
from qiskit.quantum_info import Statevector

states = {
    "0": [],
    "1": ["X"],
    "+": ["H"],
    "-": ["X", "H"]
}

for name, gates in states.items():

    qc = QuantumCircuit(1)

    for gate in gates:
        if gate == "X":
            qc.x(0)
        elif gate == "H":
            qc.h(0)

    state = Statevector.from_instruction(qc)

    print("=" * 40)
    print("Quantum Signature State:", name)
    print("Statevector:")
    print(state)

    print("Probabilities:")
    print(state.probabilities_dict())