import requests
import json
import sys

BASE_URL = "http://127.0.0.1:8000"

def test_api():
    print("=== Testing Quantum QDS Dashboard Endpoints & 10 QA Scenarios ===")
    
    # 0. Health check
    res = requests.get(f"{BASE_URL}/api/health")
    assert res.status_code == 200, f"Health check failed: {res.text}"
    print(f"[PASS] Health check: {res.json()['status']} ({res.json()['project']})")

    # 0.1 States
    res = requests.get(f"{BASE_URL}/api/states")
    assert res.status_code == 200
    print(f"[PASS] States endpoint: {res.json()['states']}, attacks: {res.json()['attacks']}")

    # Reset Replay cache first
    res = requests.post(f"{BASE_URL}/api/replay/reset")
    assert res.status_code == 200
    print(f"[PASS] Replay cache reset: {res.json()}")

    # Scenario 1: |0⟩ + NONE + Bob -> VALID
    p1 = {"state": "0", "attack": "NONE", "verifier": "Bob", "sender": "Alice", "shots": 1000, "error_threshold_pct": 10.0, "chi_threshold": 10.0, "channel_gate": "Z"}
    r1 = requests.post(f"{BASE_URL}/api/verify", json=p1).json()
    assert r1["status"] == "VALID", f"Scenario 1 failed: {r1}"
    print(f"[PASS] Scenario 1 (|0> + NONE + Bob): status={r1['status']}, error_rate={r1['error_rate_percent']}%, chi2={r1['chi_square']}")

    # Scenario 2: |1⟩ + NONE + Bob -> VALID
    p2 = {"state": "1", "attack": "NONE", "verifier": "Bob", "sender": "Alice", "shots": 1000, "error_threshold_pct": 10.0, "chi_threshold": 10.0, "channel_gate": "Z"}
    r2 = requests.post(f"{BASE_URL}/api/verify", json=p2).json()
    assert r2["status"] == "VALID", f"Scenario 2 failed: {r2}"
    print(f"[PASS] Scenario 2 (|1> + NONE + Bob): status={r2['status']}, error_rate={r2['error_rate_percent']}%, chi2={r2['chi_square']}")

    # Scenario 3: |+⟩ + NONE + Bob -> VALID
    p3 = {"state": "+", "attack": "NONE", "verifier": "Bob", "sender": "Alice", "shots": 1000, "error_threshold_pct": 10.0, "chi_threshold": 10.0, "channel_gate": "Z"}
    r3 = requests.post(f"{BASE_URL}/api/verify", json=p3).json()
    assert r3["status"] == "VALID", f"Scenario 3 failed: {r3}"
    print(f"[PASS] Scenario 3 (|+> + NONE + Bob): status={r3['status']}, error_rate={r3['error_rate_percent']}%, chi2={r3['chi_square']}")

    # Scenario 4: |−⟩ + NONE + Bob -> VALID
    p4 = {"state": "-", "attack": "NONE", "verifier": "Bob", "sender": "Alice", "shots": 1000, "error_threshold_pct": 10.0, "chi_threshold": 10.0, "channel_gate": "Z"}
    r4 = requests.post(f"{BASE_URL}/api/verify", json=p4).json()
    assert r4["status"] == "VALID", f"Scenario 4 failed: {r4}"
    print(f"[PASS] Scenario 4 (|-> + NONE + Bob): status={r4['status']}, error_rate={r4['error_rate_percent']}%, chi2={r4['chi_square']}")

    # Scenario 5: |0⟩ + FORGERY + Bob -> THREAT
    p5 = {"state": "0", "attack": "FORGERY", "verifier": "Bob", "sender": "Alice", "shots": 1000, "error_threshold_pct": 10.0, "chi_threshold": 10.0, "channel_gate": "Z"}
    r5 = requests.post(f"{BASE_URL}/api/verify", json=p5).json()
    assert r5["status"] == "THREAT", f"Scenario 5 failed: {r5}"
    print(f"[PASS] Scenario 5 (|0> + FORGERY + Bob): status={r5['status']}, error_rate={r5['error_rate_percent']}%, chi2={r5['chi_square']}")

    # Scenario 6: |+⟩ + CHANNEL + Bob -> THREAT
    p6 = {"state": "+", "attack": "CHANNEL", "verifier": "Bob", "sender": "Alice", "shots": 1000, "error_threshold_pct": 10.0, "chi_threshold": 10.0, "channel_gate": "Z"}
    r6 = requests.post(f"{BASE_URL}/api/verify", json=p6).json()
    assert r6["status"] == "THREAT", f"Scenario 6 failed: {r6}"
    print(f"[PASS] Scenario 6 (|+> + CHANNEL(Z) + Bob): status={r6['status']}, error_rate={r6['error_rate_percent']}%, chi2={r6['chi_square']}")

    # Scenario 7: IMPERSONATION + Bob -> THREAT
    p7 = {"state": "0", "attack": "IMPERSONATION", "verifier": "Bob", "sender": "Attacker", "shots": 1000, "error_threshold_pct": 10.0, "chi_threshold": 10.0, "channel_gate": "Z"}
    r7 = requests.post(f"{BASE_URL}/api/verify", json=p7).json()
    assert r7["status"] == "THREAT", f"Scenario 7 failed: {r7}"
    print(f"[PASS] Scenario 7 (IMPERSONATION + Bob): status={r7['status']}")

    # Scenario 8: REPLAY first submission -> VALID
    fixed_sig = "sig_fixed_replay_test_001"
    p8 = {"state": "0", "attack": "REPLAY", "verifier": "Bob", "sender": "Alice", "shots": 1000, "error_threshold_pct": 10.0, "chi_threshold": 10.0, "channel_gate": "Z", "signature_id": fixed_sig, "digital_message": "Msg 1"}
    r8 = requests.post(f"{BASE_URL}/api/verify", json=p8).json()
    assert r8["status"] == "VALID", f"Scenario 8 failed: {r8}"
    print(f"[PASS] Scenario 8 (REPLAY 1st submission): status={r8['status']}, replay_detected={r8['attack_details'].get('replay_detected')}")

    # Scenario 9: REPLAY second submission with SAME signature -> THREAT
    r9 = requests.post(f"{BASE_URL}/api/verify", json=p8).json()
    assert r9["status"] == "THREAT", f"Scenario 9 failed: {r9}"
    print(f"[PASS] Scenario 9 (REPLAY 2nd submission): status={r9['status']}, replay_detected={r9['attack_details'].get('replay_detected')}")

    # Scenario 10: NONE + Eve -> BLOCKED
    p10 = {"state": "0", "attack": "NONE", "verifier": "Eve", "sender": "Alice", "shots": 1000, "error_threshold_pct": 10.0, "chi_threshold": 10.0, "channel_gate": "Z"}
    r10 = requests.post(f"{BASE_URL}/api/verify", json=p10).json()
    assert r10["status"] == "BLOCKED", f"Scenario 10 failed: {r10}"
    print(f"[PASS] Scenario 10 (NONE + Eve): status={r10['status']}, message={r10.get('message')}")

    # Test Tabs endpoints
    r_e2e = requests.get(f"{BASE_URL}/api/end-to-end?shots=1000")
    assert r_e2e.status_code == 200
    print(f"[PASS] End-to-End Suite endpoint: returned {len(r_e2e.json().get('matrix', []))} matrix items")

    r_sec = requests.get(f"{BASE_URL}/api/security-analysis?shots=1000")
    assert r_sec.status_code == 200
    print(f"[PASS] Security Analysis endpoint: TPR={r_sec.json().get('metrics_summary', {}).get('TPR')}%")

    r_perf = requests.get(f"{BASE_URL}/api/performance?attempts=10&shots=1000")
    assert r_perf.status_code == 200
    print(f"[PASS] Performance endpoint: avg_latency={r_perf.json().get('latency_stats', {}).get('mean_ms')} ms")

    r_res = requests.get(f"{BASE_URL}/api/research-evaluation?shots=1000")
    assert r_res.status_code == 200
    print(f"[PASS] Research & Compliance endpoint OK")

    # Static file check
    r_html = requests.get(f"{BASE_URL}/")
    assert r_html.status_code == 200 and "QUANTUM QUBITS" in r_html.text
    print(f"[PASS] Frontend index.html served: length={len(r_html.text)} chars")

    r_css = requests.get(f"{BASE_URL}/style.css")
    assert r_css.status_code == 200 and "--c-cyan" in r_css.text
    print(f"[PASS] Frontend style.css served: length={len(r_css.text)} chars")

    r_js = requests.get(f"{BASE_URL}/app.js")
    assert r_js.status_code == 200 and "animateCommunicationFlow" in r_js.text
    print(f"[PASS] Frontend app.js served: length={len(r_js.text)} chars")

    print("\nALL 10 QA SCENARIOS + API ENDPOINTS PASSED SUCCESSFULLY!")

if __name__ == "__main__":
    test_api()
