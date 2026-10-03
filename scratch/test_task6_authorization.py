import sys
import os
sys.path.insert(0, os.path.abspath('.'))

from qds_attack_simulator import QDSAttackSimulator

def main():
    sim = QDSAttackSimulator()
    print("==================================================")
    print("TASK #6 VALIDATION: UNAUTHORIZED VERIFICATION ATTEMPT DETECTION")
    print("==================================================")

    # 1. Test evaluate_unauthorized_verification individually
    print("\n--- INDIVIDUAL EVALUATION TESTS ---")

    # TEST 1: Authorized Verifier (Bob) + Valid Sig
    t1 = sim.evaluate_unauthorized_verification(sender="Alice", expected_verifier="Bob", actual_verifier="Bob", signature_valid=True)
    print(f"TEST 1 (Bob, Valid Sig)   -> Status: {t1['identity_status']}, Access: {t1['access_label']}, Threat: {t1['threat_detected']}, Type: {t1['threat_type']}")
    assert t1["identity_status"] == "AUTHORIZED"
    assert t1["verification_allowed"] == True
    assert t1["threat_detected"] == False

    # TEST 2: Unauthorized Verifier (Eve) + Valid Sig
    t2 = sim.evaluate_unauthorized_verification(sender="Alice", expected_verifier="Bob", actual_verifier="Eve", signature_valid=True)
    print(f"TEST 2 (Eve, Valid Sig)   -> Status: {t2['identity_status']}, Access: {t2['access_label']}, Threat: {t2['threat_detected']}, Type: {t2['threat_type']}")
    assert t2["identity_status"] == "UNAUTHORIZED"
    assert t2["verification_allowed"] == False
    assert t2["threat_detected"] == True
    assert t2["threat_type"] == "UNAUTHORIZED VERIFICATION ATTEMPT"

    # TEST 3: Authorized Verifier (Bob) + Forged Sig
    t3 = sim.evaluate_unauthorized_verification(sender="Alice", expected_verifier="Bob", actual_verifier="Bob", signature_valid=False)
    print(f"TEST 3 (Bob, Forged Sig)  -> Status: {t3['identity_status']}, Access: {t3['access_label']}, Threat: {t3['threat_detected']}, Type: {t3['threat_type']}")
    assert t3["identity_status"] == "AUTHORIZED"
    assert t3["verification_allowed"] == True
    assert t3["threat_type"] != "UNAUTHORIZED VERIFICATION ATTEMPT"

    # TEST 4: Sender Impersonation (Eve -> Bob)
    t4 = sim.evaluate_unauthorized_verification(sender="Eve", expected_verifier="Bob", actual_verifier="Bob", signature_valid=True)
    print(f"TEST 4 (Eve Sender->Bob) -> Status: {t4['identity_status']}, Access: {t4['access_label']}, Threat: {t4['threat_detected']}, Type: {t4['threat_type']}")
    assert t4["identity_status"] == "AUTHORIZED"
    assert t4["verification_allowed"] == True

    # 2. Test run_controlled_authorization_evaluation
    print("\n--- CONTROLLED AUTHORIZATION BENCHMARK ---")
    auth_eval = sim.run_controlled_authorization_evaluation()
    cases = auth_eval["cases"]
    metrics = auth_eval["metrics"]

    print(f"{'Test Name':<45} | {'Sender':<7} | {'Verifier':<8} | {'Sig':<7} | {'Auth Status':<13} | {'Access':<8} | {'Threat':<7} | {'Classification'}")
    print("-" * 140)
    for c in cases:
        print(f"{c['test_name']:<45} | {c['sender']:<7} | {c['actual_verifier']:<8} | {c['sig_valid']:<7} | {c['identity_status']:<13} | {c['verification_allowed']:<8} | {c['threat_detected']:<7} | {c['classification']}")

    print("\n--- AUTHORIZATION METRICS ---")
    print(f"Total Attempts               : {metrics['total_attempts']}")
    print(f"Authorized Attempts          : {metrics['authorized_attempts']}")
    print(f"Unauthorized Attempts        : {metrics['unauthorized_attempts']}")
    print(f"Correctly Allowed Authorized : {metrics['correctly_allowed']}")
    print(f"Correctly Blocked Unauth     : {metrics['correctly_blocked']}")
    print(f"False Authorization          : {metrics['false_authorization']}")
    print(f"Authorization Detection Rate : {metrics['authorization_detection_rate_str']}")
    print(f"False Authorization Rate     : {metrics['false_authorization_rate_str']}")

    print("\n[OK] Task #6 Validation Completed Successfully!")

if __name__ == "__main__":
    main()
