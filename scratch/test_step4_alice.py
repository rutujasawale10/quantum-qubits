"""
Automated Test for STEP 4 — Alice Quantum Transmission Preparation & Egress Packet
SIH26141 / Q-SHIELD
"""

import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import unittest
from alice_sender import AliceTransactionCreator, normalize_state_name
from api import (
    app,
    create_alice_transaction,
    AliceTransactionRequest,
    prepare_alice_transmission,
    AliceTransmissionPrepareRequest,
    get_alice_transmission_packet,
    set_alice_quantum_state,
    AliceQuantumStateRequest,
    reset_alice_session
)
from fastapi import HTTPException


class TestAliceStep4TransmissionPreparation(unittest.TestCase):

    def setUp(self):
        self.creator = AliceTransactionCreator()
        reset_alice_session()

    def test_01_valid_signed_and_prepared_transaction_ready(self):
        """Test that a valid signed & prepared transaction prepares a READY transmission packet."""
        tx = self.creator.create_transaction("Transfer request: INR 5000", quantum_state="|+>")
        self.assertEqual(tx["status"], "SIGNED")
        self.assertEqual(tx["quantum_verification"], "STATE_VERIFIED")
        self.assertEqual(tx["transmission_status"], "READY")

        # Explicitly prepare packet via method
        res = self.creator.prepare_transmission_packet(tx["transaction_id"])
        self.assertEqual(res["transmission_status"], "READY")
        self.assertEqual(res["quantum_state"], "|+>")
        self.assertEqual(res["quantum_basis"], "X")
        self.assertEqual(res["signature_status"], "VERIFIED")
        self.assertEqual(res["quantum_verification"], "STATE_VERIFIED")
        
        packet = res["transmission_packet"]
        self.assertIsNotNone(packet)
        self.assertEqual(packet["transaction_id"], tx["transaction_id"])
        self.assertEqual(packet["sender"], "Alice")
        self.assertEqual(packet["receiver"], "Bob")
        self.assertEqual(packet["transmission_status"], "READY")

    def test_02_missing_transaction_rejection(self):
        """Test that preparing transmission for a non-existent transaction is rejected."""
        with self.assertRaises(ValueError) as ctx:
            self.creator.prepare_transmission_packet("TX-NON-EXISTENT")
        self.assertIn("does not exist", str(ctx.exception))

    def test_03_unsigned_transaction_rejection(self):
        """Test that an unsigned transaction is rejected from transmission preparation."""
        # Create unsigned transaction
        tx = self.creator.create_transaction("Unsigned message", auto_sign=False, quantum_state="0")
        self.assertEqual(tx["status"], "CREATED")
        self.assertIsNone(tx["signature"])

        with self.assertRaises(ValueError) as ctx:
            self.creator.prepare_transmission_packet(tx["transaction_id"])
        self.assertIn("is not signed", str(ctx.exception))

    def test_04_unprepared_quantum_state_rejection(self):
        """Test that transaction with missing quantum state preparation is rejected."""
        tx = self.creator.create_transaction("Valid message", auto_sign=True, quantum_state="0")
        # Artificially alter quantum preparation status to test validation guard
        tx["preparation_status"] = "UNPREPARED"
        
        with self.assertRaises(ValueError) as ctx:
            self.creator.prepare_transmission_packet(tx["transaction_id"])
        self.assertIn("Quantum state is not prepared", str(ctx.exception))

    def test_05_invalid_quantum_verification_rejection(self):
        """Test that transaction with failed quantum state verification is rejected."""
        tx = self.creator.create_transaction("Valid message", auto_sign=True, quantum_state="1")
        # Artificially fail quantum verification
        tx["quantum_verification"] = "VERIFICATION_FAILED"

        with self.assertRaises(ValueError) as ctx:
            self.creator.prepare_transmission_packet(tx["transaction_id"])
        self.assertIn("Quantum state is not verified", str(ctx.exception))

    def test_06_packet_contains_all_required_fields(self):
        """Test that the transmission packet contains all mandatory fields."""
        tx = self.creator.create_transaction("Authorize smart contract", quantum_state="|->")
        res = self.creator.prepare_transmission_packet(tx["transaction_id"])
        packet = res["transmission_packet"]

        required_fields = [
            "transaction_id",
            "message",
            "sender",
            "receiver",
            "timestamp",
            "message_hash",
            "signature",
            "signature_algorithm",
            "public_key_fingerprint",
            "quantum_state",
            "quantum_state_label",
            "quantum_basis",
            "statevector",
            "probabilities",
            "preparation_gates",
            "circuit_ascii",
            "quantum_verification",
            "preparation_status",
            "transmission_status"
        ]

        for field in required_fields:
            self.assertIn(field, packet, f"Missing required field in transmission packet: {field}")
            self.assertIsNotNone(packet[field], f"Field {field} should not be None")

        self.assertEqual(packet["quantum_verification"], "STATE_VERIFIED")
        self.assertEqual(packet["preparation_status"], "PREPARED")
        self.assertEqual(packet["transmission_status"], "READY")
        self.assertEqual(packet["sender"], "Alice")
        self.assertEqual(packet["receiver"], "Bob")
        self.assertEqual(packet["quantum_state"], "|->")
        self.assertEqual(packet["quantum_basis"], "X")

    def test_07_fastapi_step4_endpoints(self):
        """Test Step 4 FastAPI endpoints: POST /api/alice/transmission/prepare and GET /api/alice/transmission/{id}."""
        # 1. Create transaction via API
        create_req = AliceTransactionRequest(message="FastAPI Step 4 Payload", quantum_state="|+>")
        create_res = create_alice_transaction(create_req)
        tx_id = create_res["transaction"]["transaction_id"]

        # 2. Call POST /api/alice/transmission/prepare
        prep_req = AliceTransmissionPrepareRequest(transaction_id=tx_id)
        prep_res = prepare_alice_transmission(prep_req)
        
        self.assertEqual(prep_res["status"], "SUCCESS")
        self.assertEqual(prep_res["transaction_id"], tx_id)
        self.assertEqual(prep_res["transmission_status"], "READY")
        self.assertEqual(prep_res["signature_status"], "VERIFIED")
        self.assertEqual(prep_res["quantum_verification"], "STATE_VERIFIED")

        # 3. Call GET /api/alice/transmission/{transaction_id}
        get_res = get_alice_transmission_packet(tx_id)
        self.assertEqual(get_res["status"], "SUCCESS")
        self.assertEqual(get_res["transaction_id"], tx_id)
        self.assertEqual(get_res["transmission_packet"]["transmission_status"], "READY")

        # 4. Test error handling on missing transaction
        invalid_req = AliceTransmissionPrepareRequest(transaction_id="TX-INVALID-9999")
        with self.assertRaises(HTTPException) as ctx:
            prepare_alice_transmission(invalid_req)
        self.assertEqual(ctx.exception.status_code, 400)


if __name__ == "__main__":
    unittest.main(verbosity=2)
