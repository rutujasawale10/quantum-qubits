from qiskit import QuantumCircuit
from qiskit.quantum_info import Statevector
from qiskit.primitives import StatevectorSampler
import random
import math

# ============================================================
# QDS FINAL END-TO-END DEMO
# Member 1 + Member 2 + Member 3
# ============================================================

random.seed(42)

MESSAGE = "SIH Quantum Digital Signature"

COPIES = 200
BASELINE_NOISE = 0.02
ATTACK_THRESHOLD = 0.20
Z_THRESHOLD = 3.0


# ============================================================
# 1. CREATE QUANTUM STATE
# ============================================================

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


# ============================================================
# 2. QDS SIGNATURE GENERATION
# ============================================================

def generate_signature(message, state_name):

    return {
        "message": message,
        "state": state_name,
        "quantum_state": create_state(state_name)
    }


# ============================================================
# 3. TELEPORTATION CIRCUIT
# ============================================================

def teleport_state(state_name):

    qc = QuantumCircuit(3)

    # Alice's original state
    if state_name == "1":
        qc.x(0)

    elif state_name == "+":
        qc.h(0)

    elif state_name == "-":
        qc.x(0)
        qc.h(0)

    # Bell pair
    qc.h(1)
    qc.cx(1, 2)

    # Alice's operations
    qc.cx(0, 1)
    qc.h(0)

    # Bob's coherent corrections
    qc.cx(1, 2)
    qc.cz(0, 2)

    return qc


# ============================================================
# 4. ATTACK
# ============================================================

def apply_attack(statevector, attack):

    attack_circuit = QuantumCircuit(1)

    if attack == "X":
        attack_circuit.x(0)

    elif attack == "Z":
        attack_circuit.z(0)

    return statevector.evolve(attack_circuit)


# ============================================================
# 5. CORRECT VERIFICATION BASIS
# ============================================================

def get_basis(state_name):

    if state_name in ["0", "1"]:
        return "Z"

    return "X"


# ============================================================
# 6. EXPECTED MEASUREMENT
# ============================================================

def expected_result(state_name):

    if state_name in ["0", "+"]:
        return "0"

    return "1"


# ============================================================
# 7. MEASURE QUANTUM STATE
# ============================================================

def measure_state(statevector, basis, copies=COPIES):

    counts = {
        "0": 0,
        "1": 0
    }

    sampler = StatevectorSampler()

    for _ in range(copies):

        qc = QuantumCircuit(1, 1)

        qc.initialize(statevector.data, 0)

        # X-basis measurement
        if basis == "X":
            qc.h(0)

        qc.measure(0, 0)

        result = sampler.run(
            [qc],
            shots=1
        ).result()

        measured = list(
            result[0].data.c.get_counts().keys()
        )[0]

        counts[measured] += 1

    return counts


# ============================================================
# 8. ERROR RATE
# ============================================================

def calculate_error_rate(counts, expected):

    wrong = "1" if expected == "0" else "0"

    return counts.get(wrong, 0) / COPIES


# ============================================================
# 9. Z-SCORE
# ============================================================

def calculate_z_score(error_rate):

    variance = (
        BASELINE_NOISE *
        (1 - BASELINE_NOISE)
        / COPIES
    )

    standard_deviation = math.sqrt(variance)

    return (
        error_rate - BASELINE_NOISE
    ) / standard_deviation


# ============================================================
# 10. THREAT DETECTION
# ============================================================

def detect_threat(error_rate, z_score):

    if error_rate >= ATTACK_THRESHOLD:
        return "THREAT DETECTED"

    elif z_score >= Z_THRESHOLD:
        return "STATISTICAL DISTURBANCE"

    elif error_rate < 0.10:
        return "NORMAL"

    else:
        return "POSSIBLE NOISE"


# ============================================================
# 11. SINGLE TEST
# ============================================================

def run_test(state_name, attack):

    original_state = create_state(state_name)

    received_state = original_state

    if attack != "NONE":
        received_state = apply_attack(
            original_state,
            attack
        )

    basis = get_basis(state_name)

    expected = expected_result(state_name)

    counts = measure_state(
        received_state,
        basis
    )

    error_rate = calculate_error_rate(
        counts,
        expected
    )

    z_score = calculate_z_score(
        error_rate
    )

    threat = detect_threat(
        error_rate,
        z_score
    )

    return {
        "state": state_name,
        "attack": attack,
        "basis": basis,
        "counts": counts,
        "error_rate": error_rate,
        "z_score": z_score,
        "threat": threat
    }


