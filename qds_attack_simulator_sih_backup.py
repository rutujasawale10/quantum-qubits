import hashlib
import time
import random

# ============================================================
# QDS ATTACK SIMULATION MODULE
# ============================================================

class QDSAttackSimulator:

    def __init__(self):
        # Local set as fallback; primary replay set is maintained in st.session_state
        self.used_signatures = set()

    # --------------------------------------------------------
    # 1. FORGERY ATTACK
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
    # 2. IMPERSONATION ATTACK
    # --------------------------------------------------------
    def simulate_impersonation_attack(self, legitimate_sender="Alice", attacker_sender="Attacker"):
        identity_verified = (legitimate_sender == attacker_sender)
        
        return {
            "attack": "Impersonation Attack",
            "expected_sender": legitimate_sender,
            "received_sender": attacker_sender,
            "identity_verified": identity_verified,
            "detected": not identity_verified
        }

    # --------------------------------------------------------
    # 3. REPLAY ATTACK
    # --------------------------------------------------------
    def simulate_replay_attack(self, message, signature_id, session_used_signatures=None):
        target_set = session_used_signatures if session_used_signatures is not None else self.used_signatures
        
        signature_hash = hashlib.sha256(
            f"{message}:{signature_id}".encode()
        ).hexdigest()

        if signature_hash in target_set:
            replay_detected = True
            previously_seen = True
        else:
            target_set.add(signature_hash)
            replay_detected = False
            previously_seen = False

        return {
            "attack": "Replay Attack",
            "message": message,
            "signature_id": signature_id,
            "replay_hash": signature_hash,
            "replay_detected": replay_detected,
            "previously_seen": previously_seen,
            "first_use": not replay_detected,
            "detected": replay_detected
        }

    # --------------------------------------------------------
    # 4. CHANNEL MANIPULATION
    # --------------------------------------------------------
    def simulate_channel_manipulation(
        self,
        original_state,
        manipulation="Z",
        basis="Z"
    ):
        manipulated_state = original_state

        if manipulation == "X":
            mapping = {
                "0": "1",
                "1": "0",
                "+": "+",
                "-": "-"
            }
            manipulated_state = mapping.get(original_state, original_state)

        elif manipulation == "Z":
            mapping = {
                "0": "0",
                "1": "1",
                "+": "-",
                "-": "+"
            }
            manipulated_state = mapping.get(original_state, original_state)

        state_changed = (manipulated_state != original_state)
        
        # Determine theoretical quantum invisibility
        invisible = False
        invisibility_reason = ""
        if manipulation == "X" and basis == "X":
            invisible = True
            invisibility_reason = f"X|{original_state}> = |{original_state}> (up to global phase). The Pauli-X operation leaves the measured state unchanged in the X basis."
        elif manipulation == "Z" and basis == "Z":
            invisible = True
            invisibility_reason = f"Z|{original_state}> = |{original_state}> (up to global phase). The Pauli-Z operation leaves the measured state unchanged in the Z basis."

        return {
            "attack": "Channel Manipulation",
            "original_state": original_state,
            "received_state": manipulated_state,
            "manipulation": manipulation,
            "state_changed": state_changed,
            "invisible": invisible,
            "invisibility_reason": invisibility_reason,
            "detected": state_changed and not invisible
        }

    # --------------------------------------------------------
    # ATTACK ANALYSIS EXPLANATION GENERATOR
    # --------------------------------------------------------
    def get_attack_explanation(self, attack_type, details, chi_square, threshold, threat_detected):
        if attack_type == "NONE":
            return "Genuine scenario: No attack was injected. The received quantum signature matches the expected distribution."
        
        elif attack_type == "FORGERY":
            orig = details.get("original_state", "")
            recv = details.get("received_state", "")
            return (
                f"The received quantum state (|{recv}>) differs from the original signed state (|{orig}>). "
                f"The quantum measurement distribution therefore deviates significantly from the expected signature distribution."
            )
            
        elif attack_type == "IMPERSONATION":
            exp = details.get("expected_sender", "Alice")
            recv = details.get("received_sender", "Attacker")
            return (
                f"The received sender identity ('{recv}') does not match the expected legitimate sender identity ('{exp}'). "
                f"An unauthorized party is attempting to submit a quantum signature under a forged sender identity."
            )
            
        elif attack_type == "REPLAY":
            if details.get("replay_detected", False):
                return (
                    f"The same message/signature/session identifier ('{details.get('signature_id', '')}') "
                    f"was previously observed and has been submitted again."
                )
            else:
                return (
                    f"First submission: The message/signature/session identifier ('{details.get('signature_id', '')}') "
                    f"has not been previously observed and is marked as valid for initial transmission."
                )
                
        elif attack_type == "CHANNEL":
            if details.get("invisible", False):
                reason = details.get("invisibility_reason", "")
                return (
                    f"The selected attack is not detected under the selected state/basis because the applied quantum operation leaves the measured state unchanged in that basis. ({reason})"
                )
            elif threat_detected:
                manip = details.get("manipulation", "Z")
                return (
                    f"A quantum-state disturbance (Pauli-{manip}) was introduced during transmission. "
                    f"The receiver's measurement distribution differs from the expected distribution."
                )
            else:
                return "Channel manipulation introduced, but statistical measurement deviation remained within expected bounds."
                
        return "Unknown attack scenario evaluated."


# ============================================================
# SELF-TEST
# ============================================================

if __name__ == "__main__":

    simulator = QDSAttackSimulator()

    print("\n=== QDS ATTACK SIMULATION TEST ===")

    print("\n1. FORGERY")
    print(simulator.simulate_forgery_attack("+"))

    print("\n2. IMPERSONATION")
    print(simulator.simulate_impersonation_attack("Alice", "Attacker"))

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

    print("\n4. CHANNEL MANIPULATION (Detectable)")
    print(simulator.simulate_channel_manipulation("+", "Z", "X"))

    print("\n4. CHANNEL MANIPULATION (Invisible)")
    print(simulator.simulate_channel_manipulation("+", "X", "X"))
