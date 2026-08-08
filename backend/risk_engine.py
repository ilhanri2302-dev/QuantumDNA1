"""QuantumDNA deterministic risk scoring engine."""

from __future__ import annotations

import json


# Maximum contribution of each risk factor.
WEIGHT_QUANTUM = 30
WEIGHT_SENSITIVITY = 20
WEIGHT_RETENTION = 20
WEIGHT_EXPOSURE = 15
WEIGHT_DEPENDENCIES = 15


def level_points(weight: int) -> dict[str, int]:
    """Convert LOW/MEDIUM/HIGH/CRITICAL into weighted points."""
    third = weight / 3

    return {
        "LOW": 0,
        "MEDIUM": round(third),
        "HIGH": round(2 * third),
        "CRITICAL": weight,
    }


POINTS_20 = level_points(WEIGHT_SENSITIVITY)
POINTS_15 = level_points(WEIGHT_DEPENDENCIES)


# These are not Shor-vulnerable, but still deserve attention.
LEGACY_PARTIAL = {"SHA-1", "AES-128"}
LEGACY_PARTIAL_POINTS = 5


def risk_band(score: int) -> str:
    """Convert a numeric score into a risk category."""

    if score >= 81:
        return "CRITICAL"

    if score >= 61:
        return "HIGH"

    if score >= 31:
        return "MODERATE"

    return "LOW"


def retention_level(years: int) -> str:
    """Classify the length of required data confidentiality."""

    if years > 10:
        return "CRITICAL"

    if years >= 6:
        return "HIGH"

    if years >= 3:
        return "MEDIUM"

    return "LOW"


def dependency_level(count: int) -> str:
    """Classify blast-radius impact based on dependent assets."""

    if count >= 7:
        return "CRITICAL"

    if count >= 4:
        return "HIGH"

    if count >= 2:
        return "MEDIUM"

    return "LOW"


def calculate_risk(
    algorithm: str,
    quantum_vulnerable: bool,
    data_sensitivity: str,
    retention_years: int,
    internet_exposed: bool,
    dependency_count: int,
) -> dict:
    """
    Calculate the QuantumDNA prioritization score.

    This is an internal, deterministic scoring model.
    It is NOT an official NIST risk formula.
    """

    sensitivity = data_sensitivity.upper()

    if sensitivity == "MODERATE":
        sensitivity = "MEDIUM"

    if sensitivity not in POINTS_20:
        raise ValueError(
            "data_sensitivity must be LOW, MEDIUM, HIGH or CRITICAL"
        )

    if retention_years < 0:
        raise ValueError("retention_years cannot be negative")

    if dependency_count < 0:
        raise ValueError("dependency_count cannot be negative")

    # 1. Quantum vulnerability — maximum 30 points.
    if quantum_vulnerable:
        quantum_score = WEIGHT_QUANTUM
        quantum_reason = "algorithm is vulnerable to sufficiently capable quantum attacks"

    elif algorithm.upper() in LEGACY_PARTIAL:
        quantum_score = LEGACY_PARTIAL_POINTS
        quantum_reason = "algorithm has legacy or reduced security margin"

    else:
        quantum_score = 0
        quantum_reason = "algorithm is not classified as quantum-vulnerable"

    # 2. Data sensitivity — maximum 20 points.
    sensitivity_score = POINTS_20[sensitivity]

    # 3. Retention / HNDL exposure — maximum 20 points.
    retention_category = retention_level(retention_years)
    retention_score = POINTS_20[retention_category]

    # 4. Internet exposure — maximum 15 points.
    exposure_score = (
        WEIGHT_EXPOSURE
        if internet_exposed
        else 0
    )

    # 5. Dependency / blast radius — maximum 15 points.
    dependency_category = dependency_level(dependency_count)
    dependency_score = POINTS_15[dependency_category]

    # Final score.
    score = (
        quantum_score
        + sensitivity_score
        + retention_score
        + exposure_score
        + dependency_score
    )

    score = min(score, 100)

    risk_level = risk_band(score)

    explanation = (
        f"{algorithm} scored {score}/100 ({risk_level}). "
        f"Quantum factor: {quantum_score}/30 because {quantum_reason}. "
        f"Data sensitivity: {sensitivity_score}/20 ({sensitivity}). "
        f"Retention/HNDL: {retention_score}/20 "
        f"({retention_years} year(s)). "
        f"Internet exposure: {exposure_score}/15. "
        f"Dependency impact: {dependency_score}/15 "
        f"({dependency_count} dependent asset(s))."
    )

    return {
        "score": score,
        "risk_level": risk_level,
        "factors": {
            "quantum_vulnerability": quantum_score,
            "data_sensitivity": sensitivity_score,
            "retention_hndl": retention_score,
            "internet_exposure": exposure_score,
            "dependency_impact": dependency_score,
        },
        "explanation": explanation,
        "migration_priority": risk_level,
    }


if __name__ == "__main__":

    example = calculate_risk(
        algorithm="RSA-2048",
        quantum_vulnerable=True,
        data_sensitivity="CRITICAL",
        retention_years=10,
        internet_exposed=True,
        dependency_count=5,
    )

    print(json.dumps(example, indent=2))