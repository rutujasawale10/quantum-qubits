# SIH26141 — Quantum-Inspired Cyber Threat Detection for Digital Signature Security
## Final Demonstration & Reproducibility Package (Task #12)

---

### 1. Project Purpose
This repository implements a **quantum-inspired cyber threat-detection prototype** for digital signature security under **SIH26141**. The prototype integrates Qiskit-based quantum state simulation (3-qubit teleportation, Pauli eigenstates, projective measurements) with an identity authorization gateway, stateful replay tracking, and a statistical chi-square threshold engine to detect cyber threats across digital signature verification pipelines.

---

### 2. Environment Requirements
- **Operating System**: Windows (tested on Windows 10/11)
- **Python**: Python 3.10+ (tested on Python 3.13)
- **Core Dependencies**:
  - `qiskit` (version >= 2.0.0)
  - `streamlit` (version >= 1.30.0)
  - `numpy` (version >= 1.24.0)
  - `scipy` (version >= 1.10.0)

---

### 3. Installation & Virtual Environment Setup

1. **Clone / Open Workspace Directory**:
   ```powershell
   cd c:\Users\ASUS\OneDrive\Desktop\quantum-qds
   ```

2. **Activate Virtual Environment** (Windows PowerShell):
   ```powershell
   .venv\Scripts\Activate.ps1
   ```
   Or in Windows Command Prompt:
   ```cmd
   .venv\Scripts\activate.bat
   ```

3. **Verify Environment**:
   ```powershell
   .venv\Scripts\python.exe scratch/environment_check.py
   ```

---

### 4. Running the Dashboard Application

Launch the Streamlit dashboard using the virtual environment Python executable:
```powershell
.venv\Scripts\python.exe -m streamlit run app.py
```
Open your browser at `http://localhost:8501` to view the **Quantum Digital Signature Security Console**.

---

### 5. Running Validation Tests

To run the complete automated test suite across Tasks #1–#12:

