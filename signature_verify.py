from qiskit import QuantumCircuit
from qiskit.quantum_info import Statevector

def create_state(state_name):
    qc = QuantumCircuit(1)

    if state_name == "0":
        pass

    elif state_name == "1":
        qc.x(0)

    elif state_name == "+":
        qc.h(0)

    elif state_name == "-":
        qc.x(0)
        qc.h(0)

    return Statevector.from_instruction(qc)


# Original signed state
original = create_state("+")

# Received state
received = create_state("-")

print("Original State:")
print(original)

print("\nReceived State:")
print(received)

# Compare statevectors
if original.equiv(received):
    print("\nSignature Verification: VALID")
else:
    print("\nSignature Verification: FORGED")