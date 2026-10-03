import sys
import os
sys.path.insert(0, os.path.abspath('.'))

from qds_attack_simulator import QDSAttackSimulator

def main():
    sim = QDSAttackSimulator()
    print("==================================================")
    print("TASK #9 VALIDATION: MATHEMATICAL VERIFICATION MODEL")
    print("==================================================")

    # 1. Test Mathematical Security Model for FORGERY attack on |0>
    print("\n[TEST 1] Evaluating Mathematical Model for FORGERY attack on |0>...")
    m_forgery = sim.get_mathematical_security_model(
        state_name="0",
        basis="Z",
        attack_type="FORGERY",
        shots=1000,
        error_threshold_pct=10.0,
        chi_threshold=10.0
    )

    formulas = m_forgery["formulas"]
    params = m_forgery["parameters"]

    print("\nFormulas:")
    for k, v in formulas.items():
        print(f"  {k:<28}: {v}")

    print("\nEvaluated Parameters:")
    print(f"  State & Basis               : {params['state'].replace('⟩', '>')} in {params['basis']}-Basis")
    print(f"  Attack Type                 : {params['attack_type']}")
    print(f"  Total Shots (N)             : {params['total_shots_N']}")
    print(f"  Mismatches (M)              : {params['mismatches_M']}")
    print(f"  Error Rate (E)              : {params['error_rate_E']:.4f} ({params['error_pct_str']})")
    print(f"  Forgery Prob Estimate (P_f) : {params['forgery_prob_str']} ({params['forgery_prob_label']})")
    print(f"  Chi-Square (X2)             : {params['chi_square_str']}")
    print(f"  Verdict Decision            : {params['verdict']}")

    # Formula & calculation assertions
    assert params["total_shots_N"] == 1000
    assert params["mismatches_M"] == 1000, "For state |0> under FORGERY flip to |1>, all 1000 shots in Z-basis must be mismatched (|1> outcome)"
    assert params["error_rate_E"] == 1.0
    assert params["error_pct_E"] == 100.0
    assert params["forgery_prob_val"] == 100.0
    assert params["forgery_prob_label"] == "Simulation-Based Forgery Probability Estimate"
    assert params["verdict"] == "THREAT"
    assert params["error_threat"] is True

    # 2. Test Mathematical Security Model for Genuine (NONE) Transmission on |0>
    print("\n[TEST 2] Evaluating Mathematical Model for Legitimate Communication (NONE) on |0>...")
    m_none = sim.get_mathematical_security_model(
        state_name="0",
        basis="Z",
        attack_type="NONE",
        shots=1000,
        error_threshold_pct=10.0,
        chi_threshold=10.0
    )
    params_none = m_none["parameters"]
    print(f"  Legitimate State |0>: Mismatches={params_none['mismatches_M']}, Error%={params_none['error_pct_str']}, Chi-Square={params_none['chi_square_str']}, Verdict={params_none['verdict']}")
    assert params_none["mismatches_M"] == 0
    assert params_none["error_pct_E"] == 0.0
    assert params_none["verdict"] == "VALID"

    # 3. Tasks #1-#8 Regression Suite
    print("\n--- REGRESSION CHECK: TASKS #1 - #8 ---")
    sec_analysis = sim.run_security_analysis(shots=100)
    assert len(sec_analysis["attack_summary"]) == 5, "Task #8 Security Analysis failed"

    perf_res = sim.run_performance_evaluation(attempts=10, shots=100)
    assert len(perf_res["cases"]) == 4, "Task #7 Performance evaluation failed"

    auth_res = sim.evaluate_unauthorized_verification("Alice", "Bob", "Eve")
    assert auth_res["verification_allowed"] is False, "Task #6 Auth check failed"

    print("\n[OK] Task #9 Mathematical Verification Model PASSED!")

if __name__ == "__main__":
    main()



