"""
Automated Test for STEP 2 — Alice Message Hash + Digital Signature
"""

import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import hashlib
import unittest
from alice_sender import AliceTransactionCreator
from api import (
    app,
    create_alice_transaction,
    AliceTransactionRequest,
    sign_alice_transaction,
    AliceSignRequest,
    verify_alice_signature,
    AliceVerifySignatureRequest,
    get_alice_public_key,
    reset_alice_session
)
from fastapi import HTTPException


class TestAliceStep2HashAndSignature(unittest.TestCase):

    def setUp(self):
        self.creator = AliceTransactionCreator()
        reset_alice_session()

    def test_01_sha256_deterministic_and_accurate(self):
        """Test SHA-256 hashing produces exact mathematical digest."""
        message = "Transfer request: INR 5000"
        expected_hash = hashlib.sha256(message.encode("utf-8")).hexdigest()
        actual_hash = self.creator.compute_message_hash(message)
        
        self.assertEqual(actual_hash, expected_hash)
        self.assertEqual(len(actual_hash), 64)
        
        # Test known NIST/RFC vector: SHA-256("abc") = ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad
        self.assertEqual(
            self.creator.compute_message_hash("abc"),
            "ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad"
        )

    def test_02_sha256_avalanche_and_sensitivity(self):
        """Test that changing a single character completely alters the hash."""
        msg1 = "Transfer request: INR 5000"
        msg2 = "Transfer request: INR 5001"
        h1 = self.creator.compute_message_hash(msg1)
        h2 = self.creator.compute_message_hash(msg2)
        
        self.assertNotEqual(h1, h2)

    def test_03_canonical_payload_determinism(self):
        """Test canonical serialization formatting."""
        payload = self.creator.build_canonical_signing_payload(
            transaction_id="TX-2026-0001",
            sender="Alice",
            receiver="Bob",
            timestamp="2026-09-27T16:00:00Z",
            message_hash="2c26b46b68ffc68ff99b453c1d30413413422d706483bfa0f98a5e886266e7ae"
        )
        expected = "TX-2026-0001|Alice|Bob|2026-09-27T16:00:00Z|2c26b46b68ffc68ff99b453c1d30413413422d706483bfa0f98a5e886266e7ae"
        self.assertEqual(payload, expected)

    def test_04_create_signed_transaction_structure(self):
        """Test creating a transaction produces full signed record without exposing private key."""
        tx = self.creator.create_transaction("Authorize Contract #402")
        
        self.assertEqual(tx["status"], "SIGNED")
        self.assertIn("TX-", tx["transaction_id"])
        self.assertEqual(tx["message"], "Authorize Contract #402")
        self.assertEqual(tx["sender"], "Alice")
        self.assertEqual(tx["receiver"], "Bob")
        self.assertTrue(bool(tx["timestamp"]))
        self.assertEqual(len(tx["message_hash"]), 64)
        self.assertTrue(bool(tx["signature"]))
        self.assertIn("ECDSA-SHA256", tx["signature_algorithm"])
        self.assertIn("ALICE-PUB-", tx["public_key_fingerprint"])
        self.assertIn("canonical_payload", tx)
        
        # Security Boundary Assertion: Private key is NEVER in the record
        self.assertNotIn("_private_key", tx)
        self.assertNotIn("private_key", tx)
        self.assertNotIn("priv_key", tx)

    def test_05_signature_verification_positive(self):
        """Test local signature verification on valid untampered transaction."""
        tx = self.creator.create_transaction("Transfer request: INR 5000")
        is_valid, details = self.creator.verify_transaction_signature(tx)
        
        self.assertTrue(is_valid)
        self.assertIn("VALID", details)

    def test_06_signature_verification_negative_tampered_message(self):
        """Test signature verification fails when message is tampered."""
        tx = self.creator.create_transaction("Transfer request: INR 5000")
        
        tampered_tx = dict(tx)
        tampered_tx["message"] = "Transfer request: INR 999999" # Modified payload
        
        is_valid, details = self.creator.verify_transaction_signature(tampered_tx)
        self.assertFalse(is_valid)

    def test_07_signature_verification_negative_tampered_route_or_id(self):
        """Test signature verification fails if transaction_id or route is tampered."""
        tx = self.creator.create_transaction("Transfer request: INR 5000")
        
        # Tamper receiver to Eve
        tampered_receiver = dict(tx)
        tampered_receiver["receiver"] = "Eve"
        is_valid, _ = self.creator.verify_transaction_signature(tampered_receiver)
        self.assertFalse(is_valid)

        # Tamper transaction ID
        tampered_id = dict(tx)
        tampered_id["transaction_id"] = "TX-FORGED-9999"
        is_valid_id, _ = self.creator.verify_transaction_signature(tampered_id)
        self.assertFalse(is_valid_id)

    def test_08_fastapi_step2_endpoints(self):
        """Test Step 2 FastAPI endpoints."""
        # 1. Public key endpoint
        pk_res = get_alice_public_key()
        self.assertEqual(pk_res["status"], "SUCCESS")
        self.assertIn("ALICE-PUB-", pk_res["public_key"]["fingerprint"])
        self.assertNotIn("private", str(pk_res).lower())

        # 2. Create and auto-sign transaction endpoint
        req = AliceTransactionRequest(message="API Payment Request INR 2500")
        res = create_alice_transaction(req)
        self.assertEqual(res["status"], "SUCCESS")
        tx_data = res["transaction"]
        self.assertEqual(tx_data["status"], "SIGNED")
        self.assertEqual(len(tx_data["message_hash"]), 64)
        self.assertTrue(bool(tx_data["signature"]))
        self.assertNotIn("private", str(res).lower())

        # 3. Verify signature endpoint
        v_req = AliceVerifySignatureRequest(transaction=tx_data)
        v_res = verify_alice_signature(v_req)
        self.assertEqual(v_res["status"], "SUCCESS")
        self.assertTrue(v_res["valid"])

        # 4. Verify signature on tampered payload endpoint
        bad_tx = dict(tx_data)
        bad_tx["message"] = "Tampered Content"
        bad_v_req = AliceVerifySignatureRequest(transaction=bad_tx)
        bad_v_res = verify_alice_signature(bad_v_req)
        self.assertEqual(bad_v_res["status"], "SUCCESS")
        self.assertFalse(bad_v_res["valid"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
