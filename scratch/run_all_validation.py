"""
Master Validation Runner for SIH26141 QDS Security Prototype
Executes all Task #1–#11 validation scripts sequentially and verifies overall reproducibility.
"""
import sys
import os
import subprocess

def run_master_validation():
    print("==================================================")
    print("SIH26141 MASTER VALIDATION RUNNER")
    print("==================================================")

    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    scratch_dir = os.path.join(base_dir, "scratch")

    # 1. Environment Check
    print("\n--- STEP 1: ENVIRONMENT CHECK ---")
    env_script = os.path.join(scratch_dir, "environment_check.py")
    if not os.path.exists(env_script):
        print("MISSING — Environment check script")
        env_pass = False
    else:
        res_env = subprocess.run([sys.executable, env_script], cwd=base_dir)
        env_pass = (res_env.returncode == 0)

    # 2. Sequential Task Validations Tasks #1–#11
    print("\n--- STEP 2: SEQUENTIAL TASK VALIDATION (TASKS #1–#11) ---")
    task_scripts = {
        1: "test_task1_forgery.py",
        2: "test_task2_threshold.py",
        3: "test_task3_pauli.py",
        4: "test_task4_performance.py",
        5: "test_task5_robustness.py",
        6: "test_task6_authorization.py",
        7: "test_task7_performance.py",
        8: "test_task8_security_analysis.py",
        9: "test_task9_math_model.py",
        10: "test_task10_end_to_end.py",
        11: "test_task11_research_evaluation.py"
    }

    task_results = {}
    all_tasks_passed = True

    for t_num, s_name in task_scripts.items():
        script_path = os.path.join(scratch_dir, s_name)
        if not os.path.exists(script_path):
            print(f"\n[TASK #{t_num}] MISSING — Task #{t_num} validation script ({s_name})")
            task_results[t_num] = "MISSING"
            all_tasks_passed = False
            continue

        print(f"\nExecuting Task #{t_num} Validation ({s_name})...")
        proc = subprocess.run([sys.executable, script_path], cwd=base_dir)
        if proc.returncode == 0:
            task_results[t_num] = "PASS"
        else:
            task_results[t_num] = "FAIL"
            all_tasks_passed = False

    # 3. Demo Integration Check
    print("\n--- STEP 3: DEMO INTEGRATION CHECK ---")
    try:
        sys.path.insert(0, base_dir)
        from qds_attack_simulator import QDSAttackSimulator
        sim = QDSAttackSimulator()
        _ = sim.run_research_evaluation()
        demo_pass = True
        print("Demo Integration Check: PASS")
    except Exception as e:
        print(f"Demo Integration Check: FAIL — {e}")
        demo_pass = False

    # 4. Final Summary Table
    overall_pass = env_pass and all_tasks_passed and demo_pass

    print("\n==================================================")
    print("FINAL VALIDATION SUMMARY")
    print("==================================================")
    for t_num in range(1, 12):
        status = task_results.get(t_num, "FAIL")
        print(f"Task #{t_num:<2} : {status}")

    print("")
    print(f"Environment : {'PASS' if env_pass else 'FAIL'}")
    print(f"Demo Integration : {'PASS' if demo_pass else 'FAIL'}")
    print("")
    print(f"Overall Reproducibility Check : {'PASS' if overall_pass else 'FAIL'}")
    print("==================================================")

    return overall_pass

if __name__ == "__main__":
    passed = run_master_validation()
    sys.exit(0 if passed else 1)
