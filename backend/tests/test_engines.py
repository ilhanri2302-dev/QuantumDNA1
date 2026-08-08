"""Tests for the QuantumDNA scoring engines."""

from __future__ import annotations

import pytest

from blast_radius import calculate_blast_radius
from crypto_knowledge import migration_direction
from hndl_engine import assess_hndl
from risk_engine import calculate_risk


# ------------------------------------------------------------------
# Risk engine
# ------------------------------------------------------------------

def test_risk_quantum_vulnerable_scores_high():
    result = calculate_risk(
        algorithm="RSA-2048",
        quantum_vulnerable=True,
        data_sensitivity="CRITICAL",
        retention_years=10,
        internet_exposed=True,
        dependency_count=5,
    )
    assert result["score"] >= 61
    assert result["risk_level"] in {"HIGH", "CRITICAL"}
    assert result["factors"]["quantum_vulnerability"] == 30
    assert "explanation" in result


def test_risk_pq_ready_scores_low():
    result = calculate_risk(
        algorithm="ML-KEM",
        quantum_vulnerable=False,
        data_sensitivity="MEDIUM",
        retention_years=3,
        internet_exposed=False,
        dependency_count=0,
    )
    assert result["score"] < 31
    assert result["risk_level"] == "LOW"


def test_risk_is_explainable():
    result = calculate_risk(
        algorithm="ECDSA",
        quantum_vulnerable=True,
        data_sensitivity="HIGH",
        retention_years=6,
        internet_exposed=True,
        dependency_count=2,
    )
    assert "scored" in result["explanation"]
    assert "Quantum factor" in result["explanation"]
    assert "Data sensitivity" in result["explanation"]


def test_risk_rejects_bad_inputs():
    with pytest.raises(ValueError):
        calculate_risk(
            algorithm="RSA",
            quantum_vulnerable=True,
            data_sensitivity="INVALID",
            retention_years=5,
            internet_exposed=False,
            dependency_count=0,
        )

    with pytest.raises(ValueError):
        calculate_risk(
            algorithm="RSA",
            quantum_vulnerable=True,
            data_sensitivity="HIGH",
            retention_years=-1,
            internet_exposed=False,
            dependency_count=0,
        )


# ------------------------------------------------------------------
# HNDL engine
# ------------------------------------------------------------------

def test_hndl_high_for_sensitive_long_lived_vulnerable():
    result = assess_hndl(
        algorithm="RSA-2048",
        quantum_vulnerable=True,
        data_sensitivity="CRITICAL",
        retention_years=10,
        internet_exposed=True,
    )
    assert result["exposure"] in {"HIGH", "CRITICAL"}
    assert result["future_decryptability"] == 100
    assert result["harvest_value"] == 100
    assert "recommendation" in result


def test_hndl_low_for_pq_ready():
    result = assess_hndl(
        algorithm="ML-KEM",
        quantum_vulnerable=False,
        data_sensitivity="MEDIUM",
        retention_years=3,
        internet_exposed=False,
    )
    assert result["exposure"] == "LOW"


def test_hndl_rejects_invalid_sensitivity():
    with pytest.raises(ValueError):
        assess_hndl(
            algorithm="RSA",
            quantum_vulnerable=True,
            data_sensitivity="NOPE",
            retention_years=5,
            internet_exposed=False,
        )


# ------------------------------------------------------------------
# Blast radius engine
# ------------------------------------------------------------------

def test_blast_radius_traverses_downstream():
    graph = {
        "rsa-payment": ["payment-api", "auth-service", "api-gateway"],
        "payment-api": ["payment-db"],
        "auth-service": ["identity-db"],
        "api-gateway": [],
        "payment-db": [],
        "identity-db": [],
    }
    result = calculate_blast_radius("rsa-payment", graph)
    assert result["affected_asset_count"] == 5
    assert result["dependency_depth"] == 2
    assert result["blast_radius_score"] > 0
    assert result["blast_radius_level"] == "HIGH"


def test_blast_radius_handles_cycles():
    graph = {"a": ["b"], "b": ["a", "c"], "c": []}
    result = calculate_blast_radius("a", graph)
    assert result["affected_asset_count"] == 2
    assert "a" not in result["affected_assets"]


def test_blast_radius_missing_asset():
    result = calculate_blast_radius("ghost", {"a": []})
    assert result["affected_asset_count"] == 0
    assert result["blast_radius_score"] == 0


def test_blast_radius_does_not_mutate_input():
    graph = {"a": ["b"], "b": ["c"], "c": []}
    snapshot = {"a": ["b"], "b": ["c"], "c": []}
    calculate_blast_radius("a", graph)
    assert graph == snapshot


# ------------------------------------------------------------------
# Migration direction (Phase 7)
# ------------------------------------------------------------------

def test_migration_direction_role_matching():
    assert migration_direction("ECDH")["target"] == "ML-KEM"
    assert migration_direction("ECDSA")["target"] == "ML-DSA"
    assert migration_direction("RSA-2048")["target"] == "ML-KEM"
    # ML-KEM and ML-DSA are NOT interchangeable.
    assert migration_direction("ML-KEM")["target"].startswith("NONE")
    assert migration_direction("ML-DSA")["target"].startswith("NONE")


def test_migration_direction_retains_resilient():
    assert migration_direction("AES-256")["target"].startswith("RETAIN")
    assert migration_direction("SHA-256")["target"] == "RETAIN"