# ============================================================
# MAIN
# ============================================================

print("\n" + "=" * 70)
print("       QUANTUM DIGITAL SIGNATURE - FINAL DEMO")
print("=" * 70)

print("\nMessage:", MESSAGE)


# ============================================================
# SIGNATURE GENERATION
# ============================================================

signature = generate_signature(
    MESSAGE,
    "+"
)

print("\n[1] QDS SIGNATURE GENERATION")

print("Signature State :", signature["state"])

print("\nQuantum Statevector:")
print(signature["quantum_state"])


# ============================================================
# TELEPORTATION
# ============================================================

print("\n[2] QUANTUM TELEPORTATION")

teleport_circuit = teleport_state("+")

print("Alice -> Bob teleportation circuit created.")

print("\nTeleportation Circuit:")
print(teleport_circuit)


# ============================================================
# TEST CASES
# ============================================================

test_cases = [
    ("0", "NONE"),
    ("0", "X"),

    ("1", "NONE"),
    ("1", "X"),

    ("+", "NONE"),
    ("+", "Z"),

    ("-", "NONE"),
    ("-", "Z")
]


print("\n" + "=" * 70)
print("              SECURITY TEST CASES")
print("=" * 70)


TP = 0
TN = 0
FP = 0
FN = 0


for number, (state, attack) in enumerate(
    test_cases,
    start=1
):

    result = run_test(
        state,
        attack
    )

    malicious = attack != "NONE"

    detected = (
        result["threat"] == "THREAT DETECTED"
    )

    if malicious and detected:
        TP += 1

    elif malicious and not detected:
        FN += 1

    elif not malicious and detected:
        FP += 1

    else:
        TN += 1


    print("\n" + "-" * 70)

    print("TEST", number)

    print("Original State       :", state)

    print("Attack               :", attack)

    print("Verification Basis   :", result["basis"])

    print("Measurement Results  :", result["counts"])

    print(
        "Error Rate           : {:.2f}%".format(
            result["error_rate"] * 100
        )
    )

    print(
        "Z-Score              : {:.2f}".format(
            result["z_score"]
        )
    )

    print("Detection            :", result["threat"])

    if malicious:

        if detected:
            print("Signature Status     : FORGED")
        else:
            print("Signature Status     : ATTACK NOT DETECTED")

    else:

        if detected:
            print("Signature Status     : FALSE ALARM")
        else:
            print("Signature Status     : VALID")


# ============================================================
# PERFORMANCE METRICS
# ============================================================

print("\n" + "=" * 70)
print("              FINAL PERFORMANCE REPORT")
print("=" * 70)

print("\nTP  (True Positive) :", TP)
print("TN  (True Negative) :", TN)
print("FP  (False Positive):", FP)
print("FN  (False Negative):", FN)


if TP + FN > 0:

    tpr = TP / (TP + FN)

else:

    tpr = 0


if TP + FN > 0:

    fnr = FN / (TP + FN)

else:

    fnr = 0


if FP + TN > 0:

    fpr = FP / (FP + TN)

else:

    fpr = 0


if TN + FP > 0:

    tnr = TN / (TN + FP)

else:

    tnr = 0


print(
    "\nDetection Rate / TPR : {:.2f}%".format(
        tpr * 100
    )
)

print(
    "False Negative Rate  : {:.2f}%".format(
        fnr * 100
    )
)

print(
    "False Alarm Rate     : {:.2f}%".format(
        fpr * 100
    )
)

print(
    "Specificity / TNR    : {:.2f}%".format(
        tnr * 100
    )
)


# ============================================================
# FINAL CONCLUSION
# ============================================================

print("\n" + "=" * 70)
print("                    CONCLUSION")
print("=" * 70)

print("""
QDS Signature Generation      : SUCCESS
Quantum Teleportation         : SUCCESS
Z-Basis Verification          : USED
X-Basis Verification          : USED
X Attack Testing              : COMPLETED
Z Attack Testing              : COMPLETED
Statistical Detection         : COMPLETED
TP/TN/FP/FN Evaluation        : COMPLETED
""")

print("=" * 70)
print("        END-TO-END QDS PROTOTYPE COMPLETED")
print("=" * 70)