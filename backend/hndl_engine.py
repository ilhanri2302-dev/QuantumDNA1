"""QuantumDNA Harvest-Now-Decrypt-Later exposure engine."""

from __future__ import annotations

import json


# Internal QuantumDNA model.
# This is NOT an official NIST formula.

WEIGHT_FUTURE = 50
WEIGHT_HARVEST = 30
WEIGHT_RETENTION = 20

INTERNET_BONUS = 10


LEVEL_POINTS = {
    "LOW": 0,
    "MEDIUM": 33,
    "HIGH": 67,
    "CRITICAL": 100,
}


FUTURE_DECRYPTABILITY = {
    "RSA": 100,
    "RSA-2048": 100,
    "RSA-3072": 100,
    "RSA-4096": 100,

    "ECDSA": 100,
    "ECDH": 100,
    "DH": 100,
    "DSA": 100,

    "AES-128": 45,
    "AES-256": 20,

    "SHA-1": 30,
    "SHA-256": 15,
    "SHA-384": 15,
    "SHA-512": 15,

    "ML-KEM": 5,
    "ML-DSA": 5,
    "SLH-DSA": 5,
}


DEFAULT_FUTURE_DECRYPTABILITY = 15


RECOMMENDATIONS = {
    "CRITICAL": (
        "Assume harvested ciphertext may become decryptable. "
        "Prioritize migration to post-quantum or hybrid cryptography."
    ),
    "HIGH": (
        "Prioritize post-quantum or hybrid migration and review "
        "long-lived sensitive data."
    ),
    "MODERATE": (
        "Plan post-quantum migration and review data retention "
        "and exposure."
    ),
    "LOW": (
        "No immediate HNDL action. Continue monitoring "
        "cryptographic readiness."
    ),
}


def exposure_band(score: int) -> str:
    """Convert a 0-100 score into an HNDL exposure level."""

    if score >= 81:
        return "CRITICAL"

    if score >= 61:
        return "HIGH"

    if score >= 31:
        return "MODERATE"

    return "LOW"


def retention_level(years: int) -> str:
    """Classify how long confidentiality must be preserved."""

    if years > 10:
        return "CRITICAL"

    if years >= 6:
        return "HIGH"

    if years >= 3:
        return "MEDIUM"

    return "LOW"


def sensitivity_level(data_sensitivity: str) -> str:
    """Validate and normalize data sensitivity."""

    level = data_sensitivity.upper()

    if level == "MODERATE":
        level = "MEDIUM"

    if level not in LEVEL_POINTS:
        raise ValueError(
            "data_sensitivity must be LOW, MEDIUM, HIGH or CRITICAL"
        )

    return level


def future_decryptability(
    algorithm: str,
    quantum_vulnerable: bool,
) -> int:
    """
    Estimate concern that protected data could become
    decryptable by a future quantum computer.
    """

    if quantum_vulnerable:
        return 100

    return FUTURE_DECRYPTABILITY.get(
        algorithm.upper(),
        DEFAULT_FUTURE_DECRYPTABILITY,
    )


def assess_hndl(
    algorithm: str,
    quantum_vulnerable: bool,
    data_sensitivity: str,
    retention_years: int,
    internet_exposed: bool,
) -> dict:
    """
    Calculate an internal QuantumDNA HNDL exposure assessment.
    """

    sensitivity = sensitivity_level(data_sensitivity)

    if retention_years < 0:
        raise ValueError(
            "retention_years cannot be negative"
        )

    # Component 1: how valuable the harvested data is.
    harvest_value = LEVEL_POINTS[sensitivity]

    # Component 2: how concerning future quantum decryption is.
    decryptability = future_decryptability(
        algorithm,
        quantum_vulnerable,
    )

    # Component 3: how long confidentiality must be preserved.
    retention_risk = LEVEL_POINTS[
        retention_level(retention_years)
    ]

    # Weighted HNDL score.
    score = round(
        (
            WEIGHT_FUTURE * decryptability
            + WEIGHT_HARVEST * harvest_value
            + WEIGHT_RETENTION * retention_risk
        ) / 100
    )

    # Internet exposure increases harvesting opportunity.
    if internet_exposed:
        score += INTERNET_BONUS

    score = min(score, 100)

    exposure = exposure_band(score)

    exposure_reason = (
        f"{algorithm} has an HNDL exposure score of "
        f"{score}/100 ({exposure}). "
        f"Future decryptability: {decryptability}/100. "
        f"Harvest value: {harvest_value}/100 "
        f"({sensitivity} sensitivity). "
        f"Retention risk: {retention_risk}/100 "
        f"({retention_years} year(s)). "
        f"Internet exposure: "
        f"{'yes' if internet_exposed else 'no'}."
    )

    if internet_exposed:
        exposure_reason += (
            f" Internet exposure adds "
            f"{INTERNET_BONUS} points for increased "
            f"harvesting opportunity."
        )

    return {
        "exposure": exposure,
        "score": score,
        "harvest_value": harvest_value,
        "future_decryptability": decryptability,
        "retention_risk": retention_risk,
        "exposure_reason": exposure_reason,
        "recommendation": RECOMMENDATIONS[exposure],
    }


if __name__ == "__main__":

    example = assess_hndl(
        algorithm="RSA-2048",
        quantum_vulnerable=True,
        data_sensitivity="CRITICAL",
        retention_years=10,
        internet_exposed=True,
    )

    print(json.dumps(example, indent=2))