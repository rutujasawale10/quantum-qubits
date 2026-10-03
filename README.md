# 🔐 Quantum Qubits

### Quantum-Inspired Cybersecurity Prototype for Digital Signature Security

**Smart India Hackathon (SIH) 2026**  
**Problem Statement ID:** SIH26141  
**Theme:** Blockchain & Cybersecurity  
**Team:** Qubits

🌐 **Live Demo:** https://quantum-qubits.onrender.com  
💻 **GitHub Repository:** https://github.com/rutujasawale10/quantum-qubits

---

## 📌 Project Overview

**Quantum Qubits** is a software-based quantum simulation and quantum-inspired cybersecurity prototype designed to explore digital-signature security under controlled adversarial scenarios.

The system combines conventional cryptographic mechanisms with quantum-state-based verification concepts and simulated attack scenarios.

The prototype follows an:

**Alice (Sender) → Eve (Adversary) → Bob (Verifier)**

workflow to demonstrate how messages, signatures, quantum states, and security verification can interact in a controlled experimental environment.

> **Note:** This project is a research and educational prototype based on software simulation. It does not use real quantum hardware and should not be interpreted as a production-ready Quantum Digital Signature (QDS) implementation.

---

## 🎯 Problem Statement

**Problem Statement ID:** `SIH26141`

**Theme:** Blockchain & Cybersecurity

The project investigates quantum-inspired techniques for strengthening and evaluating digital-signature security through software-based simulation and controlled cybersecurity experiments.

---

## ✨ Key Features

- 🔏 Digital signature generation and verification
- 🔐 SHA-256 based message hashing
- 🔑 ECDSA digital signatures using the SECP256R1 / NIST P-256 curve
- ⚛️ Quantum-state simulation using Qiskit
- 🧪 Controlled adversarial attack simulations
- 🔍 Quantum-state verification
- 📊 Statistical security/threat analysis
- 🔁 Replay-attack detection mechanisms
- 👩 Alice sender workflow
- 🕵️ Eve adversarial simulation
- 👨 Bob verification workflow
- 🌐 Interactive web dashboard
- 📈 Research and performance evaluation endpoints

---

## 🏗️ System Architecture

```text
                ┌──────────────────────┐
                │        ALICE         │
                │       Sender         │
                │                      │
                │  Message Generation  │
                │  SHA-256 Hashing     │
                │  ECDSA Signature     │
                │  Quantum Encoding    │
                └──────────┬───────────┘
                           │
                           ▼
                ┌──────────────────────┐
                │         EVE          │
                │      Adversary       │
                │                      │
                │ Controlled Attack    │
                │    Simulation        │
                └──────────┬───────────┘
                           │
                           ▼
                ┌──────────────────────┐
                │         BOB          │
                │      Verifier        │
                │                      │
                │ Signature Check      │
                │ Quantum-State Check  │
                │ Security Analysis    │
                └──────────────────────┘
```

---

## ⚛️ Quantum States

The prototype works with quantum-state representations including:

| State | Representation |
|---|---|
| `|0⟩` | Computational basis state |
| `|1⟩` | Computational basis state |
| `|+⟩` | Superposition state |
| `|-⟩` | Superposition state |

Qiskit is used to support software-based quantum-state preparation and simulation.

---

## 🛡️ Controlled Attack Simulations

The prototype supports controlled cybersecurity scenarios such as:

- **Forgery**
- **Impersonation**
- **Replay Attack**
- **Channel Manipulation**
- **Unauthorized Verification**

These scenarios are used for experimental evaluation of the prototype and should not be interpreted as evidence of universal real-world attack detection.

---

## 🔄 Verification Pipeline

```text
Input Message
     │
     ▼
SHA-256 Hash
     │
     ▼
ECDSA Signature
     │
     ▼
Quantum-State Preparation
     │
     ▼
Controlled Attack Simulation
     │
     ▼
Signature Verification
     │
     ▼
Quantum-State Verification
     │
     ▼
Statistical Security Analysis
     │
     ▼
Final Verification Result
```

---

## 🧰 Technology Stack

### Backend

- Python
- FastAPI
- Uvicorn

### Quantum Simulation

- Qiskit

