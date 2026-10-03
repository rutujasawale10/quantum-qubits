import sys
import os
sys.path.insert(0, os.path.abspath('.'))

from qds_attack_simulator import QDSAttackSimulator

def main():
    sim = QDSAttackSimulator()
    print("==================================================")
    print("TASK #7 VALIDATION: COMPLETE VERIFICATION PIPELINE PERFORMANCE")
    print("==================================================")

    # 1. Test with shots = 100
    print("\n[TEST 1] Running 100 attempts per case with shots=100...")
    res100 = sim.run_performance_evaluation(attempts=100, shots=100)
    
    # 2. Test with shots = 1000
    print("\n[TEST 2] Running 100 attempts per case with shots=1000...")
    res1000 = sim.run_performance_evaluation(attempts=100, shots=1000)

    cases = res1000["cases"]
    summary = res1000["summary"]
    fp_summary = res1000["full_pipeline_summary"]
    ag_summary = res1000["auth_gateway_summary"]

    print("\n--- CONTROLLED BENCHMARK PERFORMANCE MATRIX (shots=1000) ---")
    print(f"{'Test Case':<23} | {'Path':<22} | {'Attempts':<8} | {'Avg Time (ms)':<14} | {'Min (ms)':<10} | {'Max (ms)':<10} | {'Result':<8}")
    print("-" * 110)

    for c in cases:
        print(f"{c['case_name']:<23} | {c['path']:<22} | {c['attempts']:<8} | {c['avg_time_ms_str']:<14} | {c['min_time_ms_str']:<10} | {c['max_time_ms_str']:<10} | {c['result']:<8}")
        
        # Timing integrity checks
        assert c['attempts'] == 100
        assert c['avg_time_ms'] > 0.0
        assert c['min_time_ms'] > 0.0
        assert c['max_time_ms'] > 0.0
        assert c['min_time_ms'] <= c['avg_time_ms'] <= c['max_time_ms'] + 1e-5
        assert c['shots'] == 1000

    # Verdict assertions
    assert cases[0]['result'] == "VALID", f"Case 1 expected VALID, got {cases[0]['result']}"
    assert cases[1]['result'] == "THREAT", f"Case 2 expected THREAT, got {cases[1]['result']}"
    assert cases[2]['result'] == "THREAT", f"Case 3 expected THREAT, got {cases[2]['result']}"
    assert cases[3]['result'] == "BLOCKED", f"Case 4 expected BLOCKED, got {cases[3]['result']}"
    assert cases[3]['path'] == "Authorization Gateway"

    print("\n--- PERFORMANCE AGGREGATES ---")
    print(f"Full Pipeline Attempts         : {fp_summary['attempts']}")
    print(f"Full Pipeline Average Time     : {fp_summary['avg_time_ms_str']}")
    print(f"Full Pipeline Min / Max Time   : {fp_summary['min_time_ms_str']} / {fp_summary['max_time_ms_str']}")
    print(f"Authorization Gateway Attempts : {ag_summary['attempts']}")
    print(f"Authorization Gateway Avg Time : {ag_summary['avg_time_ms_str']}")
    print(f"Authorization Gateway Min/Max  : {ag_summary['min_time_ms_str']} / {ag_summary['max_time_ms_str']}")
    print(f"Total Benchmark Evaluation     : {summary['total_attempts']} attempts in {summary['total_time_sec_str']}")

    assert fp_summary['attempts'] == 300
    assert ag_summary['attempts'] == 100
    assert fp_summary['avg_time_ms'] > ag_summary['avg_time_ms'], "Full pipeline should include quantum simulation overhead vs fast auth check"

    # Tasks #1-#6 regression check
    print("\n--- REGRESSION CHECK: TASKS #1 - #6 ---")
    forg_res = sim.simulate_forgery_attack("0")
    assert forg_res["detected"] is True, "Task #1 Forgery failed"

    auth_res = sim.evaluate_unauthorized_verification("Alice", "Bob", "Eve")
    assert auth_res["verification_allowed"] is False, "Task #6 Auth check failed"

    print("\n[OK] Task #7 Performance Benchmark Validation PASSED!")

if __name__ == "__main__":
    main()

