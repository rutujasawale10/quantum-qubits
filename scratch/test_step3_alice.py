"""
Automated Test for STEP 3 — Alice Quantum State Preparation & Statevector Verification
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
    set_alice_quantum_state,
    AliceQuantumStateRequest,
    get_alice_quantum_states,
    reset_alice_session
)
from fastapi import HTTPException


class TestAliceStep3QuantumStatePreparation(unittest.TestCase):

    def setUp(self):
        self.creator = AliceTransactionCreator()
        reset_alice_session()

    def test_01_state_0_preparation(self):
        """Test |0> preparation: default ground state, Z-basis, P(0)=1, P(1)=0."""
        q = self.creator.prepare_quantum_state("0")
        
        self.assertEqual(q["canonical_name"], "0")
        self.assertEqual(q["basis"], "Z")
        self.assertEqual(q["preparation_gates"], [])
        self.assertEqual(q["probabilities"]["0"], 1.0)
        self.assertEqual(q["probabilities"]["1"], 0.0)
        self.assertAlmostEqual(q["statevector"][0]["real"], 1.0)
        self.assertAlmostEqual(q["statevector"][1]["real"], 0.0)
        self.assertTrue(q["is_verified"])
        self.assertEqual(q["verification_status"], "STATE_VERIFIED")
        self.assertEqual(q["preparation_status"], "PREPARED")

    def test_02_state_1_preparation(self):
        """Test |1> preparation: Pauli-X gate, Z-basis, P(0)=0, P(1)=1."""
        q = self.creator.prepare_quantum_state("1")
        
        self.assertEqual(q["canonical_name"], "1")
        self.assertEqual(q["basis"], "Z")
        self.assertEqual(q["preparation_gates"], ["X"])
        self.assertEqual(q["probabilities"]["0"], 0.0)
        self.assertEqual(q["probabilities"]["1"], 1.0)
        self.assertAlmostEqual(q["statevector"][0]["real"], 0.0)
        self.assertAlmostEqual(q["statevector"][1]["real"], 1.0)
        self.assertTrue(q["is_verified"])
        self.assertEqual(q["verification_status"], "STATE_VERIFIED")
        self.assertEqual(q["preparation_status"], "PREPARED")

    def test_03_state_plus_preparation(self):
        """Test |+> preparation: Hadamard gate, X-basis, P(0)=0.5, P(1)=0.5."""
        q = self.creator.prepare_quantum_state("+")
        
        self.assertEqual(q["canonical_name"], "+")
        self.assertEqual(q["basis"], "X")
        self.assertEqual(q["preparation_gates"], ["H"])
        self.assertAlmostEqual(q["probabilities"]["0"], 0.5, places=4)
        self.assertAlmostEqual(q["probabilities"]["1"], 0.5, places=4)
        self.assertAlmostEqual(q["statevector"][0]["real"], 1.0 / math.sqrt(2), places=4)
        self.assertAlmostEqual(q["statevector"][1]["real"], 1.0 / math.sqrt(2), places=4)
        self.assertTrue(q["is_verified"])
        self.assertEqual(q["verification_status"], "STATE_VERIFIED")
        self.assertEqual(q["preparation_status"], "PREPARED")

    def test_04_state_minus_preparation(self):
        """Test |-> preparation: X + H gates, X-basis, P(0)=0.5, P(1)=0.5."""
        q = self.creator.prepare_quantum_state("-")
        
        self.assertEqual(q["canonical_name"], "-")
        self.assertEqual(q["basis"], "X")
        self.assertEqual(q["preparation_gates"], ["X", "H"])
        self.assertAlmostEqual(q["probabilities"]["0"], 0.5, places=4)
        self.assertAlmostEqual(q["probabilities"]["1"], 0.5, places=4)
        self.assertAlmostEqual(q["statevector"][0]["real"], 1.0 / math.sqrt(2), places=4)
        self.assertAlmostEqual(q["statevector"][1]["real"], -1.0 / math.sqrt(2), places=4)
        self.assertTrue(q["is_verified"])
        self.assertEqual(q["verification_status"], "STATE_VERIFIED")
        self.assertEqual(q["preparation_status"], "PREPARED")

    def test_05_invalid_state_rejection(self):
        """Test that invalid quantum states are rejected with clear error."""
        with self.assertRaises(ValueError) as ctx:
            self.creator.prepare_quantum_state("INVALID_STATE")
        self.assertIn("Invalid quantum state", str(ctx.exception))

        with self.assertRaises(ValueError) as ctx:
            self.creator.prepare_quantum_state("|2>")
        self.assertIn("Invalid quantum state", str(ctx.exception))

    def test_06_attach_quantum_state_to_signed_transaction(self):
        """Test attaching quantum state to an existing signed transaction."""
        tx = self.creator.create_transaction("Transfer request: INR 5000", quantum_state="|0>")
        self.assertEqual(tx["status"], "SIGNED")
        self.assertEqual(tx["quantum_state"], "|0>")
        
        # Now update to |+>
        updated = self.creator.set_transaction_quantum_state(tx["transaction_id"], "|+>")
        self.assertEqual(updated["quantum_state"], "|+>")
        self.assertEqual(updated["quantum_basis"], "X")
        self.assertEqual(updated["preparation_status"], "PREPARED")
        self.assertAlmostEqual(updated["probabilities"]["0"], 0.5, places=4)
        self.assertAlmostEqual(updated["probabilities"]["1"], 0.5, places=4)

    def test_07_fastapi_step3_endpoints(self):
        """Test Step 3 FastAPI endpoints."""
        # 1. Get supported quantum states
        states_res = get_alice_quantum_states()
        self.assertEqual(states_res["status"], "SUCCESS")
        self.assertIn("0", states_res["states"])
        self.assertIn("+", states_res["states"])

        # 2. Create transaction with |+> state
        req = AliceTransactionRequest(message="Quantum Token Transfer", quantum_state="|+>")
        res = create_alice_transaction(req)
        self.assertEqual(res["status"], "SUCCESS")
        tx_data = res["transaction"]
        self.assertEqual(tx_data["quantum_state"], "|+>")
        self.assertEqual(tx_data["quantum_basis"], "X")

        # 3. Update quantum state via POST /api/alice/quantum-state
        q_req = AliceQuantumStateRequest(transaction_id=tx_data["transaction_id"], state="|1>")
        q_res = set_alice_quantum_state(q_req)
        self.assertEqual(q_res["status"], "SUCCESS")
        self.assertEqual(q_res["quantum_state"], "|1>")
        self.assertEqual(q_res["basis"], "Z")
        self.assertEqual(q_res["verification_status"], "STATE_VERIFIED")


if __name__ == "__main__":
    unittest.main(verbosity=2)
