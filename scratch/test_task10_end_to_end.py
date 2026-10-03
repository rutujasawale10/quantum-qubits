import sys
import os
sys.path.insert(0, os.path.abspath('.'))

from qds_attack_simulator import QDSAttackSimulator

def main():
    sim = QDSAttackSimulator()
    print("==================================================")
    print("TASK #10 VALIDATION: END-TO-END SECURITY VALIDATION & BENCHMARK")
    print("==================================================")

    print("\nExecuting End-to-End Validation across 6 Controlled Scenarios...")
    e2e_res = sim.run_end_to_end_validation(shots=1000)

    matrix = e2e_res["matrix"]
    metrics = e2e_res["metrics"]
    perf = e2e_res["performance_reference"]
    sec = e2e_res["security_metrics_reference"]

    print("\n--- 6-SCENARIO CONTROLLED VALIDATION MATRIX ---")
    print(f"{'Scenario Name':<28} | {'Path':<22} | {'Expected':<10} | {'Actual':<10} | {'Status':<6}")
    print("-" * 88)

    for row in matrix:
        print(f"{row['scenario_name']:<28} | {row['path']:<22} | {row['expected_decision']:<10} | {row['actual_decision']:<10} | {row['status']:<6}")
        # Assertions
        assert row["status"] == "PASS", f"Scenario {row['scenario_id']} failed! Expected {row['expected_decision']}, got {row['actual_decision']}"

    assert len(matrix) == 6, f"Expected 6 scenarios, got {len(matrix)}"

    # Specific Scenario Verdict Checks
    assert matrix[0]["actual_decision"] == "VALID", "Scenario 1 (NONE) expected VALID"
    assert matrix[1]["actual_decision"] == "THREAT", "Scenario 2 (FORGERY) expected THREAT"
    assert matrix[2]["actual_decision"] == "THREAT", "Scenario 3 (IMPERSONATION) expected THREAT"
    assert matrix[3]["actual_decision"] == "THREAT", "Scenario 4 (REPLAY) expected THREAT"
    assert matrix[4]["actual_decision"] == "THREAT", "Scenario 5 (CHANNEL) expected THREAT"
    assert matrix[5]["actual_decision"] == "BLOCKED", "Scenario 6 (UNAUTHORIZED) expected BLOCKED"

    print("\n--- VALIDATION METRICS ---")
    print(f"Total Benchmark Scenarios      : {metrics['total_scenarios']}")
    print(f"Passed Scenarios               : {metrics['passed_scenarios']}")
    print(f"Failed Scenarios               : {metrics['failed_scenarios']}")
    print(f"End-to-End Validation Rate     : {metrics['validation_rate_str']} ({metrics['validation_label']})")

    assert metrics["passed_scenarios"] == 6
    assert metrics["failed_scenarios"] == 0
    assert metrics["validation_rate"] == 100.0

    print("\n--- SYSTEM PERFORMANCE & SECURITY REFERENCES ---")
    print(f"Full Pipeline Average Speed    : {perf['full_pipeline_avg_ms_str']} ({perf['runtime_label']})")
    print(f"Authorization Gateway Speed    : {perf['auth_gateway_avg_ms_str']}")
    print(f"Overall Detection Rate (TPR)   : {sec['TPR']:.2f}%")
    print(f"Authorization Detection Rate   : {sec['authorization_detection_rate_str']}")

    assert perf["full_pipeline_avg_ms"] > 0.0
    assert sec["TPR"] >= 0.0

    # 3. Tasks #1-#9 Regression Suite
    print("\n--- REGRESSION CHECK: TASKS #1 - #9 ---")
    math_model = sim.get_mathematical_security_model(state_name="0", basis="Z", attack_type="FORGERY")
    assert math_model["parameters"]["verdict"] == "THREAT", "Task #9 Math model failed"

    sec_analysis = sim.run_security_analysis(shots=100)
    assert len(sec_analysis["attack_summary"]) == 5, "Task #8 Security analysis failed"

    perf_res = sim.run_performance_evaluation(attempts=10, shots=100)
    assert len(perf_res["cases"]) == 4, "Task #7 Performance evaluation failed"

    auth_res = sim.evaluate_unauthorized_verification("Alice", "Bob", "Eve")
    assert auth_res["verification_allowed"] is False, "Task #6 Auth check failed"

    print("\n[OK] Task #10 End-to-End Security Validation PASSED!")

if __name__ == "__main__":
    main()




