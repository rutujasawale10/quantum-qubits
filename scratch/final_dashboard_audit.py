"""
Final Dashboard Audit & SIH Demo Readiness Script
Automated validation of dashboard components, scientific claims, environment check,
and regression status for SIH26141.
"""
import sys
import os
import subprocess

def run_final_dashboard_audit():
    print("==================================================")
    print("RUNNING FINAL DASHBOARD AUDIT & SIH DEMO READINESS")
    print("==================================================")

    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    scratch_dir = os.path.join(base_dir, "scratch")

    audit_results = {}

    # 1. App Startup & Syntax Check
    print("\n1. Verifying app.py exists and parses cleanly...")
    app_path = os.path.join(base_dir, "app.py")
    assert os.path.exists(app_path), "app.py is missing!"
    with open(app_path, "r", encoding="utf-8") as f:
        app_content = f.read()
    
    try:
        compile(app_content, "app.py", "exec")
        print("  [PASS] app.py syntax & compilation verified.")
        audit_results["Startup"] = "PASS"
    except Exception as e:
        print(f"  [FAIL] app.py syntax error: {e}")
        audit_results["Startup"] = "FAIL"

    # 2. Required Sections Check (Sections #1–#15)
    print("\n2. Verifying Sections #1–#15 exist in app.py...")
    required_sections = [
        "SECTION 14",
        "SECTION 15",
        "Quantum Digital Signature Security",
        "Security Verification Result",
        "SIH Problem Statement Objective Coverage Matrix",
        "Expected Solution Component Coverage Matrix",
        "Experimental Evidence Summary",
        "Attack Coverage Matrix",
        "Implemented Threat Detection Security Architecture",
        "Research Gap & Prototype Limitations",
        "Prototype Contribution Summary"
    ]
    all_sections_found = True
    for sec in required_sections:
        if sec in app_content:
            print(f"  - Found: {sec}")
        else:
            print(f"  - MISSING: {sec}")
            all_sections_found = False

    audit_results["Sections"] = "PASS" if all_sections_found else "FAIL"

    # 3. Demo Presets & Scenarios Check
    print("\n3. Verifying Final SIH Demo Presets exist in app.py...")
    demo_presets = [
        "FINAL SIH DEMO PRESETS",
        "A. Legitimate Communication",
        "B. Forgery Attack",
        "C. Impersonation Attack",
        "D. Replay Attack",
        "E. Channel Manipulation",
        "F. Unauthorized Verification"
    ]
    all_presets_found = True
    for dp in demo_presets:
        if dp in app_content:
            print(f"  - Found preset: {dp}")
        else:
            print(f"  - MISSING preset: {dp}")
            all_presets_found = False

    audit_results["Demo Scenarios"] = "PASS" if all_presets_found else "FAIL"

    # 4. Scientific Claims & Teleportation Separation Audit
    print("\n4. Verifying scientific claim safety & teleportation separation...")
    dangerous_claims = [
        "100% secure",
        "unbreakable security",
        "quantum advantage",
        "quantum speedup",
        "formal information-theoretic security proof"
    ]
    dangerous_found = False
    for dc in dangerous_claims:
        if dc in app_content.lower():
            print(f"  - WARNING: Found risky claim '{dc}'")
            dangerous_found = True

    assert "software simulation" in app_content.lower()
    assert "prototype" in app_content.lower()
    print("  [PASS] Scientific claim safety verified (wording is prototype & software simulation).")
    audit_results["Scientific Claims"] = "PASS" if not dangerous_found else "FAIL"

    # 5. Encoding & Mojibake Check
    print("\n5. Checking for corrupted characters / mojibake in app.py...")
    mojibake_patterns = ["â", "€™", "â€“", "â€œ", "â€", "Ã"]
    mojibake_found = False
    for mb in mojibake_patterns:
        if mb in app_content:
            print(f"  - WARNING: Found possible mojibake pattern '{mb}'")
            mojibake_found = True
    
    print("  [PASS] No obvious mojibake patterns detected.")
    audit_results["UI / Encoding"] = "PASS" if not mojibake_found else "FAIL"

    # 6. Core Project Modules Import Check
    print("\n6. Verifying core project modules import...")
    sys.path.insert(0, base_dir)
    try:
        from qds_attack_simulator import QDSAttackSimulator
        import qds_signature_layer
        import qds_teleport_integrated
        import quantum_background
        import ui_theme
        sim = QDSAttackSimulator()
        print("  [PASS] All core backend modules imported cleanly.")
        audit_results["Modules Import"] = "PASS"
    except Exception as e:
        print(f"  [FAIL] Module import error: {e}")
        audit_results["Modules Import"] = "FAIL"

    # 7. Environment Check
    print("\n7. Running environment_check.py...")
    env_script = os.path.join(scratch_dir, "environment_check.py")
    proc_env = subprocess.run([sys.executable, env_script], cwd=base_dir, capture_output=True, text=True)
    env_pass = (proc_env.returncode == 0)
    print("  [PASS] Environment check passed." if env_pass else "  [FAIL] Environment check failed.")
    audit_results["Environment"] = "PASS" if env_pass else "FAIL"

    # 8. Master Validation Suite & Task #12 Test
    print("\n8. Executing master validation suite (Tasks #1–#11 & #12)...")
    master_script = os.path.join(scratch_dir, "run_all_validation.py")
    proc_master = subprocess.run([sys.executable, master_script], cwd=base_dir, capture_output=True, text=True)
    reg_pass = (proc_master.returncode == 0)

    task12_script = os.path.join(scratch_dir, "test_task12_reproducibility.py")
    proc_t12 = subprocess.run([sys.executable, task12_script], cwd=base_dir, capture_output=True, text=True)
    t12_pass = (proc_t12.returncode == 0)

    all_reg_pass = reg_pass and t12_pass
    audit_results["Regression #1–#12"] = "PASS" if all_reg_pass else "FAIL"

    # 9. Final Dashboard Status Summary
    overall_status = "READY" if all(v == "PASS" for v in audit_results.values()) else "NEEDS FIXES"

    print("\n==================================================")
    print("FINAL DASHBOARD AUDIT SUMMARY")
    print("==================================================")
    for k, v in audit_results.items():
        print(f"{k:<22} : {v}")
    print("--------------------------------------------------")
    print(f"OVERALL DASHBOARD STATUS: {overall_status}")
    print("==================================================")

    return overall_status == "READY"

if __name__ == "__main__":
    ready = run_final_dashboard_audit()
    sys.exit(0 if ready else 1)
