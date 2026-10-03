import sys
import os
sys.path.insert(0, os.path.abspath('.'))

from qds_attack_simulator import QDSAttackSimulator

def main():
    sim = QDSAttackSimulator()
    print("==================================================")
    print("TASK #8 VALIDATION: CONSOLIDATED SECURITY ANALYSIS & SUMMARY")
    print("==================================================")

    sec_res = sim.run_security_analysis(shots=1000)

    # 1. Structure Verification
    assert "attack_summary" in sec_res, "Missing attack_summary"
    assert "metrics_summary" in sec_res, "Missing metrics_summary"
    assert "security_flow" in sec_res, "Missing security_flow"
    assert sec_res["scope"] == "Controlled Prototype Evaluation"

    attack_list = sec_res["attack_summary"]
    metrics = sec_res["metrics_summary"]
    flow = sec_res["security_flow"]

    # 2. Attack Summary Verification (5 Attacks)
    print("\n--- CONSOLIDATED ATTACK-WISE SECURITY MATRIX ---")
    print(f"{'Attack Vector':<25} | {'Detection Mechanism':<42} | {'Decision':<10} | {'Controlled Result':<25}")
    print("-" * 110)

    for item in attack_list:
        print(f"{item['attack']:<25} | {item['mechanism']:<42} | {item['decision']:<10} | {item['controlled_result']:<25}")

    assert len(attack_list) == 5, f"Expected 5 attack vectors, got {len(attack_list)}"
    
    attacks_found = [a["attack"] for a in attack_list]
    expected_attacks = ["Forgery Attack", "Impersonation Attack", "Replay Attack", "Channel Manipulation", "Unauthorized Verification"]
    for ea in expected_attacks:
        assert ea in attacks_found, f"Missing attack: {ea}"

    # Verify mechanisms & decisions
    for item in attack_list:
        if item["attack"] == "Forgery Attack":
            assert "Quantum-state" in item["mechanism"]
            assert item["decision"] == "THREAT"
        elif item["attack"] == "Impersonation Attack":
            assert "identity" in item["mechanism"].lower()
            assert item["decision"] == "THREAT"
        elif item["attack"] == "Replay Attack":
            assert "hash" in item["mechanism"].lower()
            assert item["decision"] == "THREAT"
        elif item["attack"] == "Channel Manipulation":
            assert "deviation" in item["mechanism"].lower() or "quantum" in item["mechanism"].lower()
            assert item["decision"] == "THREAT"
        elif item["attack"] == "Unauthorized Verification":
            assert "gateway" in item["mechanism"].lower()
            assert item["decision"] == "BLOCKED"

    # 3. Metrics Summary Verification
    print("\n--- CONSOLIDATED EMPIRICAL METRICS ---")
    print(f"Overall TPR / Detection Rate   : {metrics['TPR']:.2f}%")
    print(f"Overall TNR / Specificity      : {metrics['TNR']:.2f}%")
    print(f"False Positive Rate / FPR      : {metrics['FPR']:.2f}%")
    print(f"False Negative Rate / FNR      : {metrics['FNR']:.2f}%")
    print(f"Authorization Detection Rate   : {metrics['authorization_detection_rate_str']}")
    print(f"False Authorization Rate       : {metrics['false_authorization_rate_str']}")
    print(f"Full Pipeline Average Speed    : {metrics['full_pipeline_avg_ms_str']}")
    print(f"Authorization Gateway Speed    : {metrics['auth_gateway_avg_ms_str']}")

    assert metrics["TPR"] >= 0.0
    assert metrics["TNR"] >= 0.0
    assert metrics["authorization_detection_rate"] >= 0.0
    assert metrics["full_pipeline_avg_ms"] > 0.0

    # 4. Security Decision Flow Verification
    print("\n--- SECURITY DECISION ARCHITECTURE FLOW ---")
    for f_step in flow:
        print(f"  [{f_step['step']}] -> {f_step['detail']}")
    assert len(flow) == 6

    # 5. Regression Check Tasks #1-#7
    print("\n--- REGRESSION CHECK: TASKS #1 - #7 ---")
    perf_res = sim.run_performance_evaluation(attempts=10, shots=100)
    assert len(perf_res["cases"]) == 4, "Task #7 Performance module failed"

    auth_res = sim.evaluate_unauthorized_verification("Alice", "Bob", "Eve")
    assert auth_res["verification_allowed"] is False, "Task #6 Auth check failed"

    forg_res = sim.simulate_forgery_attack("0")
    assert forg_res["detected"] is True, "Task #1 Forgery check failed"

    print("\n[OK] Task #8 Consolidated Security Analysis Validation PASSED!")

if __name__ == "__main__":
    main()