1. **Master Validation Suite (Tasks #1–#11 & Environment)**:
   ```powershell
   .venv\Scripts\python.exe scratch/run_all_validation.py
   ```

2. **Task #12 Reproducibility Verification**:
   ```powershell
   .venv\Scripts\python.exe scratch/test_task12_reproducibility.py
   ```

3. **Individual Task Validation Scripts**:
   ```powershell
   .venv\Scripts\python.exe scratch/test_task10_end_to_end.py
   .venv\Scripts\python.exe scratch/test_task11_research_evaluation.py
   ```

---

### 6. Project Structure

```text
quantum-qds/
│
├── app.py                             # Streamlit interactive Security Command Center
├── qds_attack_simulator.py            # Core threat simulator & security evaluation engine
├── qds_signature_layer.py             # Classical signature & hash generation layer
├── qds_teleport_integrated.py         # 3-qubit Qiskit teleportation circuit module
├── quantum_background.py              # Animated quantum canvas background component
├── ui_theme.py                        # Command Center CSS design theme & styling
├── README_REPRODUCIBILITY.md          # Comprehensive reproducibility guide (this file)
└── scratch/                           # Automated validation suite & environment tools
    ├── environment_check.py           # Dynamic package version checker
    ├── run_all_validation.py          # Master sequential validation runner (Tasks #1–#11)
    ├── test_task1_forgery.py          # Task #1 Forgery probability test
    ├── test_task2_threshold.py        # Task #2 Statistical threshold engine test
    ├── test_task3_pauli.py            # Task #3 Pauli eigenstate & projective measurement test
    ├── test_task4_performance.py      # Task #4 Accuracy & attack-wise performance test
    ├── test_task5_robustness.py       # Task #5 Noise vs attack differentiation test
    ├── test_task6_authorization.py    # Task #6 Unauthorized verification detection test
    ├── test_task7_performance.py      # Task #7 Complete pipeline latency benchmark test
    ├── test_task8_security_analysis.py # Task #8 Security analysis & attack summary test
    ├── test_task9_math_model.py       # Task #9 Mathematical decision model test
    ├── test_task10_end_to_end.py      # Task #10 Integrated 6-scenario validation test
    ├── test_task11_research_evaluation.py # Task #11 SIH objective coverage evaluation test
    └── test_task12_reproducibility.py # Task #12 Reproducibility & package validation test
```

---

### 7. FINAL SIH DEMO FLOW

Follow these step-by-step instructions to demonstrate the prototype's capabilities:

1. **Step 1: Start Dashboard**: Run `.venv\Scripts\python.exe -m streamlit run app.py`.
2. **Step 2: Open Sidebar Controls**: Locate the **⚡ FINAL SIH DEMO PRESET** dropdown in the sidebar.
3. **Step 3: Scenario A — Legitimate Communication**:
   - Select **A. Legitimate Communication (NONE -> VALID)** preset.
   - Click **▶ Run Security Verification**.
   - **Expected Result**: `FINAL SECURITY DECISION: VALID` (Green banner).
4. **Step 4: Scenario B — Forgery Attack**:
   - Select **B. Forgery Attack (FORGERY -> THREAT)** preset.
   - Click **▶ Run Security Verification**.
   - **Expected Result**: `FINAL SECURITY DECISION: THREAT` (Red banner — State alteration detected via Chi-Square).
5. **Step 5: Scenario C — Impersonation Attack**:
   - Select **C. Impersonation Attack (IMPERSONATION -> THREAT)** preset.
   - Click **▶ Run Security Verification**.
   - **Expected Result**: `FINAL SECURITY DECISION: THREAT` (Red banner — Sender mismatch detected).
6. **Step 6: Scenario D — Replay Attack**:
   - Select **D. Replay Attack (REPLAY -> THREAT)** preset.
   - Click **▶ Run Security Verification** twice.
   - **Expected Result**: 1st submission `VALID (FIRST USE)`, 2nd submission `FINAL SECURITY DECISION: THREAT` (Replay hash detected).
7. **Step 7: Scenario E — Channel Manipulation**:
   - Select **E. Channel Manipulation (CHANNEL -> THREAT)** preset.
   - Click **▶ Run Security Verification**.
   - **Expected Result**: `FINAL SECURITY DECISION: THREAT` (Phase-flip noise detected under orthogonal measurement basis).
8. **Step 8: Scenario F — Unauthorized Verification**:
   - Select **F. Unauthorized Verification (UNAUTHORIZED -> BLOCKED)** preset.
   - Click **▶ Run Security Verification**.
   - **Expected Result**: `FINAL SECURITY DECISION: BLOCKED` (Yellow/Orange banner — Unauthorized verifier Eve intercepted).

---

### 8. Scientific Scope & Prototype Limitations

> **IMPORTANT SCIENTIFIC NOTICE**:
> *This project is a quantum-inspired cybersecurity prototype evaluated through controlled software simulation.*

- **Software Simulation**: All quantum states and measurement operations are simulated using Qiskit 2.x software primitives (`Statevector`, `StatevectorSampler`).
- **No Real Quantum Hardware**: No claim is made regarding deployment on physical Quantum Processing Units (QPUs).
- **No Formal Cryptographic Proof**: The prototype demonstrates statistical threat detection; it does not constitute a formal mathematical security proof of information-theoretic security.
- **Controlled Evaluation Boundaries**: Benchmarks and thresholds are prototype evaluation parameters derived from controlled 8-case and 6-scenario benchmark callsets.
- **Runtime Scope**: Latency numbers (~12.8 ms verification / ~0.001 ms gateway) represent local software execution speed and do not evaluate production-scale network distribution.

---

### 9. Final Metrics Reference Summary

- **Controlled 8-Case Attack Benchmark**: 4/4 attack cases detected (100.00% TPR, 100.00% TNR).
- **Controlled Authorization Evaluation**: 1/1 unauthorized verifier attempt blocked (100.00% Auth Detection Rate).
- **Controlled Noise Experiment**: 14/15 cases correctly classified (93.33% Robustness Benchmark Rate).
- **Controlled End-to-End Validation**: 6/6 scenarios passed (100.00% Validation Rate).
- **Controlled Software-Simulation Runtime**:
  - Full Verification Pipeline: ~12.8 ms per attempt.
  - Authorization Gateway: ~0.001 ms per attempt.
