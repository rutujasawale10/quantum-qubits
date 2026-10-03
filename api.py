import logging
import os
from typing import Optional, Dict, Any
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from qds_attack_simulator import QDSAttackSimulator
from alice_sender import alice_transaction_creator

# Configure Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("qds_api")

app = FastAPI(
    title="Quantum-QDS Security API",
    description="Quantum-Inspired Cyber Threat Detection for Digital Signature Security (SIH26141 - Team Qubits)",
    version="1.0.0"
)

# Enable CORS for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Instantiate QDS Attack Simulator Engine
simulator = QDSAttackSimulator()


# Helper function to ensure dict keys and numerical values are JSON serializable
def sanitize_json_data(obj):
    if isinstance(obj, dict):
        return {str(k): sanitize_json_data(v) for k, v in obj.items()}
    elif isinstance(obj, (list, tuple)):
        return [sanitize_json_data(v) for v in obj]
    elif hasattr(obj, "item"):  # handle numpy scalar types if present
        return obj.item()
    return obj


# Global Exception Handler to prevent exposing unhandled tracebacks
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled Backend Error on {request.url}: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "status": "ERROR",
            "message": f"Backend Error: {str(exc)}",
            "error_type": exc.__class__.__name__
        }
    )


class VerificationRequest(BaseModel):
    state: str = Field(default="0", description="Quantum state: '0', '1', '+', '-'")
    attack: str = Field(default="NONE", description="Attack type: 'NONE', 'FORGERY', 'IMPERSONATION', 'REPLAY', 'CHANNEL'")
    verifier: str = Field(default="Bob", description="Verifier identity: 'Bob' or unauthorized entity like 'Eve'")
    sender: str = Field(default="Alice", description="Sender identity: 'Alice' or attacker identity like 'Attacker'")
    shots: int = Field(default=1000, description="Number of quantum measurement shots")
    error_threshold_pct: float = Field(default=10.0, description="Statistical error threshold percentage")
    chi_threshold: float = Field(default=10.0, description="Chi-square statistic threshold")
    channel_gate: str = Field(default="Z", description="Channel manipulation gate: 'Z' or 'X'")
    digital_message: str = Field(default="Default Quantum Message", description="Message content for replay tracking")
    signature_id: str = Field(default="sig_default_001", description="Signature identifier for replay tracking")


@app.get("/api/health")
def health():
    return {
        "status": "healthy",
        "project": "Quantum-Inspired Cyber Threat Detection for Digital Signature Security",
        "problem_statement": "SIH26141",
        "team": "Qubits",
        "qiskit_backend": "Statevector Simulation"
    }


@app.get("/api/states")
def states():
    return {
        "states": ["0", "1", "+", "-"],
        "bases": ["Z", "X"],
        "attacks": [
            "NONE",
            "FORGERY",
            "IMPERSONATION",
            "REPLAY",
            "CHANNEL"
        ],
        "verifiers": ["Bob", "Eve"]
    }


