from qiskit import QuantumCircuit
from qiskit.quantum_info import Statevector

# ============================================================
# MEMBER 2 - QDS SIGNATURE LAYER
# ============================================================

def create_quantum_state(state_name):
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


def generate_signature(message, state_name):
    """
    Educational QDS-inspired signature generation.
    The quantum state is used as the signature state.
    """

    signature = {
        "message": message,
        "state": state_name,
        "quantum_state": create_quantum_state(state_name)
    }

    return signature


def verify_signature(original_signature, received_state):
    """
    Compare the original signed quantum state
    with the received quantum state.
    """

    original_state = original_signature["quantum_state"]

    if original_state.equiv(received_state):
        return "VALID"
    else:
        return "FORGED"


# ============================================================
# DEMO
# ============================================================

message = "SIH Quantum Digital Signature"

# Alice generates a signature
signature = generate_signature(message, "+")

print("=" * 60)
print("        QDS SIGNATURE GENERATION")
print("=" * 60)

print("\nMessage:")
print(signature["message"])

print("\nSignature Quantum State:")
print(signature["state"])

print("\nQuantum Statevector:")
print(signature["quantum_state"])


# Bob receives the same state
received_state = create_quantum_state("+")

result = verify_signature(signature, received_state)

print("\n" + "=" * 60)
print("        SIGNATURE VERIFICATION")
print("=" * 60)

print("\nOriginal State : +")
print("Received State : +")

if result == "VALID":
    print("\nSignature Verification: VALID")
else:
    print("\nSignature Verification: FORGED")


# ============================================================
# FORGERY TEST
# ============================================================

forged_state = create_quantum_state("-")

forged_result = verify_signature(signature, forged_state)

print("\n" + "=" * 60)
print("        FORGERY TEST")
print("=" * 60)

print("\nOriginal State : +")
print("Attacker State : -")

if forged_result == "VALID":
    print("\nSignature Verification: VALID")
else:
    print("\nSignature Verification: FORGED")

print("\n" + "=" * 60)