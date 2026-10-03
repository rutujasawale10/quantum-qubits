import sys
import os
sys.path.insert(0, os.path.abspath('.'))

# Import QDS Attack Simulator
from qds_attack_simulator import QDSAttackSimulator

def main():
    sim = QDSAttackSimulator()
    print("==================================================")
    print("TASK #4 VALIDATION: VERIFICATION ACCURACY & ATTACK PERFORMANCE")
    print("==================================================")

    shots = 1000

    # 1. Attack-Wise Performance Evaluation
    perf_data = sim.evaluate_attack_performance(shots=shots)
    overall = perf_data["overall"]
    attack_wise = perf_data["attack_wise"]

    print("\n--- OVERALL CONFUSION MATRIX & METRICS ---")
    print(f"TP (True Positives)  : {overall['TP']}")
    print(f"TN (True Negatives)  : {overall['TN']}")
    print(f"FP (False Positives) : {overall['FP']}")
    print(f"FN (False Negatives) : {overall['FN']}")
    print(f"Detection Rate / TPR : {overall['TPR_str']}")
    print(f"False Negative Rate  : {overall['FNR_str']}")
    print(f"False Positive Rate  : {overall['FPR_str']}")
    print(f"Specificity / TNR    : {overall['TNR_str']}")

    print("\n--- ATTACK-WISE BREAKDOWN ---")
    print(f"{'Attack':<15} | {'Cases':<6} | {'Det':<5} | {'Miss':<5} | {'FA':<5} | {'TPR':<8} | {'FNR':<8} | {'FPR':<8} | {'TNR':<8}")
    print("-" * 80)
    for aw in attack_wise:
        print(f"{aw['attack']:<15} | {aw['total_cases']:<6} | {aw['detected_threats']:<5} | {aw['missed_threats']:<5} | {aw['false_alarms']:<5} | {aw['tpr_str']:<8} | {aw['fnr_str']:<8} | {aw['fpr_str']:<8} | {aw['tnr_str']:<8}")

    # 2. Controlled 8-State Prototype Evaluation
    print("\n--- CONTROLLED 8-STATE BENCHMARK ---")
    ctrl_data = sim.run_controlled_8state_evaluation(shots=shots)
    ctrl_results = ctrl_data["results"]
    ctrl_metrics = ctrl_data["metrics"]

    print(f"{'Test Case':<15} | {'Transmitted':<11} | {'Received':<11} | {'Basis':<8} | {'Attack':<10} | {'Exp Threat':<10} | {'Detected':<8} | {'Verdict'}")
    print("-" * 110)
    for cr in ctrl_results:
        st_clean = cr['state'].replace('⟩', '>').replace('|', '|')
        rec_clean = cr['received'].replace('⟩', '>').replace('|', '|')
        lbl_clean = cr['label'].replace('⟩', '>').replace('|\n', '')
        print(f"{lbl_clean:<15} | {st_clean:<11} | {rec_clean:<11} | {cr['basis']:<8} | {cr['attack']:<10} | {cr['expected_threat']:<10} | {cr['detected']:<8} | {cr['verdict']}")

    print("\nControlled Evaluation Summary:")
    print(f"TP={ctrl_metrics['TP']}, TN={ctrl_metrics['TN']}, FP={ctrl_metrics['FP']}, FN={ctrl_metrics['FN']}")
    print(f"TPR={ctrl_metrics['TPR']:.2f}%, FNR={ctrl_metrics['FNR']:.2f}%, FPR={ctrl_metrics['FPR']:.2f}%, TNR={ctrl_metrics['TNR']:.2f}%")

    print("\n[OK] Task #4 Validation Completed Successfully!")

if __name__ == "__main__":
    main()
