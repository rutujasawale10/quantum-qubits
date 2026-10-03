import hashlib
import time
import random

# ============================================================
# QDS ATTACK SIMULATION MODULE
# ============================================================

class QDSAttackSimulator:

    def __init__(self):
        self.used_signatures = set()

    # --------------------------------------------------------
    # FORGERY ATTACK
    # --------------------------------------------------------
    def simulate_forgery_attack(self, original_state):
        states = {
            "0": "1",
            "1": "0",
            "+": "-",
            "-": "+"
        }

        forged_state = states.get(original_state, original_state)

        return {
            "attack": "Forgery Attack",
            "original_state": original_state,
            "received_state": forged_state,
            "signature_modified": forged_state != original_state,
            "detected": forged_state != original_state
        }

    # --------------------------------------------------------
    # IMPERSONATION ATTACK
    # --------------------------------------------------------
    def simulate_impersonation_attack(self, legitimate_sender="Alice"):
        attacker_sender = "Attacker"

        return {
            "attack": "Impersonation Attack",
            "expected_sender": legitimate_sender,
            "received_sender": attacker_sender,
            "identity_verified": False,
            "detected": True
        }

    # --------------------------------------------------------
    # REPLAY ATTACK
    # --------------------------------------------------------
    def simulate_replay_attack(self, message, signature_id):
        signature_hash = hashlib.sha256(
            f"{message}:{signature_id}".encode()
        ).hexdigest()

        if signature_hash in self.used_signatures:
            replay_detected = True
        else:
            self.used_signatures.add(signature_hash)
            replay_detected = False

        return {
            "attack": "Replay Attack",
            "message": message,
            "signature_id": signature_id,
            "replay_detected": replay_detected,
            "first_use": not replay_detected,
            "detected": replay_detected
        }

    # --------------------------------------------------------
    # CHANNEL MANIPULATION
    # --------------------------------------------------------
    def simulate_channel_manipulation(
        self,
        original_state,
        manipulation="Z"
    ):
        manipulated_state = original_state

        if manipulation == "X":
            mapping = {
                "0": "1",
                "1": "0",
                "+": "+",
                "-": "-"
            }
            manipulated_state = mapping.get(
                original_state,
                original_state
            )

        elif manipulation == "Z":
            mapping = {
                "0": "0",
                "1": "1",
                "+": "-",
                "-": "+"
            }
            manipulated_state = mapping.get(
                original_state,
                original_state
            )

        return {
            "attack": "Channel Manipulation",
            "original_state": original_state,
            "received_state": manipulated_state,
            "manipulation": manipulation,
            "state_changed": manipulated_state != original_state,
            "detected": manipulated_state != original_state
        }


# ============================================================
# TEST
# ============================================================

if __name__ == "__main__":

    simulator = QDSAttackSimulator()

    print("\n=== QDS ATTACK SIMULATION TEST ===")

    print("\n1. FORGERY")
    print(simulator.simulate_forgery_attack("+"))

    print("\n2. IMPERSONATION")
    print(simulator.simulate_impersonation_attack("Alice"))

    print("\n3. REPLAY - FIRST USE")
    print(simulator.simulate_replay_attack(
        "SIH Quantum Digital Signature",
        "ROUND-001"
    ))

    print("\n3. REPLAY - SECOND USE")
    print(simulator.simulate_replay_attack(
        "SIH Quantum Digital Signature",
        "ROUND-001"
    ))

    print("\n4. CHANNEL MANIPULATION")
    print(simulator.simulate_channel_manipulation("+", "Z"))
