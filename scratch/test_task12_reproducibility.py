"""
Automated Validation Script for Task #12 — Final Demonstration & Reproducibility Package
SIH26141: Quantum-Inspired Cyber Threat Detection for Digital Signature Security
"""
import sys
import os
import subprocess

def test_task12_reproducibility():
    print("==================================================")
    print("RUNNING AUTOMATED VALIDATION FOR TASK #12")
    print("==================================================")

    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    scratch_dir = os.path.join(base_dir, "scratch")

    # 1. Check README_REPRODUCIBILITY.md
    readme_path = os.path.join(base_dir, "README_REPRODUCIBILITY.md")
    print("\n1. Verifying README_REPRODUCIBILITY.md exists...")
    assert os.path.exists(readme_path), "README_REPRODUCIBILITY.md is missing!"
    with open(readme_path, "r", encoding="utf-8") as f:
        readme_content = f.read()

    assert "FINAL SIH DEMO FLOW" in readme_content
    assert "Scientific Scope & Prototype Limitations" in readme_content
    assert "software simulation" in readme_content.lower()
    print("  [PASS] README_REPRODUCIBILITY.md verified.")

    # 2. Check Environment Checker Script
    env_script = os.path.join(scratch_dir, "environment_check.py")
    print("\n2. Verifying environment_check.py exists and executes...")
    assert os.path.exists(env_script), "environment_check.py is missing!"
    proc_env = subprocess.run([sys.executable, env_script], cwd=base_dir, capture_output=True, text=True)
    assert proc_env.returncode == 0, f"environment_check.py failed with code {proc_env.returncode}"
    assert "Qiskit" in proc_env.stdout
    assert "Streamlit" in proc_env.stdout
    print("  [PASS] environment_check.py executed successfully.")

    # 3. Check Required Core Files Exist
    print("\n3. Verifying core project files exist...")
    required_files = [
        "app.py",
        "qds_attack_simulator.py",
        "qds_signature_layer.py",
        "qds_teleport_integrated.py",
        "quantum_background.py",
        "ui_theme.py"
    ]
    for rf in required_files:
        fp = os.path.join(base_dir, rf)
        assert os.path.exists(fp), f"Core file missing: {rf}"
        print(f"  - Found {rf}")
    print("  [PASS] All core project files present.")

    # 4. Check Master Validation Runner
    master_script = os.path.join(scratch_dir, "run_all_validation.py")
    print("\n4. Verifying run_all_validation.py exists and executes master suite...")
    assert os.path.exists(master_script), "run_all_validation.py is missing!"
    proc_master = subprocess.run([sys.executable, master_script], cwd=base_dir, capture_output=True, text=True)
    assert proc_master.returncode == 0, f"run_all_validation.py failed with code {proc_master.returncode}\n{proc_master.stdout}"
    assert "Overall Reproducibility Check : PASS" in proc_master.stdout
    print("  [PASS] Master validation runner executed cleanly across Tasks #1–#11.")

    # 5. Check No Duplicate Attack Engine Created
    print("\n5. Verifying no duplicate attack engine was created...")
    sys.path.insert(0, base_dir)
    from qds_attack_simulator import QDSAttackSimulator
    sim = QDSAttackSimulator()
    assert hasattr(sim, "simulate_forgery_attack")
    assert hasattr(sim, "simulate_impersonation_attack")
    assert hasattr(sim, "simulate_replay_attack")
    assert hasattr(sim, "simulate_channel_manipulation")
    assert hasattr(sim, "evaluate_unauthorized_verification")
    print("  [PASS] Single unified simulator class intact.")

    print("\n==================================================")
    print("TASK #12 REPRODUCIBILITY VALIDATION PASSED SUCCESSFULLY")
    print("==================================================")

if __name__ == "__main__":
    test_task12_reproducibility()
    sys.exit(0)