### Cryptography

- SHA-256
- ECDSA
- SECP256R1 / NIST P-256

### Frontend

- HTML
- CSS
- JavaScript

### Deployment

- GitHub
- Render

---

## 🌐 API

The FastAPI backend provides endpoints for the different stages of the prototype.

Some important endpoints include:

```text
GET  /api/health
GET  /api/states
POST /api/verify
GET  /api/security-analysis
GET  /api/end-to-end
GET  /api/performance
GET  /api/research-evaluation
GET  /api/mathematical-model
```

Interactive API documentation is available through FastAPI Swagger UI:

**Live API Docs:**  
https://quantum-qubits.onrender.com/docs

Health endpoint:

https://quantum-qubits.onrender.com/api/health

---

## 📂 Project Structure

```text
quantum-qubits/
│
├── api.py
├── requirements.txt
├── README.md
├── README_REPRODUCIBILITY.md
│
├── frontend/
│   ├── index.html
│   ├── style.css
│   └── app.js
│
└── ...
```

Additional Python modules contain the cryptographic, quantum-simulation, security-analysis, and experimental components of the prototype.

---

## 🚀 Installation

### 1. Clone the repository

```bash
git clone https://github.com/rutujasawale10/quantum-qubits.git
cd quantum-qubits
```

### 2. Create a virtual environment

Windows:

```bash
python -m venv .venv
.venv\Scripts\activate
```

Linux/macOS:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

---

## ▶️ Run Locally

Start the FastAPI application with Uvicorn:

```bash
uvicorn api:app --host 127.0.0.1 --port 8000
```

Then open:

```text
http://127.0.0.1:8000
```

API documentation:

```text
http://127.0.0.1:8000/docs
```

Health check:

```text
http://127.0.0.1:8000/api/health
```

---

## ☁️ Live Deployment

The application is deployed using **Render**.

### Live Application

https://quantum-qubits.onrender.com

The deployment uses:

```bash
pip install -r requirements.txt
```

as the build command and:

```bash
uvicorn api:app --host 0.0.0.0 --port $PORT
```

as the production start command.

> The application currently uses Render's free service tier, so the first request after inactivity may take additional time while the service starts.

---

## 🔒 Security Considerations

Private cryptographic keys must remain server-side and must never be exposed through:

- Browser JavaScript
- DOM elements
- Public API responses
- Frontend source code
- Public repository files

The project is designed so that sensitive private-key material is not intentionally exposed to the client.

---

## ⚠️ Limitations

Quantum Qubits is an experimental research prototype.

It:

- Uses software-based quantum simulation.
- Does not currently execute on real quantum hardware.
- Is not a production-ready Quantum Digital Signature implementation.
- Does not replace established production cryptographic infrastructure.
- Does not guarantee 100% security or attack detection.
- Evaluates attacks in controlled simulated scenarios.
- Should not be interpreted as formal proof of quantum-safe security.

Results produced by the prototype should therefore be interpreted within the scope and assumptions of the experimental environment.

---

## 🔭 Future Scope

Possible future research directions include:

- Evaluation using real quantum hardware
- Larger and more diverse experimental scenarios
- Extended adversarial models
- Improved statistical verification techniques
- Comparative evaluation with additional cryptographic approaches
- Investigation of more advanced QDS-inspired protocols
- Larger-scale performance and security evaluation

---

## 👥 Team

### Team Qubits

Developed for **Smart India Hackathon (SIH) 2026**.

**Problem Statement ID:** SIH26141  
**Theme:** Blockchain & Cybersecurity

---

## 📚 Research Disclaimer

This repository represents a **quantum-inspired cybersecurity research prototype**.

Terms related to quantum security or Quantum Digital Signatures refer to concepts explored through software simulation and prototype experimentation unless explicitly stated otherwise.

The project does not claim universal security, perfect attack detection, or production-ready quantum-secure communication.

---

## 🔗 Links

**Live Demo:**  
https://quantum-qubits.onrender.com

**API Documentation:**  
https://quantum-qubits.onrender.com/docs

**GitHub Repository:**  
https://github.com/rutujasawale10/quantum-qubits

---

⭐ If you find the project useful for learning or research, consider starring the repository.