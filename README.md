# Speech Biomarker ALS Parkinson

> **Domain:** Clinical Decision Support & Biomedical Computing
> **Reference Guidelines & Standards:** `Standard Clinical Formulations & ISO/IEC Quality Frameworks`

<div align="center">

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
![Python](https://img.shields.io/badge/Python-3.10%20%7C%203.11%20%7C%203.12-3776AB.svg?logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.111-009688.svg?logo=fastapi&logoColor=white)
![Audit Trail](https://img.shields.io/badge/Audit-HMAC--SHA256_Tamper--Evident-brightgreen.svg)
![Zero-PHI Guard](https://img.shields.io/badge/Guard-Zero--PHI_Outbound-blue.svg)
![Docker](https://img.shields.io/badge/Docker-Ready-2496ED.svg?logo=docker&logoColor=white)

</div>

---

## 📖 What It Does

Speech Biomarker ALS Parkinson is an enterprise-grade analytical engine for detecting vocal biomarkers associated with Amyotrophic Lateral Sclerosis (ALS) and Parkinson's disease. The system analyzes acoustic features including:

- **Jitter & Shimmer Perturbations** - Micro-perturbations in fundamental frequency and amplitude
- **Dysarthria Indicators** - Speech motor control degradation markers
- **Formant Frequency Analysis** - Vocal tract resonance patterns
- **Harmonics-to-Noise Ratio (HNR)** - Voice quality assessment

The system employs a multi-agent consensus architecture with specialized workers for invariant quality control, safety escalation, and protocol conformance verification.

---

## ⚙️ Key Capabilities & Algorithmic Modules

- **Deterministic Calculation Engine**: Strict compliance with standard reference formulations and thresholds.
- **Risk & Urgency Classification**: Multi-tier categorization (ROUTINE, ELEVATED, CRITICAL_STAT) with automated clinical/operational action recommendations.
- **Validation & Guardrails**: Rigorous input bounds checking and anomaly detection.
- **Multi-Agent Consensus**: Three specialized workers evaluate each task independently.
- **Zero-PHI Outbound Protection**: Prevents protected health information leakage.

### Worker Agents

| Worker | Responsibility |
|--------|----------------|
| `InvariantQCWorker` | Primary metric threshold boundary audit |
| `SafetyEscalationWorker` | Critical safety interlock and emergency escalation |
| `ProtocolConformanceWorker` | Specification conformance and anomaly triage |

---

## 💻 Installation

```bash
# Clone the repository
git clone https://github.com/abusuraihsakhri/speech-biomarker-als-parkinson.git
cd speech-biomarker-als-parkinson

# Install dependencies
pip install fastapi uvicorn pydantic pytest
```

---

## 💻 CLI Quickstart & Usage

### 1. Guided Interactive Mode
```bash
python cli.py
```

### 2. Direct Parameterized Evaluation
```bash
python cli.py audit --task-id TASK-001 --target KEY-01 --primary 28.5 --secondary 14.2 --critical --status DISCORDANT
```

### 3. Batch Processing
```bash
python cli.py batch -i sample.csv -o results.csv
```

### 4. Verify Audit Trail Integrity
```bash
python cli.py verify-audit
```

### 5. Launch REST API Server
```bash
python cli.py serve --host 127.0.0.1 --port 8000
```

### Parameter Reference
- `--task-id`: Unique task/case identifier (required, 1-128 chars)
- `--target`: Entity or specimen identifier (required, 1-128 chars)
- `--primary`: Primary measurement value (float)
- `--secondary`: Secondary measurement value (float)
- `--critical`: Flag for emergency escalation (boolean)
- `--status`: Status descriptor (1-64 chars, e.g., NOMINAL, DISCORDANT, ANOMALY)

### Input Data Schema (CSV)

| Field | Description | Requirement |
|:------|:------------|:------------|
| `task_id` | Parameter / observation metric | Required |
| `target_identifier` | Parameter / observation metric | Required |
| `primary_metric` | Primary measurement value (float) | Required |
| `secondary_metric` | Secondary measurement value (float) | Optional |
| `is_critical_flag` | Emergency escalation flag (true/false) | Optional |
| `status_descriptor` | Status code or phenotype | Optional |

---

## 🛡️ Security & Enterprise Architecture

* **Zero-PHI Outbound Interceptor:** Active AST and regex inspection blocking SSNs, MRNs, phone numbers, and patient identifiers.
* **Tamper-Evident HMAC-SHA256 Audit Trail:** Chained, cryptographically signed logs for every evaluation and state transition.
* **Secure Secret Management:** HMAC key sourced from `AUDIT_SECRET_KEY` environment variable or cryptographically random fallback.
* **Air-Gapped LLM Reasoning Adapter:** Agnostic integration for local Ollama instances (`llama3`, `mistral`), Claude 3.5 Sonnet, GPT-4o, and deterministic test mocks.
* **Active Learning Bayesian Calibration:** Dynamic tracker updating worker reliability weights and monitoring Brier calibration drift.
* **FastAPI & Prometheus Telemetry:** Exposes OpenAPI 3.1 REST endpoints and operational Prometheus metrics (`/metrics`).

---

## 🧪 Testing & Verification

Run the automated test suite:

```bash
pytest -v
```

Execute high-throughput batch simulation benchmarks:

```bash
python simulator.py --tasks 1000 --concurrency 8
```

### Test Coverage

| Test Module | Description |
|------------|-------------|
| `test_phi_guard_enforcement` | Validates PHI detection and blocking |
| `test_specialized_workers` | Tests individual worker agent logic |
| `test_supervisor_consensus_and_audit` | Verifies multi-agent consensus and audit trail |
| `test_sub_agents` | Tests vocal marker AI sub-agents |
| `test_coordinator` | Validates coordinator consensus logic |
| `test_cli` | CLI command integration tests |
| `test_enrichment_suite_execution` | Enrichment feature execution tests |
| `test_enrichment_threshold_escalation` | Enrichment threshold boundary tests |

---

## 🐳 Container Deployment

```bash
docker build -t speech-biomarker-als-parkinson .
docker run -p 8000:8000 speech-biomarker-als-parkinson
```

---

## 📁 Project Structure

```
speech-biomarker-als-parkinson/
├── agents/                    # Enterprise analytical agents
│   ├── __init__.py           # Package initialization
│   ├── api.py                # FastAPI REST endpoints
│   ├── base.py               # Security, PHI guard, audit trail
│   ├── learning.py           # Bayesian calibration engine
│   ├── llm_factory.py        # LLM client factory
│   ├── metrics.py            # Prometheus metrics collector
│   ├── models.py             # Pydantic data models
│   ├── streamer.py           # WebSocket telemetry streamer
│   ├── supervisor.py         # Master orchestrator
│   └── workers.py            # Specialized worker agents
├── vocal_marker_ai/          # Vocal marker AI engine
│   ├── __init__.py           # Package initialization
│   ├── agents.py             # Sub-agent implementations
│   ├── cli.py                # CLI interface
│   ├── engine.py             # Core algorithmic engine
│   ├── models.py             # Data models
│   └── server.py             # FastAPI server factory
├── tests/                    # Test suite
│   ├── test_speech_biomarker_als_parkinson.py
│   ├── test_vocal_marker_ai.py
│   └── test_enrichment.py
├── enrichment.py             # Domain enrichment features
├── cli.py                    # Main CLI entry point
├── simulator.py              # High-throughput simulator
├── pyproject.toml            # Project configuration
├── Dockerfile                # Container configuration
├── sample.csv                # Sample input data
└── sample_payload.json       # Sample API payload
```

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
