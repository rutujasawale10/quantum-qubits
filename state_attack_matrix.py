from qiskit import QuantumCircuit
from qiskit.primitives import StatevectorSampler


# ============================================
# CREATE QUANTUM STATE
# ============================================

def create_state(state_name):

    qc = QuantumCircuit(1, 1)

    if state_name == "0":
        # |0>
        pass

    elif state_name == "1":
        # |1>
        qc.x(0)

    elif state_name == "+":
        # |+>
        qc.h(0)

    elif state_name == "-":
        # |->
        qc.x(0)
        qc.h(0)

    return qc


# ============================================
# APPLY ATTACK
# ============================================

def apply_attack(qc, attack):

    if attack == "X":
        qc.x(0)

    elif attack == "Z":
        qc.z(0)

    elif attack == "NONE":
        pass

    return qc


# ============================================
# MEASURE IN Z-BASIS
# ============================================

def measure_z_basis(state, attack, shots=1000):

    qc = create_state(state)

    qc = apply_attack(qc, attack)

    qc.measure(0, 0)

    sampler = StatevectorSampler()

    result = sampler.run(
        [qc],
        shots=shots
    ).result()

    return result[0].data.c.get_counts()


# ============================================
# MEASURE IN X-BASIS
# ============================================

def measure_x_basis(state, attack, shots=1000):

    qc = create_state(state)

    qc = apply_attack(qc, attack)

    # Convert X-basis measurement to Z-basis
    qc.h(0)

    qc.measure(0, 0)

    sampler = StatevectorSampler()

    result = sampler.run(
        [qc],
        shots=shots
    ).result()

    return result[0].data.c.get_counts()


# ============================================
# DISPLAY HEADER
# ============================================

print("=" * 70)
print("QUANTUM STATE - ATTACK DETECTION MATRIX")
print("=" * 70)


states = ["0", "1", "+", "-"]

attacks = ["NONE", "X", "Z"]


# ============================================
# TEST ALL STATES AND ATTACKS
# ============================================

for state in states:

    print("\n" + "-" * 70)
    print("ORIGINAL STATE:", "|" + state + ">")
    print("-" * 70)

    # Original measurements
    original_z = measure_z_basis(state, "NONE")
    original_x = measure_x_basis(state, "NONE")

    print("\nOriginal Z-Basis:", original_z)
    print("Original X-Basis:", original_x)

    for attack in attacks:

        received_z = measure_z_basis(
            state,
            attack
        )

        received_x = measure_x_basis(
            state,
            attack
        )

        # ====================================
        # GET COUNTS
        # ====================================

        z_0 = received_z.get("0", 0)
        z_1 = received_z.get("1", 0)

        x_0 = received_x.get("0", 0)
        x_1 = received_x.get("1", 0)


        # ====================================
        # SIMPLE CHANGE DETECTION
        # ====================================

        original_z_0 = original_z.get("0", 0)
        original_z_1 = original_z.get("1", 0)

        original_x_0 = original_x.get("0", 0)
        original_x_1 = original_x.get("1", 0)


        z_changed = (
            abs(z_0 - original_z_0) > 100
            or
            abs(z_1 - original_z_1) > 100
        )

        x_changed = (
            abs(x_0 - original_x_0) > 100
            or
            abs(x_1 - original_x_1) > 100
        )


        # ====================================
        # RESULT
        # ====================================

        print("\nAttack:", attack)

        print("Z-Basis:", received_z)
        print("X-Basis:", received_x)

        if attack == "NONE":

            print("Result: NORMAL")

        elif z_changed or x_changed:

            print("Result: THREAT DETECTED")

            if z_changed:
                print("Detected in: Z-Basis")

            if x_changed:
                print("Detected in: X-Basis")

        else:

            print("Result: ATTACK NOT DETECTED")

            print("Reason: This state/basis combination")
            print("does not reveal the attack.")


# ============================================
# END
# ============================================

print("\n" + "=" * 70)
print("STATE-ATTACK ANALYSIS COMPLETED")
print("=" * 70)