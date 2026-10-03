"""
Automated Test for STEP 1 — Alice Transaction Creator
"""

import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import unittest
from alice_sender import AliceTransactionCreator
from api import app, create_alice_transaction, AliceTransactionRequest, get_alice_transactions, get_alice_next_id, reset_alice_session
from fastapi import HTTPException


class TestAliceTransactionCreator(unittest.TestCase):

    def setUp(self):
        self.creator = AliceTransactionCreator()
        reset_alice_session()

    def test_01_create_valid_transaction(self):
        """Test creating a valid transaction."""
        tx = self.creator.create_transaction("Transfer request: INR 5000")
        self.assertIn("TX-", tx["transaction_id"])
        self.assertEqual(tx["message"], "Transfer request: INR 5000")
        self.assertEqual(tx["sender"], "Alice")
        self.assertEqual(tx["receiver"], "Bob")
        self.assertIn(tx["status"], ["CREATED", "SIGNED"])
        self.assertTrue(bool(tx["timestamp"]))
        self.assertEqual(len(self.creator.get_all_transactions()), 1)

    def test_02_empty_message_validation(self):
        """Test that empty messages are rejected with clear error."""
        with self.assertRaises(ValueError) as ctx:
            self.creator.create_transaction("")
        self.assertIn("Message cannot be empty", str(ctx.exception))

        with self.assertRaises(ValueError) as ctx:
            self.creator.create_transaction("   \n\t  ")
        self.assertIn("Message cannot be empty", str(ctx.exception))

    def test_03_sender_and_receiver_validation(self):
        """Test sender must be Alice and receiver must be Bob."""
        with self.assertRaises(ValueError) as ctx:
            self.creator.create_transaction("Test message", sender="Eve")
        self.assertIn("Sender must remain 'Alice'", str(ctx.exception))

        with self.assertRaises(ValueError) as ctx:
            self.creator.create_transaction("Test message", receiver="Mallory")
        self.assertIn("Receiver must remain 'Bob'", str(ctx.exception))

    def test_04_unique_transaction_ids(self):
        """Test automatic generation of distinct unique transaction IDs."""
        tx1 = self.creator.create_transaction("Message 1")
        tx2 = self.creator.create_transaction("Message 2")
        tx3 = self.creator.create_transaction("Message 3")

        self.assertNotEqual(tx1["transaction_id"], tx2["transaction_id"])
        self.assertNotEqual(tx2["transaction_id"], tx3["transaction_id"])
        self.assertEqual(len(self.creator.get_all_transactions()), 3)

    def test_05_duplicate_custom_id_rejected(self):
        """Test that duplicate transaction IDs are rejected."""
        self.creator.create_transaction("First message", transaction_id="TX-CUSTOM-001")
        with self.assertRaises(ValueError) as ctx:
            self.creator.create_transaction("Duplicate ID message", transaction_id="TX-CUSTOM-001")
        self.assertIn("already exists", str(ctx.exception))

    def test_06_fastapi_endpoints(self):
        """Test FastAPI Alice handler functions."""
        # 1. Next ID
        next_id_res = get_alice_next_id()
        self.assertEqual(next_id_res["status"], "SUCCESS")
        self.assertIn("TX-", next_id_res["next_transaction_id"])

        # 2. Create Transaction via endpoint
        req = AliceTransactionRequest(message="FastAPI Test Payment")
        res = create_alice_transaction(req)
        self.assertEqual(res["status"], "SUCCESS")
        self.assertEqual(res["transaction"]["message"], "FastAPI Test Payment")
        self.assertIn(res["transaction"]["status"], ["CREATED", "SIGNED"])

        # 3. Get transactions list
        tx_list = get_alice_transactions()
        self.assertEqual(tx_list["status"], "SUCCESS")
        self.assertTrue(len(tx_list["transactions"]) >= 1)

        # 4. Error handling via endpoint
        bad_req = AliceTransactionRequest(message="   ")
        with self.assertRaises(HTTPException) as ctx:
            create_alice_transaction(bad_req)
        self.assertEqual(ctx.exception.status_code, 400)


if __name__ == "__main__":
    unittest.main(verbosity=2)