@app.post("/api/verify")
def verify(request: VerificationRequest):
    state = request.state
    attack = request.attack.upper()
    verifier = request.verifier
    sender = request.sender
    shots = request.shots

    # 1. Request Validation
    if state not in ["0", "1", "+", "-"]:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid quantum state '{state}'. Allowed states: '0', '1', '+', '-'"
        )

    if attack not in ["NONE", "FORGERY", "IMPERSONATION", "REPLAY", "CHANNEL"]:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid attack '{attack}'. Allowed attacks: 'NONE', 'FORGERY', 'IMPERSONATION', 'REPLAY', 'CHANNEL'"
        )

    if shots <= 0:
        raise HTTPException(
            status_code=400,
            detail="Shots count must be a positive integer (> 0)."
        )

    if request.error_threshold_pct < 0 or request.chi_threshold < 0:
        raise HTTPException(
            status_code=400,
            detail="Threshold parameters must be non-negative numeric values."
        )

    # 2. Check Verifier Authorization
    auth_res = simulator.evaluate_unauthorized_verification(
        sender=sender,
        expected_verifier="Bob",
        actual_verifier=verifier
    )

    if not auth_res["is_authorized"]:
        simulation_trace = {
            "is_blocked": True,
            "steps": [
                {
                    "id": "start",
                    "title": "Simulation Started",
                    "detail": f"Verification process initialized for state |{state}⟩ from verifier '{verifier}'",
                    "status": "completed"
                },
                {
                    "id": "auth_check",
                    "title": "Authorization Gateway Check",
                    "detail": f"Authorization Check → FAILED (Actual Verifier '{verifier}' != Expected 'Bob')",
                    "status": "blocked"
                },
                {
                    "id": "final_decision",
                    "title": "Final Decision",
                    "detail": "Verification Blocked — Access Denied before quantum processing",
                    "status": "blocked"
                }
            ]
        }
        return sanitize_json_data({
            "status": "BLOCKED",
            "threat_detected": True,
            "attack": "UNAUTHORIZED VERIFICATION ATTEMPT",
            "message": f"Unauthorized verifier '{verifier}' attempt blocked.",
            "verifier": verifier,
            "sender": sender,
            "state": state,
            "authorization_details": auth_res,
            "simulation_trace": simulation_trace
        })

    # 3. Determine Basis (Z basis for |0> and |1>, X basis for |+> and |->)
    basis = "Z" if state in ["0", "1"] else "X"

    # 4. Get Baseline Quantum Statevector
    original_sv = simulator._get_quantum_statevector(state)

    # 5. Simulate Selected Attack Logic
    attack_res = {}
    received_sv = original_sv
    identity_threat = False
    replay_threat = False
    forgery_threat = False
    channel_threat = False

    if attack == "NONE":
        attack_res = {
            "attack": "Genuine / No Attack",
            "received_state": state,
            "detected": False
        }
        received_sv = original_sv

    elif attack == "FORGERY":
        attack_res = simulator.simulate_forgery_attack(state)
        received_sv = simulator._get_quantum_statevector(attack_res["received_state"])
        forgery_threat = attack_res.get("detected", False)

    elif attack == "IMPERSONATION":
        effective_sender = sender if sender != "Alice" else "Attacker"
        attack_res = simulator.simulate_impersonation_attack(
            legitimate_sender="Alice",
            attacker_sender=effective_sender
        )
        identity_threat = attack_res.get("detected", False)
        received_sv = original_sv

    elif attack == "REPLAY":
        sig_id = request.signature_id if request.signature_id != "sig_default_001" else f"{request.digital_message}:{state}"
        attack_res = simulator.simulate_replay_attack(
            message=request.digital_message,
            signature_id=sig_id
        )
        replay_threat = attack_res.get("detected", False)
        received_sv = original_sv

    elif attack == "CHANNEL":
        gate = request.channel_gate.upper() if request.channel_gate.upper() in ["X", "Z"] else "Z"
        attack_res = simulator.simulate_channel_manipulation(
            original_state=state,
            manipulation=gate,
            basis=basis
        )
        received_sv = simulator._get_quantum_statevector(attack_res["received_state"])
        channel_threat = attack_res.get("detected", False)

    # 6. Quantum Measurement & Statistical Analysis
    received_counts = simulator._measure_state_in_basis(
        received_sv,
        basis,
        shots=shots
    )

    expected_probs = simulator._calculate_expected_distribution(
        original_sv,
        basis
    )

    chi_square = simulator._calculate_chi_square_stat(
        received_counts,
        expected_probs,
        shots
    )

    original_counts = simulator._measure_state_in_basis(
        original_sv,
        basis,
        shots=shots
    )

    error_rate = simulator._calculate_error_rate(
        original_counts,
        received_counts
    )

    # 7. Forgery Probability & Statistical Threshold Engine Evaluation
    received_state_str = attack_res.get("received_state", state)
    forgery_prob_data = simulator.calculate_forgery_probability(
        attack_type=attack,
        original_state=state,
        received_state=received_state_str,
        recv_counts=received_counts,
        total_shots=shots,
        identity_threat=identity_threat,
        replay_threat=replay_threat
    )

    threshold_result = simulator.evaluate_statistical_threshold(
        attack_type=attack,
        error_rate=error_rate,
        forgery_prob_data=forgery_prob_data,
        chi_square_val=chi_square,
        error_threshold_pct=request.error_threshold_pct,
        chi_threshold=request.chi_threshold,
        identity_threat=identity_threat,
        replay_threat=replay_threat
    )

    # Aggregate Threat Flag
    stat_threat = bool(threshold_result.get("is_threat", False))
    threat_detected = (
        stat_threat or identity_threat or replay_threat or forgery_threat or channel_threat
    )

    # Construct Simulation Trace Steps
    c0 = received_counts.get(0, received_counts.get("0", 0))
    c1 = received_counts.get(1, received_counts.get("1", 0))
    err_pct_val = round(error_rate * 100.0, 2)
    chi_square_val = round(chi_square, 2)

    if attack == "NONE":
        attack_detail = "No attack applied. Legitimate verification path."
        state_trans_detail = f"State Preserved: |{state}⟩ → |{state}⟩"
    elif attack == "FORGERY":
        attack_detail = "Received quantum state/signature differs from the expected state."
        state_trans_detail = f"State Transformation: |{state}⟩ → |{received_state_str}⟩"
    elif attack == "IMPERSONATION":
        effective_snd = sender if sender != "Alice" else "Attacker"
        attack_detail = "Verifier identity does not match the authorized identity."
        state_trans_detail = f"State Preserved: |{state}⟩ (Header Credential Mismatch: {effective_snd})"
    elif attack == "REPLAY":
        is_rep = attack_res.get("replay_detected", False)
        if is_rep:
            attack_detail = "Previously used message/signature hash was submitted again."
        else:
            attack_detail = "First signature use verified. Signature hash registered."
        state_trans_detail = f"State Preserved: |{state}⟩"
    elif attack == "CHANNEL":
        gate = request.channel_gate.upper()
        attack_detail = "Simulated Pauli operation changed the transmitted quantum state."
        state_trans_detail = f"State Transformation: |{state}⟩ → |{received_state_str}⟩ (Pauli-{gate} Gate)"

    err_exceeded = err_pct_val > request.error_threshold_pct
    chi_exceeded = chi_square_val > request.chi_threshold

    err_detail = f"Error Threshold Check: Error {err_pct_val:.2f}% " + (f"> {request.error_threshold_pct:.2f}% (EXCEEDED)" if err_exceeded else f"≤ {request.error_threshold_pct:.2f}% (WITHIN THRESHOLD)")
    chi_detail = f"Chi-Square Check: Chi-Square {chi_square_val:.2f} " + (f"> {request.chi_threshold:.2f} (EXCEEDED)" if chi_exceeded else f"≤ {request.chi_threshold:.2f} (WITHIN THRESHOLD)")

    trace_steps = [
        {"id": "start", "title": "Simulation Started", "detail": f"Verification process initialized (Shots: {shots})", "status": "completed"},
        {"id": "state_prep", "title": "Quantum State Preparation", "detail": f"State Prepared: |{state}⟩", "status": "completed"},
        {"id": "basis_select", "title": "Basis Selection", "detail": f"Verification Basis: {basis}-Basis", "status": "completed"},
        {"id": "attack_apply", "title": f"Attack / Channel: {attack}", "detail": attack_detail, "status": "completed"},
        {"id": "transformation", "title": "State Transformation", "detail": state_trans_detail, "status": "completed"},
        {"id": "measurement", "title": "Quantum Measurement", "detail": f"Running {shots} Measurements... Results: |0⟩ = {c0}, |1⟩ = {c1}", "status": "completed"},
        {"id": "error_rate", "title": "Observed Error Analysis", "detail": f"Observed Error = {err_pct_val:.2f}%", "status": "completed"},
        {"id": "chi_square", "title": "Chi-Square Calculation", "detail": f"Chi-Square = {chi_square_val:.2f}", "status": "completed"},
        {"id": "thresh_error", "title": "Threshold Check (Error)", "detail": err_detail, "status": "completed"},
        {"id": "thresh_chi", "title": "Threshold Check (Chi-Square)", "detail": chi_detail, "status": "completed"},
        {"id": "final_decision", "title": "Threat Decision", "detail": f"FINAL RESULT: {'THREAT DETECTED' if threat_detected else 'VALID SIGNATURE'}", "status": "completed"}
    ]

    simulation_trace = {
        "is_blocked": False,
        "steps": trace_steps
    }

    res_dict = {
        "status": "THREAT" if threat_detected else "VALID",
        "threat_detected": threat_detected,
        "state": state,
        "basis": basis,
        "attack": attack,
        "verifier": verifier,
        "sender": sender,
        "shots": shots,
        "measurement_counts": received_counts,
        "expected_probs": expected_probs,
        "error_rate": error_rate,
        "error_rate_percent": err_pct_val,
        "chi_square": chi_square_val,
        "threshold": {
            "error_threshold_percent": request.error_threshold_pct,
            "chi_threshold": request.chi_threshold
        },
        "threshold_result": threshold_result,
        "forgery_probability": forgery_prob_data,
        "attack_details": attack_res,
        "simulation_trace": simulation_trace
    }

    return sanitize_json_data(res_dict)


