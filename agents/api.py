"""
FastAPI REST API Server for Speech Biomarker Als Parkinson.
"""
import hmac
import os
from typing import Dict, Any, List
from fastapi import FastAPI, Header, HTTPException
from pydantic import BaseModel
from .base import AuditLogger, PHIGuard, SecurityException
from .models import SystemTaskPayload, ConsensusDossier
from .supervisor import SystemSupervisor

supervisor = SystemSupervisor(model_provider="mock")

app = FastAPI(
    title="Speech Biomarker Als Parkinson API",
    description="Experimental numeric threshold evaluation (not a clinical diagnostic system)",
    version="3.0.0-ENTERPRISE",
)


class ChatRequest(BaseModel):
    query: str


@app.get("/health")
def health():
    return {"status": "HEALTHY", "service": "speech-biomarker-als-parkinson", "domain": "Clinical & Biomedical AI", "standard": "Unvalidated prototype thresholds", "version": "3.0.0-ENTERPRISE"}


@app.get("/metrics")
def metrics():
    return {
        "dossiers_processed_total": len(supervisor.dossier_registry),
        "audit_blocks_total": len(AuditLogger.get_trail()),
        "system_status": "ACTIVE"
    }


@app.post("/api/audit")
def api_audit(payload: SystemTaskPayload):
    try:
        dossier = supervisor.process_task(payload)
    except SecurityException:
        raise HTTPException(status_code=422, detail="Input contains a disallowed identifier") from None
    return dossier.to_dict()


@app.post("/api/chat")
def api_chat(req: ChatRequest):
    try:
        ans = supervisor.query_supervisory_chat(req.query)
        return {"response": ans}
    except SecurityException:
        raise HTTPException(status_code=422, detail="Input contains a disallowed identifier") from None


@app.get("/api/audit/logs")
def api_audit_logs(x_audit_token: str = Header(default="")):
    token = os.environ.get("AUDIT_LOG_READ_TOKEN", "")
    if not token or not hmac.compare_digest(x_audit_token, token):
        raise HTTPException(status_code=403, detail="Audit log access is disabled or unauthorized")
    return {"audit_trail": AuditLogger.get_trail(), "verified": AuditLogger.verify_integrity()}
