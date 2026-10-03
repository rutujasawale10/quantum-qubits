"""
Automated Validation Script for Task #2 — Statistical Threshold Engine Module
"""
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from qds_attack_simulator import QDSAttackSimulator

def test_task2():
    simulator = QDSAttackSimulator()
    print("==================================================")
    print("RUNNING VALIDATION FOR TASK #2: STATISTICAL THRESHOLD ENGINE")
    print("==================================================")

    # Test THREAT condition (error_rate > threshold)
    th_threat = simulator.evaluate_statistical_threshold(
        attack_type="FORGERY",
        error_rate=0.5,
        forgery_prob_data={"error_pct_str": "50.00%"},
        chi_square_val=500.0,
        error_threshold_pct=10.0,
        chi_threshold=10.0
    )
    assert th_threat["is_threat"] is True
    assert th_threat["verdict"] == "THREAT"

    # Test NORMAL condition (error_rate <= threshold)
    th_normal = simulator.evaluate_statistical_threshold(
        attack_type="NONE",
        error_rate=0.01,
        forgery_prob_data={"error_pct_str": "1.00%"},
        chi_square_val=1.2,
        error_threshold_pct=10.0,
        chi_threshold=10.0
    )
    assert th_normal["is_threat"] is False
    assert th_normal["verdict"] == "NORMAL"

    print("TASK 02 : PASS")

if __name__ == "__main__":
    test_task2()
    sys.exit(0)