# -------------------------------------------------------------------
# Additional Analytical & Evaluation Endpoints
# -------------------------------------------------------------------

@app.get("/api/security-analysis")
def security_analysis(shots: int = 1000):
    return sanitize_json_data(simulator.run_security_analysis(shots=shots))


@app.get("/api/end-to-end")
def end_to_end_validation(shots: int = 1000):
    return sanitize_json_data(simulator.run_end_to_end_validation(shots=shots))


@app.get("/api/performance")
def performance_evaluation(attempts: int = 50, shots: int = 1000):
    return sanitize_json_data(simulator.run_performance_evaluation(attempts=attempts, shots=shots))


@app.get("/api/research-evaluation")
def research_evaluation(shots: int = 1000):
    return sanitize_json_data(simulator.run_research_evaluation(shots=shots))


@app.get("/api/mathematical-model")
def mathematical_model(
    state: str = "0",
    basis: str = "Z",
    attack: str = "FORGERY",
    shots: int = 1000,
    error_threshold_pct: float = 10.0,
    chi_threshold: float = 10.0
):
    return sanitize_json_data(simulator.get_mathematical_security_model(
        state_name=state,
        basis=basis,
        attack_type=attack,
        shots=shots,
        error_threshold_pct=error_threshold_pct,
        chi_threshold=chi_threshold
    ))


