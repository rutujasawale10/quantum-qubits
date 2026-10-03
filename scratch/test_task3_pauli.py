"""
Automated Validation Script for Task #3 — Pauli Eigenstate & Projective Measurement Module
"""
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from qds_attack_simulator import QDSAttackSimulator

def test_task3():
    simulator = QDSAttackSimulator()
    print("==================================================")
    print("RUNNING VALIDATION FOR TASK #3: PAULI EIGENSTATE & PROJECTIVE MEASUREMENT")
    print("==================================================")

    res_z = simulator.projective_measurement("0", "Z", shots=1000)
    assert res_z["state_name"] == "0"
    assert res_z["basis"] == "Z"
    assert res_z["is_natural"] is True

    res_x = simulator.projective_measurement("+", "X", shots=1000)
    assert res_x["state_name"] == "+"
    assert res_x["basis"] == "X"
    assert res_x["is_natural"] is True

    res_cross = simulator.projective_measurement("0", "X", shots=1000)
    assert res_cross["is_natural"] is False

    print("TASK 03 : PASS")

if __name__ == "__main__":
    test_task3()
    sys.exit(0)
