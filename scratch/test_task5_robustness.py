import sys
import os
sys.path.insert(0, os.path.abspath('.'))

from qds_attack_simulator import QDSAttackSimulator

def main():
    sim = QDSAttackSimulator()
    print("==================================================")
    print("TASK #5 & TASK #4 FIX VALIDATION")
    print("==================================================")

    # 1. Verify Task #4 TPR fix for NONE
    perf_data = sim.evaluate_attack_performance(1000)
    for aw in perf_data["attack_wise"]:
        if aw["attack"] == "NONE":
            print(f"\n[Task #4 Fix Verification] NONE TPR Display String: '{aw['tpr_str']}'")
            assert "N/A" in aw["tpr_str"], f"Expected 'N/A' in tpr_str for NONE, got '{aw['tpr_str']}'"

    # 2. Verify Task #5 Noise vs Attack Differentiation Matrix
    print("\n--- TASK #5 NOISE VS ATTACK MATRIX (Shots=1000, Threshold=5%) ---")
    noise_res = sim.evaluate_noise_vs_attack_matrix(
        noise_levels=[0.0, 0.01, 0.02, 0.05, 0.10],
        shots=1000,
        threshold=0.05
    )

    matrix = noise_res["matrix"]
    summary = noise_res["summary"]

    print(f"{'Condition':<25} | {'Noise':<6} | {'Obs Error':<10} | {'Threshold':<9} | {'Verdict':<20} | {'Classification Result'}")
    print("-" * 110)
    for r in matrix:
        print(f"{r['condition']:<25} | {r['noise_pct_str']:<6} | {r['observed_error_pct_str']:<10} | {r['threshold_pct_str']:<9} | {r['verdict']:<20} | {r['classification_result']}")

    print("\n--- SUMMARY METRICS ---")
    print(f"Total Tests Evaluated       : {summary['total_tests']}")
    print(f"Correct Classifications     : {summary['correct_classifications']}")
    print(f"False Alarms (Noise>Thresh) : {summary['false_alarms']}")
    print(f"Missed Threats              : {summary['missed_threats']}")
    print(f"Robustness Benchmark Rate   : {summary['robustness_rate']:.2f}%")

    print("\n[OK] Task #5 & Task #4 Fix Validation Completed Successfully!")

if __name__ == "__main__":
    main()
