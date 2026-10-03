import sys
import os
import json
import subprocess
import time
import urllib.request
import urllib.error

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

def run_live_http_tests():
    print("==================================================")
    print("STARTING LIVE FASTAPI BACKEND VERIFICATION")
    print("==================================================")

    env = os.environ.copy()
    env["PYTHONIOENCODING"] = "utf-8"
    env["PYTHONUTF8"] = "1"

    port = 8008
    base_url = f"http://127.0.0.1:{port}"

    cmd = [
        sys.executable, "-m", "uvicorn", "api:app",
        "--host", "127.0.0.1", "--port", str(port)
    ]
    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, env=env, encoding="utf-8")
    
    # Wait for server startup
    time.sleep(2.5)

    passed = 0

    def make_req(path, method="GET", body=None):
        url = base_url + path
        headers = {"Content-Type": "application/json"} if body else {}
        data = json.dumps(body).encode("utf-8") if body is not None else None
        req = urllib.request.Request(url, data=data, headers=headers, method=method)
        try:
            with urllib.request.urlopen(req) as resp:
                res_bytes = resp.read()
                res_str = res_bytes.decode("utf-8")
                try:
                    return resp.status, json.loads(res_str)
                except Exception as e:
                    return resp.status, res_str
        except urllib.error.HTTPError as e:
            err_body = e.read().decode("utf-8")
            try:
                err_json = json.loads(err_body)
            except:
                err_json = err_body
            return e.code, err_json

    try:
        # Test 1: GET / (Frontend Dashboard)
        req_root = urllib.request.Request(base_url + "/", method="GET")
        with urllib.request.urlopen(req_root) as resp:
            print(f"[PASS] GET / (Frontend Dashboard): HTTP {resp.status}")
            passed += 1

        # Test 2: GET /api/health
        code, d = make_req("/api/health")
        print(f"[PASS] GET /api/health: HTTP {code}, Backend: {d.get('qiskit_backend') if isinstance(d, dict) else d}")
        assert code == 200 and isinstance(d, dict) and d.get("status") == "healthy"
        passed += 1

        # Test 3: GET /api/states
        code, d = make_req("/api/states")
        print(f"[PASS] GET /api/states: HTTP {code}, States: {d.get('states') if isinstance(d, dict) else d}")
        assert code == 200 and isinstance(d, dict) and "0" in d.get("states")
        passed += 1

        # Test 4: POST /api/verify [NONE]
        code, d = make_req("/api/verify", method="POST", body={
            "state": "0", "attack": "NONE", "verifier": "Bob", "shots": 1000
        })
        print(f"[PASS] POST /api/verify [NONE]: HTTP {code}, Status: {d.get('status')}, Error Rate: {d.get('error_rate_percent')}%")
        assert code == 200 and d.get("status") == "VALID" and d.get("threat_detected") is False
        passed += 1

        # Test 5: POST /api/verify [FORGERY]
        code, d = make_req("/api/verify", method="POST", body={
            "state": "0", "attack": "FORGERY", "verifier": "Bob", "shots": 1000
        })
        print(f"[PASS] POST /api/verify [FORGERY]: HTTP {code}, Status: {d.get('status')}, Threat: {d.get('threat_detected')}")
        assert code == 200 and d.get("status") == "THREAT" and d.get("threat_detected") is True
        passed += 1

        # Test 6: POST /api/verify [CHANNEL]
        code, d = make_req("/api/verify", method="POST", body={
            "state": "+", "attack": "CHANNEL", "channel_gate": "Z", "verifier": "Bob", "shots": 1000
        })
        print(f"[PASS] POST /api/verify [CHANNEL]: HTTP {code}, Status: {d.get('status')}, Threat: {d.get('threat_detected')}")
        assert code == 200 and d.get("status") == "THREAT" and d.get("threat_detected") is True
        passed += 1

        # Test 7: POST /api/verify [UNAUTHORIZED EVE]
        code, d = make_req("/api/verify", method="POST", body={
            "state": "0", "attack": "NONE", "verifier": "Eve", "shots": 1000
        })
        print(f"[PASS] POST /api/verify [UNAUTHORIZED EVE]: HTTP {code}, Status: {d.get('status')}, Message: {d.get('message')}")
        assert code == 200 and d.get("status") == "BLOCKED" and d.get("threat_detected") is True
        passed += 1

        # Test 8: POST /api/verify [IMPERSONATION]
        code, d = make_req("/api/verify", method="POST", body={
            "state": "0", "attack": "IMPERSONATION", "sender": "Attacker", "verifier": "Bob", "shots": 1000
        })
        print(f"[PASS] POST /api/verify [IMPERSONATION]: HTTP {code}, Status: {d.get('status')}")
        assert code == 200 and d.get("status") == "THREAT" and d.get("threat_detected") is True
        passed += 1

        # Test 9: POST /api/verify [REPLAY]
        sig_id = "replay_live_sig_999"
        code1, d1 = make_req("/api/verify", method="POST", body={
            "state": "0", "attack": "REPLAY", "digital_message": "Msg1", "signature_id": sig_id, "verifier": "Bob"
        })
        code2, d2 = make_req("/api/verify", method="POST", body={
            "state": "0", "attack": "REPLAY", "digital_message": "Msg1", "signature_id": sig_id, "verifier": "Bob"
        })
        print(f"[PASS] POST /api/verify [REPLAY 1st use]: Status: {d1.get('status')} | [REPLAY 2nd use]: Status: {d2.get('status')}")
        assert code1 == 200 and d1.get("status") == "VALID"
        assert code2 == 200 and d2.get("status") == "THREAT"
        passed += 2

        # Test 10: GET /api/security-analysis
        code, d = make_req("/api/security-analysis?shots=500")
        print(f"[PASS] GET /api/security-analysis: HTTP {code}")
        assert code == 200
        passed += 1

        # Test 11: GET /api/end-to-end
        code, d = make_req("/api/end-to-end?shots=500")
        print(f"[PASS] GET /api/end-to-end: HTTP {code}")
        assert code == 200
        passed += 1

        # Test 12: GET /api/performance
        code, d = make_req("/api/performance?attempts=5&shots=500")
        print(f"[PASS] GET /api/performance: HTTP {code}")
        assert code == 200
        passed += 1

        # Test 13: GET /api/research-evaluation
        code, d = make_req("/api/research-evaluation?shots=500")
        print(f"[PASS] GET /api/research-evaluation: HTTP {code}")
        assert code == 200
        passed += 1

        # Test 14: GET /api/mathematical-model
        code, d = make_req("/api/mathematical-model?state=0&basis=Z&attack=FORGERY")
        print(f"[PASS] GET /api/mathematical-model: HTTP {code}")
        assert code == 200
        passed += 1

        # Test 15: POST /api/replay/reset
        code, d = make_req("/api/replay/reset", method="POST")
        print(f"[PASS] POST /api/replay/reset: HTTP {code}")
        assert code == 200
        passed += 1

        # Test 16: Invalid state request validation (HTTP 400)
        code, d = make_req("/api/verify", method="POST", body={"state": "INVALID", "attack": "NONE"})
        print(f"[PASS] POST /api/verify [INVALID STATE]: HTTP {code} (Expected 400)")
        assert code == 400
        passed += 1

        print("==================================================")
        print(f"ALL LIVE BACKEND TESTS PASSED: {passed} TESTS PASSED, 0 FAILED")
        print("==================================================")

    finally:
        proc.terminate()
        proc.wait()

if __name__ == "__main__":
    run_live_http_tests()
