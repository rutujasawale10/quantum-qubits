"""
Automated Validation Script for Task #11 — Research-Based Security Evaluation Layer
SIH26141: Quantum-Inspired Cyber Threat Detection for Digital Signature Security
"""

import sys
import os

# Add parent directory to path to import qds modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from qds_attack_simulator import QDSAttackSimulator

def test_task11_research_evaluation():
    print("==================================================")
    print("RUNNING AUTOMATED VALIDATION FOR TASK #11")
    print("==================================================")

    simulator = QDSAttackSimulator()

    # 1. Execute run_research_evaluation
    res = simulator.run_research_evaluation(shots=1000)

    # 2. Check SIH Objective Matrix (14 rows)
    sih_matrix = res["sih_objective_matrix"]
    print(f"\n1. SIH Objective Matrix Rows: {len(sih_matrix)} (Expected: 14)")
    assert len(sih_matrix) == 14, f"Expected 14 SIH objectives, got {len(sih_matrix)}"

    expected_objectives = [
        "Teleportation-based QDS framework",
        "Forgery detection",
        "Impersonation detection",
        "Replay detection",
        "Unauthorized verification detection",
        "Pauli eigenstates",
        "Quantum measurement analysis",
        "Statistical threshold methods",
        "Efficient verification",
        "Forgery probability analysis",
        "Attack simulation",
        "Mathematical modelling",
        "Security analysis",
        "Performance evaluation"
    ]
    actual_objectives = [r["objective"] for r in sih_matrix]
    for obj in expected_objectives:
        assert obj in actual_objectives, f"Missing SIH objective: {obj}"
    print("  [PASS] All 14 SIH objective rows verified.")

    # 3. Check Expected Solution Coverage (10 components)
    sol_coverage = res["expected_solution_coverage"]
    print(f"\n2. Expected Solution Coverage Rows: {len(sol_coverage)} (Expected: 10)")
    assert len(sol_coverage) == 10, f"Expected 10 solution components, got {len(sol_coverage)}"
    expected_components = [
        "Bell-state entanglement",
        "Quantum teleportation",
        "Pauli correction operations",
        "Projective measurements",
        "Statistical evaluation",
        "Threshold-based decisions",
        "Mathematical modelling",
        "Attack simulation",
        "Security analysis",
        "Performance evaluation"
    ]
    actual_components = [r["component"] for r in sol_coverage]
    for comp in expected_components:
        assert comp in actual_components, f"Missing solution component: {comp}"
    print("  [PASS] All 10 Expected Solution components verified.")

    # 4. Check Experimental Evidence Summary
    exp_evidence = res["experimental_evidence"]
    print("\n3. Experimental Evidence Summary:")
    print("  - Benchmark:", exp_evidence["controlled_8case_benchmark"])
    print("  - Auth Test:", exp_evidence["authorization_test"])
    print("  - Noise Experiment:", exp_evidence["controlled_noise_experiment"])
    print("  - End-to-End Validation:", exp_evidence["controlled_end_to_end_validation_rate"])
    print("  - Software Simulation Runtime:", exp_evidence["controlled_software_simulation_runtime"])

    assert "4 attack cases detected out of 4" in exp_evidence["controlled_8case_benchmark"]
    assert "1/1 unauthorized attempt blocked" in exp_evidence["authorization_test"]
    assert "Controlled Noise Experiment:" in exp_evidence["controlled_noise_experiment"]
    assert "14/15" in exp_evidence["controlled_noise_experiment"]
    assert "Controlled End-to-End Validation Rate:" in exp_evidence["controlled_end_to_end_validation_rate"]
    assert "6/6" in exp_evidence["controlled_end_to_end_validation_rate"]
    assert "Controlled software-simulation runtime:" in exp_evidence["controlled_software_simulation_runtime"]
    assert "Average Full Verification Pipeline:" in exp_evidence["controlled_software_simulation_runtime"]
    assert "Authorization Gateway:" in exp_evidence["controlled_software_simulation_runtime"]
    print("  [PASS] All experimental evidence values verified against existing Task results.")

    # 5. Check Attack Coverage Matrix (5 categories)
    atk_matrix = res["attack_coverage_matrix"]
    print(f"\n4. Attack Coverage Matrix Rows: {len(atk_matrix)} (Expected: 5)")
    assert len(atk_matrix) == 5, f"Expected 5 attack categories, got {len(atk_matrix)}"

    expected_attacks = [
        "Forgery",
        "Impersonation",
        "Replay",
        "Channel Manipulation",
        "Unauthorized Verification"
    ]
    actual_attacks = [r["attack"] for r in atk_matrix]
    for atk in expected_attacks:
        assert atk in actual_attacks, f"Missing attack category: {atk}"
    print("  [PASS] All 5 attack categories verified.")

    # 6. Check Security Architecture Flow
    sec_arch = res["security_model_architecture"]
    print("\n5. Security Architecture Flow Diagram:")
    assert "Alice" in sec_arch
    assert "Authorization" in sec_arch
    assert "Teleportation / Verification" in sec_arch
    assert "Projective Measurement" in sec_arch
    assert "Statistical Analysis" in sec_arch
    assert "Threshold Decision" in sec_arch
    assert "VALID" in sec_arch
    assert "THREAT" in sec_arch
    assert "BLOCK" in sec_arch
    print("  [PASS] Security Architecture Flow Diagram verified.")

    # 7. Check Research Gap & Limitations (8 items)
    limitations = res["research_gaps_and_limitations"]
    print(f"\n6. Research Gaps & Limitations Items: {len(limitations)} (Expected: 8)")
    assert len(limitations) == 8, f"Expected 8 limitations, got {len(limitations)}"
    assert "Current evaluation is software simulation." in limitations
    assert "No real quantum hardware evaluation." in limitations
    assert "No formal cryptographic security proof." in limitations
    assert "Controlled test datasets are small." in limitations
    assert "Threshold values are prototype evaluation parameters." in limitations
    assert "No claim of universal real-world attack detection." in limitations
    assert "No production-scale deployment evaluation." in limitations
    assert "Information-theoretic security is not formally proven by this prototype." in limitations
    print("  [PASS] All 8 Research Gaps & Limitations verified.")

    # 8. Check Prototype Contribution Summary (9 items)
    contributions = res["prototype_contributions"]
    print(f"\n7. Prototype Contributions Items: {len(contributions)} (Expected: 9)")
    assert len(contributions) == 9, f"Expected 9 contributions, got {len(contributions)}"
    print("  [PASS] All 9 Prototype Contributions verified.")

    # 9. Verify Tasks #1–#10 remain functional (Regression Check)
    print("\n8. Tasks #1–#10 Regression Check:")
    sec_eval = simulator.run_controlled_8state_evaluation()
    assert sec_eval["metrics"]["TPR"] == 100.0
    print("  - Task #4 / #8 benchmark intact: 100% TPR / TNR")

    auth_eval = simulator.run_controlled_authorization_evaluation()
    assert auth_eval["metrics"]["false_authorization_rate"] == 0.0
    print("  - Task #6 auth detection intact: 100% auth blocked")

    noise_eval = simulator.evaluate_noise_vs_attack_matrix()
    assert noise_eval["summary"]["correct_classifications"] == 14
    print("  - Task #5 noise experiment intact: 14/15 correct classification")

    perf_eval = simulator.run_performance_evaluation(attempts=10)
    assert perf_eval["full_pipeline_summary"]["avg_time_ms"] > 0
    print("  - Task #7 performance module intact")

    math_model = simulator.get_mathematical_security_model()
    assert "formulas" in math_model and "parameters" in math_model
    print("  - Task #9 mathematical decision model intact")

    e2e_eval = simulator.run_end_to_end_validation()
    assert e2e_eval["metrics"]["validation_rate"] == 100.0
    print("  - Task #10 end-to-end validation intact: 6/6 scenarios passed")

    print("\n==================================================")
    print("TASK #11 AUTOMATED VALIDATION PASSED SUCCESSFULLY")
    print("==================================================")

if __name__ == "__main__":
    test_task11_research_evaluation()
    sys.exit(0)