@app.post("/api/replay/reset")
def reset_replay_history():
    simulator.used_signatures.clear()
    return {
        "status": "SUCCESS",
        "message": "Replay signature cache successfully cleared."
    }


# ============================================================================
# ALICE / SENDER MODULE ENDPOINTS (STEP 1 + STEP 2 + STEP 3: QUANTUM PREP)
# ============================================================================

class AliceTransactionRequest(BaseModel):
    message: str = Field(..., description="Transaction message / data content")
    transaction_id: Optional[str] = Field(default=None, description="Optional unique Transaction ID")
    sender: str = Field(default="Alice", description="Sender identity (fixed as Alice)")
    receiver: str = Field(default="Bob", description="Receiver identity (fixed as Bob)")
    auto_sign: bool = Field(default=True, description="Whether to automatically compute SHA-256 and digital signature")
    quantum_state: Optional[str] = Field(default="|0>", description="Single-qubit quantum state: '|0>', '|1>', '|+>', '|->'")


class AliceSignRequest(BaseModel):
    transaction_id: Optional[str] = Field(default=None, description="Transaction ID of existing transaction in session")
    message: Optional[str] = Field(default=None, description="Direct transaction message to sign")


class AliceVerifySignatureRequest(BaseModel):
    transaction: Dict[str, Any] = Field(..., description="Transaction record to verify signature against Alice public key")


