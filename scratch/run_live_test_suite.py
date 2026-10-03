import sys
import os
import json
import urllib.request
import urllib.error

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

BASE_URL = "http://127.0.0.1:8000"

def make_request(endpoint, method="GET", data=None):
    url = BASE_URL + endpoint
    headers = {"Content-Type": "application/json"} if data is not None else {}
    body = json.dumps(data).encode("utf-8") if data is not None else None
    
    req = urllib.request.Request(url, data=body, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req) as resp:
            resp_bytes = resp.read()
            resp_str = resp_bytes.decode("utf-8")
            try:
                return resp.status, json.loads(resp_str)
            except Exception:
                return resp.status, resp_str
    except urllib.error.HTTPError as e:
        err_bytes = e.read()
        err_str = err_bytes.decode("utf-8")
        try:
            return e.code, json.loads(err_str)
        except Exception:
            return e.code, err_str
    except urllib.error.URLError as e:
        return 0, str(e.reason)

def main():
    print("Testing connection to live backend at http://127.0.0.1:8000...")
    status, res = make_request("/api/health")
    if status == 0:
        print("Backend server not running on 8000! Starting background uvicorn server...")
        import subprocess, time
        env = os.environ.copy()
        env["PYTHONIOENCODING"] = "utf-8"
        env["PYTHONUTF8"] = "1"
        proc = subprocess.Popen(
            [sys.executable, "-m", "uvicorn", "api:app", "--host", "127.0.0.1", "--port", "8000"],
            env=env
        )
        time.sleep(2.5)
        status, res = make_request("/api/health")
        print(f"Server startup health check: HTTP {status}")

    results = {}
    details = {}

    # TEST 1 — HEALTH
    st, resp = make_request("/api/health")
    pass_t1 = (st == 200 and isinstance(resp, dict) and resp.get("status") == "healthy")
    results["Test 1 (Health)"] = "PASS" if pass_t1 else "FAIL"
    details["t1"] = {"status": st, "resp": resp}

    # TEST 2 — STATES
    st, resp = make_request("/api/states")
    states_ok = isinstance(resp, dict) and all(s in resp.get("states", []) for s in ["0", "1", "+", "-"])
    attacks_ok = isinstance(resp, dict) and all(a in resp.get("attacks", []) for a in ["NONE", "FORGERY", "IMPERSONATION", "REPLAY", "CHANNEL"])
    pass_t2 = (st == 200 and states_ok and attacks_ok)
    results["Test 2 (States)"] = "PASS" if pass_t2 else "FAIL"
    details["t2"] = {"status": st, "resp": resp}

    # TEST 3 — LEGITIMATE |0>
    st, resp = make_request("/api/verify", method="POST", data={
        "state": "0", "attack": "NONE", "verifier": "Bob", "shots": 1000, "error_threshold_pct": 10.0, "chi_threshold": 10.0
    })
    pass_t3 = (st == 200 and isinstance(resp, dict) and resp.get("status") == "VALID" and resp.get("threat_detected") is False)
    results["Test 3 (|0> NONE)"] = "PASS" if pass_t3 else "FAIL"
    details["t3"] = {"status": st, "resp": resp}

    # TEST 4 — LEGITIMATE |1>
    st, resp = make_request("/api/verify", method="POST", data={
        "state": "1", "attack": "NONE", "verifier": "Bob", "shots": 1000, "error_threshold_pct": 10.0, "chi_threshold": 10.0
    })
    pass_t4 = (st == 200 and isinstance(resp, dict) and resp.get("status") == "VALID" and resp.get("basis") == "Z")
    results["Test 4 (|1> NONE)"] = "PASS" if pass_t4 else "FAIL"
    details["t4"] = {"status": st, "resp": resp}

    # TEST 5 — LEGITIMATE |+>
    st, resp = make_request("/api/verify", method="POST", data={
        "state": "+", "attack": "NONE", "verifier": "Bob", "shots": 1000, "error_threshold_pct": 10.0, "chi_threshold": 10.0
    })
    pass_t5 = (st == 200 and isinstance(resp, dict) and resp.get("status") == "VALID" and resp.get("basis") == "X")
    results["Test 5 (|+> NONE)"] = "PASS" if pass_t5 else "FAIL"
    details["t5"] = {"status": st, "resp": resp}

    # TEST 6 — LEGITIMATE |->
    st, resp = make_request("/api/verify", method="POST", data={
        "state": "-", "attack": "NONE", "verifier": "Bob", "shots": 1000, "error_threshold_pct": 10.0, "chi_threshold": 10.0
    })
    pass_t6 = (st == 200 and isinstance(resp, dict) and resp.get("status") == "VALID" and resp.get("basis") == "X")
    results["Test 6 (|-> NONE)"] = "PASS" if pass_t6 else "FAIL"
    details["t6"] = {"status": st, "resp": resp}

    # TEST 7 — FORGERY
    st, resp = make_request("/api/verify", method="POST", data={
        "state": "0", "attack": "FORGERY", "verifier": "Bob", "shots": 1000, "error_threshold_pct": 10.0, "chi_threshold": 10.0
    })
    pass_t7 = (st == 200 and isinstance(resp, dict) and resp.get("status") == "THREAT" and resp.get("threat_detected") is True)
    results["Test 7 (Forgery)"] = "PASS" if pass_t7 else "FAIL"
    details["t7"] = {"status": st, "resp": resp}

    # TEST 8 — CHANNEL MANIPULATION
    st, resp = make_request("/api/verify", method="POST", data={
        "state": "+", "attack": "CHANNEL", "verifier": "Bob", "shots": 1000, "error_threshold_pct": 10.0, "chi_threshold": 10.0
    })
    pass_t8 = (st == 200 and isinstance(resp, dict) and resp.get("status") == "THREAT" and resp.get("threat_detected") is True)
    results["Test 8 (Channel)"] = "PASS" if pass_t8 else "FAIL"
    details["t8"] = {"status": st, "resp": resp}

    # TEST 9 — IMPERSONATION
    st, resp = make_request("/api/verify", method="POST", data={
        "state": "0", "attack": "IMPERSONATION", "verifier": "Bob", "shots": 1000, "error_threshold_pct": 10.0, "chi_threshold": 10.0
    })
    pass_t9 = (st == 200 and isinstance(resp, dict) and resp.get("status") == "THREAT" and resp.get("threat_detected") is True)
    results["Test 9 (Impersonation)"] = "PASS" if pass_t9 else "FAIL"
    details["t9"] = {"status": st, "resp": resp}

    # TEST 10 — UNAUTHORIZED VERIFIER
    st, resp = make_request("/api/verify", method="POST", data={
        "state": "0", "attack": "NONE", "verifier": "Eve", "shots": 1000, "error_threshold_pct": 10.0, "chi_threshold": 10.0
    })
    pass_t10 = (st == 200 and isinstance(resp, dict) and resp.get("status") == "BLOCKED" and resp.get("threat_detected") is True)
    results["Test 10 (Unauthorized)"] = "PASS" if pass_t10 else "FAIL"
    details["t10"] = {"status": st, "resp": resp}

    # TEST 11 — REPLAY
    make_request("/api/replay/reset", method="POST")
    replay_body = {
        "state": "0", "attack": "REPLAY", "verifier": "Bob", "shots": 1000, "error_threshold_pct": 10.0, "chi_threshold": 10.0,
        "digital_message": "SIH Replay Test Message", "signature_id": "replay_fixed_sig_001"
    }
    st1, resp1 = make_request("/api/verify", method="POST", data=replay_body)
    st2, resp2 = make_request("/api/verify", method="POST", data=replay_body)
    pass_t11 = (st1 == 200 and resp1.get("status") == "VALID" and st2 == 200 and resp2.get("status") == "THREAT")
    results["Test 11 (Replay)"] = "PASS" if pass_t11 else "FAIL"
    details["t11"] = {"resp1": resp1, "resp2": resp2}

    # TEST 12 — INVALID STATE
    st, resp = make_request("/api/verify", method="POST", data={
        "state": "INVALID", "attack": "NONE", "verifier": "Bob", "shots": 1000, "error_threshold_pct": 10.0, "chi_threshold": 10.0
    })
    pass_t12 = (st == 400)
    results["Test 12 (Invalid State)"] = "PASS" if pass_t12 else "FAIL"
    details["t12"] = {"status": st, "resp": resp}

    # TEST 13 — END-TO-END
    st, resp = make_request("/api/end-to-end")
    pass_t13 = (st == 200 and isinstance(resp, dict))
    results["Test 13 (End-to-End)"] = "PASS" if pass_t13 else "FAIL"
    details["t13"] = {"status": st, "resp": resp}

    # TEST 14 — SECURITY ANALYSIS
    st, resp = make_request("/api/security-analysis")
    pass_t14 = (st == 200 and isinstance(resp, dict))
    results["Test 14 (Security)"] = "PASS" if pass_t14 else "FAIL"
    details["t14"] = {"status": st, "resp": resp}

    # TEST 15 — PERFORMANCE
    st, resp = make_request("/api/performance")
    pass_t15 = (st == 200 and isinstance(resp, dict))
    results["Test 15 (Performance)"] = "PASS" if pass_t15 else "FAIL"
    details["t15"] = {"status": st, "resp": resp}

    # TEST 16 — RESEARCH EVALUATION
    st, resp = make_request("/api/research-evaluation")
    pass_t16 = (st == 200 and isinstance(resp, dict))
    results["Test 16 (Research)"] = "PASS" if pass_t16 else "FAIL"
    details["t16"] = {"status": st, "resp": resp}

    # TEST 17 — MATHEMATICAL MODEL
    st, resp = make_request("/api/mathematical-model")
    pass_t17 = (st == 200 and isinstance(resp, dict))
    results["Test 17 (Mathematical)"] = "PASS" if pass_t17 else "FAIL"
    details["t17"] = {"status": st, "resp": resp}

    # Save detailed dump to scratch json
    with open("c:/Users/ASUS/OneDrive/Desktop/quantum-qds/scratch/live_test_results.json", "w") as f:
        json.dump({"results": results, "details": details}, f, indent=2)

    print(json.dumps({"results": results, "details": details}, indent=2))

if __name__ == "__main__":
    main()
