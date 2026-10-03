"""
Automated Test for STEP 5 — Alice Bell-State Entanglement & 3-Qubit Quantum Teleportation
SIH26141 / Q-SHIELD
"""

import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import math
import unittest
from alice_sender import AliceTransactionCreator, normalize_state_name
from api import (
    app,
    create_alice_transaction,
    AliceTransactionRequest,
    teleport_alice_transaction,
    AliceTeleportRequest,
    get_alice_bell_state,
    get_alice_teleportation_details,
    reset_alice_session
)
from fastapi import HTTPException


class TestAliceStep5BellAndTeleportation(unittest.TestCase):

    def setUp(self):
        self.creator = AliceTransactionCreator()
        reset_alice_session()

    def test_01_bell_state_preparation(self):
        """Test Bell state |Φ+> generation, circuit, and statevector."""
        bell = self.creator.generate_bell_state()
        self.assertEqual(bell["bell_state"], "|Φ+>")
        self.assertTrue(bell["is_verified"])
        self.assertEqual(bell["verification_status"], "BELL_STATE_VERIFIED")
        self.assertAlmostEqual(bell["fidelity"], 1.0, places=4)
        self.assertIn("H", bell["circuit_ascii"])
        self.assertIn("X", bell["circuit_ascii"])

    def test_02_bell_state_probabilities(self):
        """Test Bell state theoretical probabilities: P(00)=0.5, P(11)=0.5, P(01)=0, P(10)=0."""
        bell = self.creator.generate_bell_state()
        probs = bell["probabilities"]
        self.assertAlmostEqual(probs["00"], 0.5, places=4)
        self.assertAlmostEqual(probs["11"], 0.5, places=4)
        self.assertAlmostEqual(probs["01"], 0.0, places=4)
        self.assertAlmostEqual(probs["10"], 0.0, places=4)

    def test_03_teleportation_state_0(self):
        """Test 3-qubit teleportation for |0> ground state."""
        res = self.creator.run_3qubit_teleportation("0")
        self.assertEqual(res["input_state"], "|0>")
        self.assertEqual(res["receiver_state"], "|0>")
        self.assertEqual(res["num_qubits"], 3)
        self.assertEqual(res["bell_state"], "|Φ+>")
        self.assertTrue(res["is_verified"])
        self.assertEqual(res["verification"], "TELEPORTATION_VERIFIED")
        self.assertGreaterEqual(res["fidelity"], 0.9999)
        self.assertEqual(res["receiver_probabilities"]["0"], 1.0)
        self.assertEqual(res["receiver_probabilities"]["1"], 0.0)

    def test_04_teleportation_state_1(self):
        """Test 3-qubit teleportation for |1> excited state."""
        res = self.creator.run_3qubit_teleportation("1")
        self.assertEqual(res["input_state"], "|1>")
        self.assertEqual(res["receiver_state"], "|1>")
        self.assertTrue(res["is_verified"])
        self.assertEqual(res["verification"], "TELEPORTATION_VERIFIED")
        self.assertGreaterEqual(res["fidelity"], 0.9999)
        self.assertEqual(res["receiver_probabilities"]["0"], 0.0)
        self.assertEqual(res["receiver_probabilities"]["1"], 1.0)

    def test_05_teleportation_state_plus(self):
        """Test 3-qubit teleportation for |+> superposition state."""
        res = self.creator.run_3qubit_teleportation("+")
        self.assertEqual(res["input_state"], "|+>")
        self.assertEqual(res["receiver_state"], "|+>")
        self.assertTrue(res["is_verified"])
        self.assertEqual(res["verification"], "TELEPORTATION_VERIFIED")
        self.assertGreaterEqual(res["fidelity"], 0.9999)
        self.assertAlmostEqual(res["receiver_probabilities"]["0"], 0.5, places=4)
        self.assertAlmostEqual(res["receiver_probabilities"]["1"], 0.5, places=4)

    def test_06_teleportation_state_minus(self):
        """Test 3-qubit teleportation for |-> superposition state."""
        res = self.creator.run_3qubit_teleportation("-")
        self.assertEqual(res["input_state"], "|->")
        self.assertEqual(res["receiver_state"], "|->")
        self.assertTrue(res["is_verified"])
        self.assertEqual(res["verification"], "TELEPORTATION_VERIFIED")
        self.assertGreaterEqual(res["fidelity"], 0.9999)
        self.assertAlmostEqual(res["receiver_probabilities"]["0"], 0.5, places=4)
        self.assertAlmostEqual(res["receiver_probabilities"]["1"], 0.5, places=4)

    def test_07_receiver_state_equivalence_and_fidelity_threshold(self):
        """Test all 4 states exceed the fidelity threshold >= 0.9999."""
        for state in ["0", "1", "+", "-"]:
            res = self.creator.run_3qubit_teleportation(state)
            self.assertGreaterEqual(res["fidelity"], 0.9999, f"Fidelity check failed for state {state}")
            self.assertEqual(res["verification"], "TELEPORTATION_VERIFIED")

    def test_08_transaction_teleportation_workflow(self):
        """Test full workflow: transaction -> sign -> quantum prep -> teleportation."""
        tx = self.creator.create_transaction("Authorize INR 10,000", quantum_state="|+>")
        self.assertEqual(tx["status"], "SIGNED")
        self.assertEqual(tx["quantum_verification"], "STATE_VERIFIED")
        self.assertEqual(tx["transmission_status"], "READY")
        self.assertIn("teleportation", tx)
        self.assertEqual(tx["teleportation"]["verification"], "TELEPORTATION_VERIFIED")

        # Explicit teleport execution
        res = self.creator.teleport_transaction(tx["transaction_id"])
        self.assertEqual(res["transaction_id"], tx["transaction_id"])
        self.assertEqual(res["input_state"], "|+>")
        self.assertEqual(res["receiver_state"], "|+>")
        self.assertEqual(res["verification"], "TELEPORTATION_VERIFIED")
        self.assertGreaterEqual(res["fidelity"], 0.9999)

    def test_09_invalid_transaction_rejection(self):
        """Test that non-existent transaction is rejected with clear error."""
        with self.assertRaises(ValueError) as ctx:
            self.creator.teleport_transaction("TX-DOES-NOT-EXIST")
        self.assertIn("does not exist", str(ctx.exception))

    def test_10_unsigned_transaction_rejection(self):
        """Test that unsigned transaction is rejected from teleportation."""
        tx = self.creator.create_transaction("Unsigned msg", auto_sign=False, quantum_state="0")
        with self.assertRaises(ValueError) as ctx:
            self.creator.teleport_transaction(tx["transaction_id"])
        self.assertIn("is not signed", str(ctx.exception))

    def test_11_private_key_remains_protected(self):
        """Test that Alice's private signing key is never exposed in teleportation metadata or session records."""
        tx = self.creator.create_transaction("Confidential transfer", quantum_state="|+>")
        res = self.creator.teleport_transaction(tx["transaction_id"])
        
        # Check dictionary keys
        keys_str = str(res)
        self.assertNotIn("_private_key", keys_str)
        self.assertNotIn("private_key", keys_str)
        self.assertIn("public_key_fingerprint", str(tx))

    def test_12_fastapi_step5_endpoints(self):
        """Test FastAPI endpoints for Step 5: POST /api/alice/teleport and GET /api/alice/bell-state."""
        # 1. Bell state endpoint
        bell_res = get_alice_bell_state()
        self.assertEqual(bell_res["status"], "SUCCESS")
        self.assertEqual(bell_res["bell_state"]["bell_state"], "|Φ+>")

        # 2. Create transaction
        req = AliceTransactionRequest(message="Teleportation Test Payload", quantum_state="|->")
        create_res = create_alice_transaction(req)
        tx_id = create_res["transaction"]["transaction_id"]

        # 3. Call POST /api/alice/teleport
        t_req = AliceTeleportRequest(transaction_id=tx_id)
        t_res = teleport_alice_transaction(t_req)
        self.assertEqual(t_res["status"], "SUCCESS")
        self.assertEqual(t_res["verification"], "TELEPORTATION_VERIFIED")
        self.assertGreaterEqual(t_res["fidelity"], 0.9999)

        # 4. Call GET /api/alice/teleport/{transaction_id}
        get_res = get_alice_teleportation_details(tx_id)
        self.assertEqual(get_res["status"], "SUCCESS")
        self.assertEqual(get_res["teleportation"]["verification"], "TELEPORTATION_VERIFIED")


if __name__ == "__main__":
    unittest.main(verbosity=2)
