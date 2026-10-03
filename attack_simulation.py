from qiskit import QuantumCircuit
from qiskit.quantum_info import Statevector


# Function to create original quantum state
def create_original_state():
    qc = QuantumCircuit(1)

    # Original state = |0>
    # Qubit automatically starts in |0>

    return Statevector.from_instruction(qc)


# Function to apply attack
def apply_attack(state, attack):
    qc = QuantumCircuit(1)

    if attack == "NONE":
        pass

    elif attack == "X":
        qc.x(0)

    elif attack == "Z":
        qc.z(0)

    return state.evolve(qc)


# ---------------------------------
# MAIN PROGRAM
# ---------------------------------

# Create original quantum signature
original = create_original_state()

# Select attack
attack = "X"

# Attacker modifies the quantum state
received = apply_attack(original, attack)


# ---------------------------------
# DISPLAY RESULTS
# ---------------------------------

print("=" * 45)
print("QUANTUM SIGNATURE ATTACK SIMULATION")
print("=" * 45)

print("\nOriginal State:")
print(original)

print("\nAttack Applied:")
print(attack)

print("\nReceived State:")
print(received)


# ---------------------------------
# SIGNATURE VERIFICATION
# ---------------------------------

print("\nVerification Result:")

if original.equiv(received):
    print("Signature Verification: VALID")
else:
    print("Signature Verification: FORGED")


print("\n" + "=" * 45)