"""
Automated Validation Script for Task #1 — Forgery Probability Analysis Module
"""
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from qds_attack_simulator import QDSAttackSimulator

def test_task1():
    simulator = QDSAttackSimulator()
    print("==================================================")
    print("RUNNING VALIDATION FOR TASK #1: FORGERY PROBABILITY ANALYSIS")
    print("==================================================")

    # Test state forgery calculation
    res_forgery = simulator.calculate_forgery_probability(
        attack_type="FORGERY",
        original_state="0",
        received_state="1",
        recv_counts={0: 0, 1: 1000},
        total_shots=1000
    )
    assert res_forgery["attack"] == "FORGERY"
    assert res_forgery["status"] == "SUSPECTED FORGERY"
    assert res_forgery["mismatch_rate"] == 1.0

    # Test genuine state calculation
    res_none = simulator.calculate_forgery_probability(
        attack_type="NONE",
        original_state="0",
        received_state="0",
        recv_counts={0: 1000, 1: 0},
        total_shots=1000
    )
    assert res_none["attack"] == "NONE"
    assert res_none["status"] == "VALID SIGNATURE"
    assert res_none["mismatch_rate"] == 0.0

    print("TASK 01 : PASS")

if __name__ == "__main__":
    test_task1()
    sys.exit(0)
