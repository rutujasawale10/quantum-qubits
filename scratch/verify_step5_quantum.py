"""
Step 5 Quantum Verification Script — Bell State + 3-Qubit Teleportation
"""
import sys
import json
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.path.insert(0, r'c:\Users\ASUS\OneDrive\Desktop\quantum-qds')
from alice_sender import AliceTransactionCreator

a = AliceTransactionCreator()

print('=== A. BELL STATE VERIFICATION ===')
bell = a.generate_bell_state()
print('Bell State Label     :', bell['bell_state'])
print('Bell State Verified  :', bell['bell_state_verified'])
probs = bell['probabilities']
print('P(|00>)              :', probs.get('00', 'N/A'))
print('P(|11>)              :', probs.get('11', 'N/A'))
print('P(|01>)              :', probs.get('01', 'N/A'))
print('P(|10>)              :', probs.get('10', 'N/A'))
print()

print('=== B. 3-QUBIT TELEPORTATION — ALL 4 INPUT STATES ===')
print(f"{'Input':<8} {'Receiver':<12} {'Fidelity':<12} {'Status'}")
print('-' * 55)
for state_key in ['0', '1', '+', '-']:
    result = a.run_3qubit_teleportation(state_key)
    tel = result['teleportation']
    inp = tel.get('input_state', f'|{state_key}>')
    rec = tel.get('receiver_state_label', '?')
    fid = tel.get('fidelity', 0.0)
    ver = tel.get('verification', '?')
    status = 'PASS' if fid >= 0.9999 else 'FAIL'
    print(f"|{state_key}>{' ':<5} {rec:<12} {fid:<12.7f} {ver} [{status}]")

print()
print('=== C. QISKIT VERSION ===')
try:
    import qiskit
    print('Qiskit version:', qiskit.__version__)
except Exception as e:
    print('Qiskit import error:', e)

print()
print('=== D. PRIVATE KEY PROTECTION ===')
tx = a.create_transaction('Step 5 Verification Test', quantum_state='+')
tx_id = tx['transaction_id']
a.sign_transaction(tx_id)
a.set_transaction_quantum_state(tx_id, '+')
a.prepare_transmission_packet(tx_id)
tele_result = a.teleport_transaction(tx_id)
tele_str = json.dumps(tele_result)
if 'private_key' in tele_str.lower() or '-----BEGIN' in tele_str:
    print('FAIL: Private key may be exposed in teleportation result!')
else:
    print('PASS: Private key NOT exposed in teleportation result.')

rec_str = json.dumps(list(a._session.values()))
if 'private_key' in rec_str.lower() or '-----BEGIN' in rec_str:
    print('FAIL: Private key may be in session records!')
else:
    print('PASS: Private key NOT in session records.')

print()
print('=== E. SUMMARY ===')
all_fid_ok = True
for state_key in ['0', '1', '+', '-']:
    result = a.run_3qubit_teleportation(state_key)
    fid = result['teleportation']['fidelity']
    if fid < 0.9999:
        all_fid_ok = False

bell_ok = bell['bell_state_verified'] and abs(probs.get('00', 0) - 0.5) < 0.01 and abs(probs.get('11', 0) - 0.5) < 0.01
if bell_ok and all_fid_ok:
    print('ALL CHECKS PASSED. STEP 5 VERIFIED.')
else:
    print('SOME CHECKS FAILED. Review above output.')