class AliceQuantumStateRequest(BaseModel):
    transaction_id: str = Field(..., description="Transaction ID to attach prepared quantum state to")
    state: str = Field(default="|0>", description="Target quantum state: '|0>', '|1>', '|+>', '|->'")


class AliceTransmissionPrepareRequest(BaseModel):
    transaction_id: str = Field(..., description="Transaction ID to prepare transmission packet for")


class AliceTeleportRequest(BaseModel):
    transaction_id: str = Field(..., description="Transaction ID to execute 3-qubit teleportation for")


@app.post("/api/alice/teleport")
def teleport_alice_transaction(req: AliceTeleportRequest):
    """
    Step 5: Run 3-qubit quantum teleportation for a verified transaction.
    """
    try:
        res = alice_transaction_creator.teleport_transaction(req.transaction_id)
        return {
            "status": "SUCCESS",
            "message": "3-Qubit Quantum Teleportation executed and verified successfully.",
            "transaction_id": res["transaction_id"],
            "sender": res["sender"],
            "receiver": res["receiver"],
            "input_state": res["input_state"],
            "bell_state": res["bell_state"],
            "measurement_bits": res["measurement_bits"],
            "correction": res["correction"],
            "receiver_state": res["receiver_state"],
            "fidelity": res["fidelity"],
            "verification": res["verification"],
            "teleportation": sanitize_json_data(res["teleportation"]),
            "transaction": sanitize_json_data(res["transaction"])
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/api/alice/bell-state")
def get_alice_bell_state():
    """
    Step 5: Retrieve verified Bell Pair |Φ+⟩ metadata and statevector.
    """
    return {
        "status": "SUCCESS",
        "bell_state": sanitize_json_data(alice_transaction_creator.generate_bell_state())
    }


@app.get("/api/alice/teleport/{transaction_id}")
def get_alice_teleportation_details(transaction_id: str):
    """
    Step 5: Retrieve teleportation details for a transaction ID.
    """
    try:
        res = alice_transaction_creator.teleport_transaction(transaction_id)
        return {
            "status": "SUCCESS",
            "transaction_id": transaction_id,
            "teleportation": sanitize_json_data(res["teleportation"])
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/api/alice/transmission/prepare")
def prepare_alice_transmission(req: AliceTransmissionPrepareRequest):
    """
    Step 4: Prepare a verified quantum transmission packet ready for quantum channel egress.
    """
    try:
        res = alice_transaction_creator.prepare_transmission_packet(req.transaction_id)
        return {
            "status": "SUCCESS",
            "message": "Quantum transmission packet prepared and ready for channel.",
            "transaction_id": res["transaction_id"],
            "sender": res["sender"],
            "receiver": res["receiver"],
            "quantum_state": res["quantum_state"],
            "quantum_basis": res["quantum_basis"],
            "signature_status": res["signature_status"],
            "quantum_verification": res["quantum_verification"],
            "transmission_status": res["transmission_status"],
            "transmission_packet": sanitize_json_data(res["transmission_packet"])
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/api/alice/transmission/{transaction_id}")
def get_alice_transmission_packet(transaction_id: str):
    """
    Step 4: Retrieve the prepared quantum transmission packet for a transaction.
    """
    try:
        packet = alice_transaction_creator.get_transmission_packet(transaction_id)
        return {
            "status": "SUCCESS",
            "transaction_id": transaction_id,
            "transmission_packet": sanitize_json_data(packet)
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/api/alice/transaction")
def create_alice_transaction(req: AliceTransactionRequest):
    """
    Steps 1, 2, 3: Alice Transaction Creator, Signer & Quantum State Preparer.
    Validates inputs, generates SHA-256 hash, signs canonical payload, and prepares verified Qiskit quantum state.
    """
    try:
        record = alice_transaction_creator.create_transaction(
            message=req.message,
            transaction_id=req.transaction_id,
            sender=req.sender,
            receiver=req.receiver,
            auto_sign=req.auto_sign,
            quantum_state=req.quantum_state
        )
        return {
            "status": "SUCCESS",
            "message": "Transaction created, digitally signed, and quantum state prepared successfully.",
            "transaction": sanitize_json_data(record)
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/api/alice/quantum-state")
def set_alice_quantum_state(req: AliceQuantumStateRequest):
    """
    Step 3: Prepare and attach a verified single-qubit quantum state (|0>, |1>, |+>, |->) to a transaction.
    """
    try:
        updated_tx = alice_transaction_creator.set_transaction_quantum_state(
            transaction_id=req.transaction_id,
            state_name=req.state
        )
        quantum_details = updated_tx.get("quantum_details", {})
        return {
            "status": "SUCCESS",
            "transaction_id": req.transaction_id,
            "quantum_state": updated_tx.get("quantum_state"),
            "quantum_state_label": updated_tx.get("quantum_state_label"),
            "basis": updated_tx.get("quantum_basis"),
            "basis_name": updated_tx.get("quantum_basis_name"),
            "statevector": sanitize_json_data(updated_tx.get("statevector")),
            "probabilities": sanitize_json_data(updated_tx.get("probabilities")),
            "preparation_gates": updated_tx.get("preparation_gates"),
            "circuit_ascii": updated_tx.get("circuit_ascii"),
            "verification_status": updated_tx.get("quantum_verification"),
            "preparation_status": updated_tx.get("preparation_status"),
            "transaction": sanitize_json_data(updated_tx)
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/api/alice/quantum-states")
def get_alice_quantum_states():
    """Retrieve supported quantum states and their basis/circuit metadata."""
    return {
        "status": "SUCCESS",
        "states": sanitize_json_data(alice_transaction_creator.get_supported_states())
    }


@app.post("/api/alice/sign")
def sign_alice_transaction(req: AliceSignRequest):
    """
    Step 2: Sign a transaction by ID or create a freshly signed record.
    """
    try:
        if req.transaction_id:
            record = alice_transaction_creator.sign_transaction_by_id(req.transaction_id)
        elif req.message:
            record = alice_transaction_creator.create_transaction(message=req.message, auto_sign=True)
        else:
            raise HTTPException(status_code=400, detail="Must provide either transaction_id or message to sign.")

        return {
            "status": "SUCCESS",
            "message": "Transaction digitally signed.",
            "transaction": sanitize_json_data(record)
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/api/alice/verify-signature")
def verify_alice_signature(req: AliceVerifySignatureRequest):
    """
    Step 2: Verify a transaction's signature against Alice's public key.
    """
    is_valid, details = alice_transaction_creator.verify_transaction_signature(req.transaction)
    return {
        "status": "SUCCESS",
        "valid": is_valid,
        "details": details
    }


@app.get("/api/alice/public-key")
def get_alice_public_key():
    """Retrieve Alice's public key metadata."""
    return {
        "status": "SUCCESS",
        "public_key": sanitize_json_data(alice_transaction_creator.get_public_key_metadata())
    }


@app.get("/api/alice/transactions")
def get_alice_transactions():
    """Retrieve all created transactions in the current Alice session."""
    return {
        "status": "SUCCESS",
        "transactions": sanitize_json_data(alice_transaction_creator.get_all_transactions())
    }


@app.get("/api/alice/next-id")
def get_alice_next_id():
    """Generate the next unique transaction ID for Alice."""
    return {
        "status": "SUCCESS",
        "next_transaction_id": alice_transaction_creator.generate_transaction_id()
    }


@app.post("/api/alice/reset")
def reset_alice_session():
    """Reset the Alice transaction creator session and re-seed keys."""
    alice_transaction_creator.reset_session()
    return {
        "status": "SUCCESS",
        "message": "Alice transaction session reset successfully."
    }


# Mount Frontend Static Directory if Present
frontend_dir = os.path.join(os.path.dirname(__file__), "frontend")
if os.path.exists(frontend_dir):
    app.mount("/", StaticFiles(directory=frontend_dir, html=True), name="frontend")