"""QuantumDNA cryptographic knowledge base.

Central source of truth for every recognized algorithm: its
cryptographic category and role, quantum-resilience status, a
plain-language explanation, and migration guidance.

Everything else (scanner classification, findings, UI labels)
reads from this module so algorithm information is never
scattered through the codebase.

This is an internal QuantumDNA POC knowledge base.
It is NOT a formal NIST or industry-standard catalogue.
"""

from __future__ import annotations

# ------------------------------------------------------------------
# Quantum status vocabulary (accurate, non-alarmist language).
# ------------------------------------------------------------------

QUANTUM_VULNERABLE = "quantum vulnerable"
COMPARATIVELY_RESILIENT = "comparatively quantum resilient"
POST_QUANTUM_READY = "post-quantum ready"

# Cryptographic categories used by the scanner and the API.
ASYMMETRIC = "ASYMMETRIC"
DIGITAL_SIGNATURE = "DIGITAL_SIGNATURE"
KEY_ESTABLISHMENT = "KEY_ESTABLISHMENT"
SYMMETRIC = "SYMMETRIC"
HASH = "HASH"
POST_QUANTUM = "POST_QUANTUM"

# Canonical roles used in findings and the UI inventory.
ROLE_PUBLIC_KEY = "public-key cryptography"
ROLE_SIGNATURE = "digital signature"
ROLE_KEY_EXCHANGE = "key exchange / key establishment"
ROLE_SYMMETRIC = "symmetric encryption"
ROLE_HASH = "cryptographic hash"
ROLE_PQ_KEY_EXCHANGE = "post-quantum key establishment"
ROLE_PQ_SIGNATURE = "post-quantum digital signature"


# ------------------------------------------------------------------
# The knowledge base itself.
# ------------------------------------------------------------------

