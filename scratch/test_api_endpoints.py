import sys
import json
from fastapi.testclient import TestClient

from api import app

client = TestClient(app)

def run_tests():
    print("==================================================")
    print("STARTING API ENDPOINT & QUANTUM ATTACK VERIFICATION")
    print("==================================================")
    
    passed = 0
    failed = 0

    def assert_status(name, response, expected_code=200):
        nonlocal passed, failed
        if response.status_code == expected_code:
            print(f"✅ {name}: HTTP {response.status_code}")
            passed += 1
            return True
        else:
            print(f"❌ {name}: Got HTTP {response.status_code}, expected {expected_code}")
            print(f"   Response: {response.text}")
            failed += 1
            return False

    # 1. GET /
    r = client.get("/")
    assert_status("GET / (Frontend Dashboard)", r)

    # 2. GET /api/health
    r = client.get("/api/health")
    if assert_status("GET /api/health", r):
        data = r.json()
        print(f"   Backend: {data.get('qiskit_backend')}, Status: {data.get('status')}")

    # 3. GET /api/states
    r = client.get("/api/states")
    if assert_status("GET /api/states", r):
        data = r.json()
        print(f"   States: {data.get('states')}, Attacks: {data.get('attacks')}")

    # 4. POST /api/verify - NONE (State |0>, Basis Z, Verifier Bob)
    r = client.post("/api/verify", json={
        "state": "0",
        "attack": "NONE",
        "verifier": "Bob",
        "shots": 1000
    })
    if assert_status("POST /api/verify [NONE]", r):
        data = r.json()
        print(f"   Status: {data.get('status')}, Threat: {data.get('threat_detected')}, Error Rate: {data.get('error_rate_percent')}%, Chi-Square: {data.get('chi_square')}")
        assert data.get("status") == "VALID"
        assert data.get("threat_detected") == False

    # 5. POST /api/verify - FORGERY (State |0>)
    r = client.post("/api/verify", json={
        "state": "0",
        "attack": "FORGERY",
        "verifier": "Bob",
        "shots": 1000
    })
    if assert_status("POST /api/verify [FORGERY]", r):
        data = r.json()
        print(f"   Status: {data.get('status')}, Threat: {data.get('threat_detected')}, Error Rate: {data.get('error_rate_percent')}%, Chi-Square: {data.get('chi_square')}")
        assert data.get("status") == "THREAT"
        assert data.get("threat_detected") == True

    # 6. POST /api/verify - CHANNEL (State |+>, Gate Z)
    r = client.post("/api/verify", json={
        "state": "+",
        "attack": "CHANNEL",
        "channel_gate": "Z",
        "verifier": "Bob",
        "shots": 1000
    })
    if assert_status("POST /api/verify [CHANNEL]", r):
        data = r.json()
        print(f"   Status: {data.get('status')}, Threat: {data.get('threat_detected')}, Error Rate: {data.get('error_rate_percent')}%, Chi-Square: {data.get('chi_square')}")
        assert data.get("status") == "THREAT"
        assert data.get("threat_detected") == True

    # 7. POST /api/verify - UNAUTHORIZED VERIFIER (Eve)
    r = client.post("/api/verify", json={
        "state": "0",
        "attack": "NONE",
        "verifier": "Eve",
        "shots": 1000
    })
    if assert_status("POST /api/verify [UNAUTHORIZED EVE]", r):
        data = r.json()
        print(f"   Status: {data.get('status')}, Message: {data.get('message')}")
        assert data.get("status") == "BLOCKED"
        assert data.get("threat_detected") == True

    # 8. POST /api/verify - IMPERSONATION
    r = client.post("/api/verify", json={
        "state": "0",
        "attack": "IMPERSONATION",
        "sender": "Attacker",
        "verifier": "Bob",
        "shots": 1000
    })
    if assert_status("POST /api/verify [IMPERSONATION]", r):
        data = r.json()
        print(f"   Status: {data.get('status')}, Threat: {data.get('threat_detected')}")
        assert data.get("status") == "THREAT"
        assert data.get("threat_detected") == True

    # 9. POST /api/verify - REPLAY ATTACK (2 consecutive requests with same signature_id)
    sig_id = "replay_test_unique_001"
    r1 = client.post("/api/verify", json={
        "state": "0",
        "attack": "REPLAY",
        "digital_message": "Secret Payload",
        "signature_id": sig_id,
        "verifier": "Bob",
        "shots": 1000
    })
    r2 = client.post("/api/verify", json={
        "state": "0",
        "attack": "REPLAY",
        "digital_message": "Secret Payload",
        "signature_id": sig_id,
        "verifier": "Bob",
        "shots": 1000
    })
    if assert_status("POST /api/verify [REPLAY 1st use]", r1) and assert_status("POST /api/verify [REPLAY 2nd use]", r2):
        d1, d2 = r1.json(), r2.json()
        print(f"   Use 1 Status: {d1.get('status')}, Use 2 Status: {d2.get('status')}")
        assert d1.get("status") == "VALID"
        assert d2.get("status") == "THREAT"

    # 10. GET /api/security-analysis
    r = client.get("/api/security-analysis?shots=500")
    if assert_status("GET /api/security-analysis", r):
        data = r.json()
        print(f"   Keys returned: {list(data.keys())}")

    # 11. GET /api/end-to-end
    r = client.get("/api/end-to-end?shots=500")
    if assert_status("GET /api/end-to-end", r):
        data = r.json()
        scenarios = data.get("scenarios", [])
        print(f"   E2E Scenarios Count: {len(scenarios)}")

    # 12. GET /api/performance
    r = client.get("/api/performance?attempts=10&shots=500")
    if assert_status("GET /api/performance", r):
        data = r.json()
        print(f"   Benchmark cases: {len(data.get('benchmarks', []))}")

    # 13. GET /api/research-evaluation
    r = client.get("/api/research-evaluation?shots=500")
    assert_status("GET /api/research-evaluation", r)

    # 14. GET /api/mathematical-model
    r = client.get("/api/mathematical-model?state=0&basis=Z&attack=FORGERY")
    assert_status("GET /api/mathematical-model", r)

    # 15. POST /api/replay/reset
    r = client.post("/api/replay/reset")
    assert_status("POST /api/replay/reset", r)

    # 16. Validation Error handling (Invalid state)
    r = client.post("/api/verify", json={
        "state": "INVALID_STATE",
        "attack": "NONE"
    })
    assert_status("POST /api/verify [INVALID STATE 400]", r, expected_code=400)

    print("==================================================")
    print(f"TEST RESULTS: {passed} PASSED, {failed} FAILED")
    print("==================================================")
    if failed > 0:
        sys.exit(1)

if __name__ == "__main__":
    run_tests()
