# Speech Biomarker ALS / Parkinson Project

An experimental Python rules engine and browser demonstration for evaluating **user-supplied numeric fields** and status labels. Despite the repository name, the current implementation **does not ingest audio, calculate F0/jitter/shimmer/HNR/formants, or predict ALS or Parkinson's disease**. The thresholds are demonstration parameters, **not clinically derived diagnostic cutoffs**.

## Browser demonstration

The static interface lives in [web/](web/) and works without a Python server. It evaluates sample IDs, numeric thresholds, a status keyword, and a manually selected priority flag, then displays and exports JSON. The evaluation runs entirely in your browser; no API requests are made. Avoid entering patient-identifiable data.

To run it locally:

```bash
python -m http.server 8765 --directory web
# open http://127.0.0.1:8765/
```

The repository also includes a GitHub Pages deployment workflow. See the repository's Pages environment for the deployment URL and status.

## Python features

- `agents/`: Pydantic-validated task payloads, three rule-based workers, coordinator, in-memory HMAC-chained audit entries, and FastAPI endpoints
- `vocal_marker_ai/`: a second threshold-driven coordinator and CLI (not acoustic signal extraction)
- `enrichment.py`: placeholder evaluators based on a common numeric threshold; not implemented acoustic, language, or longitudinal analytics
- `cli.py`: single-task audit, batch CSV processing, mock chat response, audit-chain check, and API startup
- `web/`: a standalone, deterministic JavaScript adaptation of the `agents/workers.py` thresholds, without server-side audit signing

Python rules: primary measurement **greater than 25** triggers a warning; secondary measurement **greater than 12** triggers a warning; a manually set critical flag changes the priority tier; certain keywords in the status descriptor trigger warnings. The `vocal_marker_ai` coordinator uses a different secondary threshold (**greater than 10**). Neither set of thresholds is clinically validated.

## Install and run

Requires Python 3.9+; CI tests Python 3.10–3.12.

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -e '.[api,test]'
python -m pytest -q
python cli.py audit --task-id DEMO-001 --target SAMPLE-001 --primary 29.4 --secondary 14.8
python cli.py batch -i sample.csv -o results.csv
python cli.py verify-audit
python cli.py serve --host 127.0.0.1 --port 8000
```

API documentation is available at `http://127.0.0.1:8000/docs`; `POST /api/audit` takes a `SystemTaskPayload`, while `GET /health` and `GET /metrics` provide basic JSON status. The mock chat endpoint does not contact any model provider.

For a container deployment, set a random signing key in the environment before using Compose:

```bash
export AUDIT_SECRET_KEY="$(python -c 'import secrets; print(secrets.token_hex(32))')"
docker compose up --build
```

The optional `AUDIT_LOG_READ_TOKEN` environment variable enables `GET /api/audit/logs` for requests supplying `X-Audit-Token`. Without it, that endpoint returns HTTP 403. Do not expose the API publicly without appropriate authentication, TLS, and operational controls.

## Security and data handling

The browser demonstration retains results only in tab memory and in JSON files explicitly exported by the user. The Python server stores its task dossiers and signed audit entries **in process memory**, not durable storage; entries and the auto-generated signing key do not survive a restart. Audit-chain verification recomputes each HMAC and verifies links between stored entries, but cannot prove the completeness of a truncated in-memory trail without an external trust anchor.

The identifier guard uses a small set of regular expressions and **is not a comprehensive PHI de-identification mechanism**. Never send identifiable patient data to this prototype. The fixed key formerly included in Compose must be treated as exposed if it was ever used and replaced in any deployment.

## Tests and limitations

```bash
python -m pytest -q
node --check web/app.js
node --test web/test_app.cjs
python simulator.py 100
```

The GitHub Actions CI workflow tests Python 3.10–3.12 and the browser's rule functions. It does not constitute clinical, security, or regulatory validation. Full speech biomarker processing would require verified audio I/O, signal-processing algorithms, reference datasets, analytical validation, and independent clinical evaluation.

Browser compatibility: current Chromium, Firefox, and Safari versions with standard ECMAScript and Blob downloads.

## License

MIT — see [LICENSE](LICENSE).