ALGORITHMS: dict[str, dict] = {
    # --------------------------------------------------------------
    # Quantum-vulnerable classical cryptography
    # --------------------------------------------------------------
    "RSA": {
        "category": ASYMMETRIC,
        "role": ROLE_PUBLIC_KEY,
        "quantum_status": QUANTUM_VULNERABLE,
        "quantum_vulnerable": True,
        "explanation": (
            "Asymmetric public-key cryptography. Shor's algorithm on a "
            "sufficiently capable quantum computer could factor RSA moduli, "
            "threatening both confidentiality and signature security."
        ),
        "migration_guidance": (
            "Migrate RSA key establishment toward ML-KEM (or a hybrid "
            "RSA + ML-KEM construction) and RSA signatures toward ML-DSA."
        ),
    },
    "RSA-2048": {
        "category": ASYMMETRIC,
        "role": ROLE_PUBLIC_KEY,
        "quantum_status": QUANTUM_VULNERABLE,
        "quantum_vulnerable": True,
        "explanation": (
            "RSA with a 2048-bit modulus. Shor's algorithm on a sufficiently "
            "capable quantum computer could factor the modulus, exposing "
            "encrypted data and allowing signature forgery."
        ),
        "migration_guidance": (
            "Highest migration priority. Move RSA-2048 key establishment to "
            "ML-KEM (or hybrid RSA + ML-KEM) and signatures to ML-DSA, "
            "especially for internet-exposed or long-lived data."
        ),
    },
    "RSA-3072": {
        "category": ASYMMETRIC,
        "role": ROLE_PUBLIC_KEY,
        "quantum_status": QUANTUM_VULNERABLE,
        "quantum_vulnerable": True,
        "explanation": (
            "RSA with a 3072-bit modulus. A larger key raises the classical "
            "cost, but Shor's algorithm still threatens the factorization "
            "problem that RSA relies on."
        ),
        "migration_guidance": (
            "Plan migration of RSA-3072 key establishment to ML-KEM "
            "(or hybrid RSA + ML-KEM) and signatures to ML-DSA."
        ),
    },
    "RSA-4096": {
        "category": ASYMMETRIC,
        "role": ROLE_PUBLIC_KEY,
        "quantum_status": QUANTUM_VULNERABLE,
        "quantum_vulnerable": True,
        "explanation": (
            "RSA with a 4096-bit modulus. Larger keys delay but do not "
            "prevent the quantum threat: Shor's algorithm scales "
            "polynomially with the modulus size."
        ),
        "migration_guidance": (
            "Begin migration of RSA-4096 key establishment to ML-KEM "
            "(or hybrid RSA + ML-KEM) and signatures to ML-DSA."
        ),
    },
    "ECDSA": {
        "category": DIGITAL_SIGNATURE,
        "role": ROLE_SIGNATURE,
        "quantum_status": QUANTUM_VULNERABLE,
        "quantum_vulnerable": True,
        "explanation": (
            "Elliptic-curve digital signature. Shor's algorithm could "
            "recover the private key from the public key, enabling "
            "signature forgery."
        ),
        "migration_guidance": (
            "Migrate digital signatures toward ML-DSA. ECDSA is not a "
            "replacement target for key establishment."
        ),
    },
    "ECDH": {
        "category": KEY_ESTABLISHMENT,
        "role": ROLE_KEY_EXCHANGE,
        "quantum_status": QUANTUM_VULNERABLE,
        "quantum_vulnerable": True,
        "explanation": (
            "Elliptic-curve key exchange. Shor's algorithm could recover "
            "the shared secret from the public key exchange, exposing "
            "negotiated session keys."
        ),
        "migration_guidance": (
            "Migrate key exchange toward ML-KEM. ECDH is a key "
            "establishment primitive, so ML-KEM is the matching "
            "post-quantum direction."
        ),
    },
    "DH": {
        "category": KEY_ESTABLISHMENT,
        "role": ROLE_KEY_EXCHANGE,
        "quantum_status": QUANTUM_VULNERABLE,
        "quantum_vulnerable": True,
        "explanation": (
            "Classical Diffie-Hellman key exchange. Shor's algorithm "
            "could recover the shared secret from the public exchange."
        ),
        "migration_guidance": (
            "Migrate Diffie-Hellman key exchange toward ML-KEM."
        ),
    },
    "DSA": {
        "category": DIGITAL_SIGNATURE,
        "role": ROLE_SIGNATURE,
        "quantum_status": QUANTUM_VULNERABLE,
        "quantum_vulnerable": True,
        "explanation": (
            "Classical digital signature algorithm. Its security rests "
            "on discrete logarithms, which Shor's algorithm could solve."
        ),
        "migration_guidance": (
            "Migrate DSA signatures toward ML-DSA."
        ),
    },

    # --------------------------------------------------------------
    # Comparatively quantum-resilient classical cryptography
    # --------------------------------------------------------------
    "AES": {
        "category": SYMMETRIC,
        "role": ROLE_SYMMETRIC,
        "quantum_status": COMPARATIVELY_RESILIENT,
        "quantum_vulnerable": False,
        "explanation": (
            "Symmetric encryption. AES is not broken by Shor's algorithm; "
            "quantum search (Grover) roughly halves effective key strength, "
            "so larger key sizes retain a wide margin."
        ),
        "migration_guidance": (
            "No cipher replacement needed. Keep AES and pair it with "
            "post-quantum key establishment (e.g., ML-KEM) so the key "
            "exchange itself is protected."
        ),
    },
    "AES-128": {
        "category": SYMMETRIC,
        "role": ROLE_SYMMETRIC,
        "quantum_status": COMPARATIVELY_RESILIENT,
        "quantum_vulnerable": False,
        "explanation": (
            "AES with a 128-bit key. Grover's algorithm could reduce its "
            "effective strength to roughly 64 bits, which is a reduced "
            "but not immediate security margin."
        ),
        "migration_guidance": (
            "Prefer AES-256 for data requiring long-term confidentiality. "
            "Use post-quantum key establishment (ML-KEM) for key exchange."
        ),
    },
    "AES-256": {
        "category": SYMMETRIC,
        "role": ROLE_SYMMETRIC,
        "quantum_status": COMPARATIVELY_RESILIENT,
        "quantum_vulnerable": False,
        "explanation": (
            "AES with a 256-bit key. Not broken by Shor's algorithm; "
            "Grover's search leaves AES-256 with an effective strength "
            "near 128 bits, a wide security margin."
        ),
        "migration_guidance": (
            "No cipher replacement needed. Retain AES-256 and protect the "
            "key exchange with ML-KEM (or hybrid) cryptography."
        ),
    },
    "SHA-1": {
        "category": HASH,
        "role": ROLE_HASH,
        "quantum_status": COMPARATIVELY_RESILIENT,
        "quantum_vulnerable": False,
        "explanation": (
            "Legacy 160-bit hash. SHA-1 is already deprecated for security "
            "because of classical collision attacks, independent of "
            "quantum considerations."
        ),
        "migration_guidance": (
            "Retire SHA-1 regardless of quantum concerns and move to "
            "SHA-256 or stronger."
        ),
    },
    "SHA-256": {
        "category": HASH,
        "role": ROLE_HASH,
        "quantum_status": COMPARATIVELY_RESILIENT,
        "quantum_vulnerable": False,
        "explanation": (
            "256-bit cryptographic hash. Not broken by Shor's algorithm; "
            "quantum search affects preimage resistance, and a 256-bit "
            "output retains a wide security margin."
        ),
        "migration_guidance": (
            "No replacement needed for quantum reasons. Keep SHA-256 for "
            "hashing and integrity checks."
        ),
    },
    "SHA-384": {
        "category": HASH,
        "role": ROLE_HASH,
        "quantum_status": COMPARATIVELY_RESILIENT,
        "quantum_vulnerable": False,
        "explanation": (
            "384-bit cryptographic hash. Comparatively quantum resilient "
            "with a very wide security margin."
        ),
        "migration_guidance": (
            "No replacement needed for quantum reasons. Suitable where a "
            "higher security margin is required."
        ),
    },
    "SHA-512": {
        "category": HASH,
        "role": ROLE_HASH,
        "quantum_status": COMPARATIVELY_RESILIENT,
        "quantum_vulnerable": False,
        "explanation": (
            "512-bit cryptographic hash. Comparatively quantum resilient "
            "with a very wide security margin."
        ),
        "migration_guidance": (
            "No replacement needed for quantum reasons. Suitable where a "
            "higher security margin is required."
        ),
    },

    # --------------------------------------------------------------
    # Post-quantum ready cryptography
    # --------------------------------------------------------------
    "ML-KEM": {
        "category": POST_QUANTUM,
        "role": ROLE_PQ_KEY_EXCHANGE,
        "quantum_status": POST_QUANTUM_READY,
        "quantum_vulnerable": False,
        "explanation": (
            "NIST-standardized post-quantum key-establishment mechanism "
            "(Kyber). Designed to resist attacks from quantum computers."
        ),
        "migration_guidance": (
            "Already post-quantum ready for key establishment. Monitor "
            "standardization and interoperability; do not replace with "
            "ML-DSA, which is a signature algorithm."
        ),
    },
    "ML-DSA": {
        "category": POST_QUANTUM,
        "role": ROLE_PQ_SIGNATURE,
        "quantum_status": POST_QUANTUM_READY,
        "quantum_vulnerable": False,
        "explanation": (
            "NIST-standardized post-quantum digital signature algorithm "
            "(Dilithium). Designed to resist attacks from quantum computers."
        ),
        "migration_guidance": (
            "Already post-quantum ready for digital signatures. Monitor "
            "standardization and interoperability; do not replace with "
            "ML-KEM, which is a key-establishment mechanism."
        ),
    },
    "SLH-DSA": {
        "category": POST_QUANTUM,
        "role": ROLE_PQ_SIGNATURE,
        "quantum_status": POST_QUANTUM_READY,
        "quantum_vulnerable": False,
        "explanation": (
            "NIST-standardized hash-based post-quantum signature algorithm "
            "(SPHINCS+). Signature-heavy but conservative in its "
            "security assumptions."
        ),
        "migration_guidance": (
            "Already post-quantum ready. Consider SLH-DSA where "
            "hash-based conservative signatures are preferred."
        ),
    },
}


