"""Definitive Step 5 Verification — Bell State + 3-Qubit Teleportation via live API."""
import urllib.request
import json
import qiskit

BASE = "http://127.0.0.1:8000"


def get(endpoint):
    return json.loads(urllib.request.urlopen(BASE + endpoint).read())


def post(endpoint, payload):
    data = json.dumps(payload).encode()
    req = urllib.request.Request(BASE + endpoint, data=data, headers={"Content-Type": "application/json"})
    return json.loads(urllib.request.urlopen(req).read())


print("=== A. BELL STATE (Qiskit Simulation) ===")
resp = get("/api/alice/bell-state")
bell = resp["bell_state"]
probs = bell["probabilities"]
print("Bell State :", bell["bell_state"])
print("Formula    :", bell["formula"])
print("Verified   :", bell["is_verified"], "/", bell["verification_status"])
print("Fidelity   :", bell["fidelity"])
print("P(|00>)    :", probs["00"])
print("P(|11>)    :", probs["11"])
print("P(|01>)    :", probs["01"])
print("P(|10>)    :", probs["10"])
print("Statevector:")
for sv in bell["statevector"]:
    print("  ", sv["basis_state"], ":", sv["str"])

print()
print("=== B. 3-QUBIT TELEPORTATION — ALL 4 INPUT STATES ===")
all_pass = True
for state in ["0", "1", "+", "-"]:
    tx_r = post("/api/alice/transaction", {
        "message": "Step5 verify " + state,
        "sender": "Alice",
        "receiver": "Bob",
        "quantum_state": state
    })
    tid = tx_r["transaction"]["transaction_id"]
    tel_r = post("/api/alice/teleport", {"transaction_id": tid})
    tel = tel_r["teleportation"]
    fid = tel["fidelity"]
    rec = tel.get("receiver_state_label", tel.get("receiver_state", "?"))
    ver = tel["verification"]
    ok = fid >= 0.9999
    if not ok:
        all_pass = False
    status_str = "PASS" if ok else "FAIL"
    rprobs = tel.get("receiver_probabilities", {})
    p0 = rprobs.get("0", rprobs.get(0, "?"))
    p1 = rprobs.get("1", rprobs.get(1, "?"))
    bell_st = tel_r.get("bell_state", "?")
    bell_ver = tel_r.get("bell_state_verified", "?")
    print("|" + state + "> -> " + str(rec) + "  Fidelity: " + str(round(fid, 10)) + "  [" + status_str + "]  " + str(ver))
    print("   Bell: " + str(bell_st) + " (verified=" + str(bell_ver) + ")   P(0)=" + str(p0) + "  P(1)=" + str(p1))

print()
print("=== C. QISKIT VERSION ===")
print("Qiskit:", qiskit.__version__)

print()
print("=== D. PRIVATE KEY PROTECTION ===")
pk_resp = get("/api/alice/public-key")
pk_str = json.dumps(pk_resp)
if "BEGIN PRIVATE KEY" in pk_str or "BEGIN EC PRIVATE KEY" in pk_str:
    print("FAIL: Private key (PRIVATE) exposed!")
elif "BEGIN PUBLIC KEY" in pk_str:
    print("PASS: Only PUBLIC key PEM exposed (intentional design).")
print("Fingerprint:", pk_resp.get("public_key", {}).get("fingerprint", "N/A"))

tx2 = post("/api/alice/transaction", {"message": "key check", "sender": "Alice", "receiver": "Bob", "quantum_state": "+"})
tid2 = tx2["transaction"]["transaction_id"]
tel2 = post("/api/alice/teleport", {"transaction_id": tid2})
tel2_str = json.dumps(tel2)
if "BEGIN PRIVATE" in tel2_str or "BEGIN EC PRIVATE" in tel2_str:
    print("FAIL: Private key in teleportation response!")
else:
    print("PASS: Private key NOT in teleportation API response.")

print()
print("=== FINAL VERDICT ===")
bell_ok = (abs(probs["00"] - 0.5) < 0.01 and abs(probs["11"] - 0.5) < 0.01 and
           abs(probs["01"]) < 0.01 and abs(probs["10"]) < 0.01)
if bell_ok and all_pass:
    print("STEP 5 VERIFIED - ALICE QUANTUM TELEPORTATION ENGINE")
else:
    print("FAILED - bell_ok=" + str(bell_ok) + ", all_pass=" + str(all_pass))
