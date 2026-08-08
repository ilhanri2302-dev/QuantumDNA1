"""QuantumDNA FastAPI orchestration layer."""

from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from blast_radius import calculate_blast_radius
from hndl_engine import assess_hndl
from risk_engine import calculate_risk
from scanner import scan_directory


app = FastAPI(
    title="QuantumDNA",
    description="Quantum Readiness & Cryptographic Blast-Radius Platform",
    version="0.1.0",
)


# Allow the local React development server to communicate with FastAPI.
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# MVP demonstration dependency graph.
# This is NOT automatically inferred from arbitrary source code yet.
DEMO_DEPENDENCY_GRAPH: dict[str, list[str]] = {
    "RSA-2048": [
        "payment-api",
        "auth-service",
        "api-gateway",
    ],
    "ECDSA": [
        "auth-service",
        "identity-service",
    ],
    "ECDH": [
        "auth-service",
        "secure-channel",
    ],
    "payment-api": [
        "payment-db",
    ],
    "auth-service": [
        "identity-db",
    ],
    "api-gateway": [],
    "identity-service": [
        "identity-db",
    ],
    "secure-channel": [
        "gateway-service",
    ],
    "payment-db": [],
    "identity-db": [],
    "gateway-service": [],
}


# Deterministic demonstration context.
SENSITIVITY_BY_CATEGORY = {
    "ASYMMETRIC": "CRITICAL",
    "KEY_ESTABLISHMENT": "CRITICAL",
    "DIGITAL_SIGNATURE": "HIGH",
    "SYMMETRIC": "MEDIUM",
    "HASH": "MEDIUM",
    "POST_QUANTUM": "HIGH",
}


RETENTION_BY_SENSITIVITY = {
    "CRITICAL": 10,
    "HIGH": 6,
    "MEDIUM": 3,
    "LOW": 1,
}


INTERNET_EXPOSED_CATEGORIES = {
    "ASYMMETRIC",
    "KEY_ESTABLISHMENT",
}


class ScanRequest(BaseModel):
    """Request body for POST /scan."""

    path: str


def demonstration_context(category: str) -> dict:
    """Return deterministic MVP context for a crypto category."""

    sensitivity = SENSITIVITY_BY_CATEGORY.get(
        category,
        "MEDIUM",
    )

    return {
        "data_sensitivity": sensitivity,
        "retention_years": RETENTION_BY_SENSITIVITY[sensitivity],
        "internet_exposed": (
            category in INTERNET_EXPOSED_CATEGORIES
        ),
    }


def enrich_finding(finding: dict) -> dict:
    """Attach risk, HNDL and blast-radius assessments."""

    algorithm = finding["algorithm"]

    context = demonstration_context(
        finding["category"]
    )

    dependency_count = len(
        DEMO_DEPENDENCY_GRAPH.get(
            algorithm,
            []
        )
    )

    risk = calculate_risk(
        algorithm=algorithm,
        quantum_vulnerable=finding["quantum_vulnerable"],
        data_sensitivity=context["data_sensitivity"],
        retention_years=context["retention_years"],
        internet_exposed=context["internet_exposed"],
        dependency_count=dependency_count,
    )

    hndl = assess_hndl(
        algorithm=algorithm,
        quantum_vulnerable=finding["quantum_vulnerable"],
        data_sensitivity=context["data_sensitivity"],
        retention_years=context["retention_years"],
        internet_exposed=context["internet_exposed"],
    )

    blast_radius = None

    if algorithm in DEMO_DEPENDENCY_GRAPH:
        blast_radius = calculate_blast_radius(
            algorithm,
            DEMO_DEPENDENCY_GRAPH,
        )

    return {
        **finding,
        "context": context,
        "risk": risk,
        "hndl": hndl,
        "blast_radius": blast_radius,
    }


@app.get("/")
def root():
    return {
        "project": "QuantumDNA",
        "status": "online",
    }


@app.get("/health")
def health():
    return {
        "status": "healthy",
    }


@app.post("/scan")
def scan(request: ScanRequest):
    """
    Scan a directory and enrich crypto findings with
    quantum risk, HNDL and blast-radius assessments.
    """

    path = Path(request.path)

    if not path.is_dir():
        raise HTTPException(
            status_code=400,
            detail=f"Path is not a directory: {request.path}",
        )

    try:
        findings = scan_directory(path)

    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail=f"Scan failed: {error}",
        ) from error

    # Prevent duplicate scoring of the same algorithm,
    # file and line combination.
    seen: set[tuple[str, str, int]] = set()

    enriched_findings = []

    for finding in findings:

        key = (
            finding["algorithm"],
            finding["file"],
            finding["line"],
        )

        if key in seen:
            continue

        seen.add(key)

        enriched_findings.append(
            enrich_finding(finding)
        )

    summary = {
        "path": request.path,

        "files_scanned": len(
            {
                finding["file"]
                for finding in enriched_findings
            }
        ),

        "crypto_findings": len(
            enriched_findings
        ),

        "quantum_vulnerable": sum(
            1
            for finding in enriched_findings
            if finding["quantum_vulnerable"]
        ),

        "post_quantum": sum(
            1
            for finding in enriched_findings
            if finding["category"] == "POST_QUANTUM"
        ),

        "critical_risk_assets": sum(
            1
            for finding in enriched_findings
            if finding["risk"]["risk_level"] == "CRITICAL"
        ),
    }

    return {
        "summary": summary,

        "findings": enriched_findings,

        "dependency_graph": {
            "mode": "DEMO",
            "description": (
                "Demonstration dependency graph for the MVP. "
                "It is not automatically inferred from source code."
            ),
        },
    }                                   