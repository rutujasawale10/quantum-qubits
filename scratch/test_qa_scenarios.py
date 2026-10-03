import urllib.request
import json
import time
import sys

# Ensure UTF-8 output
sys.stdout.reconfigure(encoding='utf-8')

BASE_URL = "http://127.0.0.1:8000"

def post_json(endpoint, data):
    url = f"{BASE_URL}{endpoint}"
    req = urllib.request.Request(
        url,
        data=json.dumps(data).encode("utf-8"),
        headers={"Content-Type": "application/json"}
    )
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read().decode("utf-8"))

def get_json(endpoint):
    url = f"{BASE_URL}{endpoint}"
    req = urllib.request.Request(url)
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read().decode("utf-8"))

def run_tests():
    print("=== STARTING QA API VERIFICATION TESTS ===\n")
    
    # 1. Reset replay cache first
    reset_resp = post_json("/api/replay/reset", {})
    print(f"Replay cache reset: {reset_resp}")
    
    scenarios = [
        {"state": "0", "attack": "NONE", "verifier": "Bob", "sender": "Alice", "expected": "VALID", "desc": "|0> NONE Bob"},
        {"state": "1", "attack": "NONE", "verifier": "Bob", "sender": "Alice", "expected": "VALID", "desc": "|1> NONE Bob"},
        {"state": "+", "attack": "NONE", "verifier": "Bob", "sender": "Alice", "expected": "VALID", "desc": "|+> NONE Bob"},
        {"state": "-", "attack": "NONE", "verifier": "Bob", "sender": "Alice", "expected": "VALID", "desc": "|-> NONE Bob"},
        {"state": "0", "attack": "FORGERY", "verifier": "Bob", "sender": "Alice", "expected": "THREAT", "desc": "|0> FORGERY Bob"},
        {"state": "+", "attack": "CHANNEL", "verifier": "Bob", "sender": "Alice", "expected": "THREAT", "desc": "|+> CHANNEL Bob (Pauli-Z on |+>)"},
        {"state": "0", "attack": "IMPERSONATION", "verifier": "Bob", "sender": "Attacker", "expected": "THREAT", "desc": "any IMPERSONATION Bob"},
    ]
    
    all_passed = True
    
    for i, s in enumerate(scenarios, 1):
        payload = {
            "state": s["state"],
            "attack": s["attack"],
            "verifier": s["verifier"],
            "sender": s["sender"],
            "shots": 1000,
            "error_threshold_pct": 10.0,
            "chi_threshold": 10.0,
            "channel_gate": "Z",
            "digital_message": "SIH26141 QA Test",
            "signature_id": f"sig_test_{i}_{int(time.time()*1000)}"
        }
        res = post_json("/api/verify", payload)
        verdict = res.get("status")
        match = (verdict == s["expected"])
        if not match:
            all_passed = False
        print(f"Scenario {i}: [{s['desc']}] => Status: {verdict} (Expected: {s['expected']}) -> {'PASS' if match else 'FAIL'}")
        print(f"   Details: error_rate={res.get('error_rate_percent')}%, chi_square={res.get('chi_square')}, basis={res.get('basis')}")

    # Test Scenario 8: REPLAY attack
    print("\nTesting Scenario 8: REPLAY attack")
    post_json("/api/replay/reset", {})
    replay_sig_id = f"sig_replay_{int(time.time()*1000)}"
    replay_payload = {
        "state": "0",
        "attack": "REPLAY",
        "verifier": "Bob",
        "sender": "Alice",
        "shots": 1000,
        "error_threshold_pct": 10.0,
        "chi_threshold": 10.0,
        "channel_gate": "Z",
        "digital_message": "SIH26141 Replay Test",
        "signature_id": replay_sig_id
    }
    # First execution: should be VALID
    res1 = post_json("/api/verify", replay_payload)
    match1 = (res1.get("status") == "VALID")
    print(f"Scenario 8 (1st run): Status: {res1.get('status')} (Expected: VALID) -> {'PASS' if match1 else 'FAIL'}")
    
    # Second execution: should be THREAT (replay detected)
    res2 = post_json("/api/verify", replay_payload)
    match2 = (res2.get("status") == "THREAT")
    print(f"Scenario 8 (2nd run): Status: {res2.get('status')} (Expected: THREAT) -> {'PASS' if match2 else 'FAIL'}")
    print(f"   Replay detected details: {res2.get('attack_details')}")
    if not (match1 and match2):
        all_passed = False

    # Test Scenario 9: Eve verifier
    print("\nTesting Scenario 9: Eve verifier")
    eve_payload = {
        "state": "0",
        "attack": "NONE",
        "verifier": "Eve",
        "sender": "Alice",
        "shots": 1000,
        "error_threshold_pct": 10.0,
        "chi_threshold": 10.0,
        "channel_gate": "Z",
        "digital_message": "SIH26141 Eve Test",
        "signature_id": f"sig_eve_{int(time.time()*1000)}"
    }
    res_eve = post_json("/api/verify", eve_payload)
    match_eve = (res_eve.get("status") == "BLOCKED")
    print(f"Scenario 9: Status: {res_eve.get('status')} (Expected: BLOCKED) -> {'PASS' if match_eve else 'FAIL'}")
    print(f"   Blocked message: {res_eve.get('message')}")
    if not match_eve:
        all_passed = False

    # Test GET Endpoints
    print("\nTesting other API endpoints:")
    endpoints = [
        "/api/end-to-end?shots=1000",
        "/api/security-analysis?shots=1000",
        "/api/performance?attempts=20&shots=1000",
        "/api/research-evaluation?shots=1000"
    ]
    for ep in endpoints:
        res = get_json(ep)
        status_ok = bool(res)
        print(f"Endpoint {ep} -> OK: {status_ok}")
        if not status_ok:
            all_passed = False

    print(f"\nOVERALL RESULT: {'ALL PASS' if all_passed else 'SOME FAILED'}")

if __name__ == "__main__":
    run_tests()