def get_algorithm(name: str) -> dict | None:
    """Return knowledge-base metadata for an algorithm name."""

    return ALGORITHMS.get(name)


def get_algorithm_info(name: str) -> dict:
    """Return safe metadata for any name (unknown names get a fallback)."""

    info = ALGORITHMS.get(name)

    if info is not None:
        return info

    return {
        "category": "UNKNOWN",
        "role": "unclassified",
        "quantum_status": COMPARATIVELY_RESILIENT,
        "quantum_vulnerable": False,
        "explanation": (
            f"{name} is not in the QuantumDNA knowledge base."
        ),
        "migration_guidance": (
            "Review the algorithm manually before planning migration."
        ),
    }


def migration_direction(algorithm: str) -> dict:
    """Return the POC post-quantum direction for an algorithm."""

    name = algorithm.upper()
    info = get_algorithm_info(algorithm)
    role = info["role"]
    category = info["category"]

    if category == POST_QUANTUM:
        return {
            "current": algorithm,
            "target": "NONE — already post-quantum ready",
            "phase": "READY",
        }

    if "key" in role or category in (KEY_ESTABLISHMENT,):
        return {
            "current": algorithm,
            "target": "ML-KEM",
            "phase": "HYBRID → ML-KEM",
        }

    if "signature" in role or category == DIGITAL_SIGNATURE:
        return {
            "current": algorithm,
            "target": "ML-DSA",
            "phase": "HYBRID → ML-DSA",
        }

    if name.startswith("AES") or category == SYMMETRIC:
        return {
            "current": algorithm,
            "target": "RETAIN + PQ KEY EXCHANGE",
            "phase": "KEEP CIPHER",
        }

    if category == HASH:
        return {
            "current": algorithm,
            "target": "RETAIN",
            "phase": "KEEP",
        }

    return {
        "current": algorithm,
        "target": "REVIEW",
        "phase": "MANUAL REVIEW",
    }
