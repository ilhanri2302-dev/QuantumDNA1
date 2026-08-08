"""QuantumDNA cryptographic discovery engine."""

from __future__ import annotations

import hashlib
import os
import re
from pathlib import Path

from crypto_knowledge import get_algorithm_info, migration_direction


SUPPORTED_EXTENSIONS = {
    ".py", ".js", ".jsx", ".ts", ".tsx", ".java",
    ".cpp", ".c", ".h", ".hpp",
    ".json", ".yaml", ".yml", ".xml", ".pem",
    ".conf", ".cfg", ".txt"
}

SKIP_DIRECTORIES = {
    "venv",
    ".venv",
    "node_modules",
    ".git",
    "__pycache__",
    "dist",
    "build"
}

MAX_FILE_SIZE = 5 * 1024 * 1024


# Detection patterns only. Classification metadata (category,
# role, quantum status, guidance) lives in crypto_knowledge.py.
ALGORITHMS = [
    # Quantum-vulnerable asymmetric cryptography
    ("RSA-4096", r"\bRSA-4096\b", 0.99),
    ("RSA-3072", r"\bRSA-3072\b", 0.99),
    ("RSA-2048", r"\bRSA-2048\b", 0.99),
    ("RSA", r"\bRSA\b(?!-\d{3,4})", 0.90),

    ("ECDSA", r"\bECDSA\b", 0.99),
    ("ECDH", r"\bECDH\b", 0.98),
    ("DH", r"\bDH\b", 0.85),
    ("DSA", r"(?<!ML-)\bDSA\b", 0.95),

    # Symmetric cryptography
    ("AES-256", r"\bAES[-_]?256\b", 0.98),
    ("AES-128", r"\bAES[-_]?128\b", 0.98),
    ("AES", r"\bAES\b(?![-_]?\d{3})", 0.90),

    # Hashing
    ("SHA-1", r"\bSHA[-_]?1\b", 0.99),
    ("SHA-256", r"\bSHA[-_]?256\b", 0.99),
    ("SHA-384", r"\bSHA[-_]?384\b", 0.99),
    ("SHA-512", r"\bSHA[-_]?512\b", 0.99),

    # Post-quantum cryptography
    ("ML-KEM", r"\bML[-_]?KEM\b", 0.98),
    ("ML-DSA", r"\bML[-_]?DSA\b", 0.98),
    ("SLH-DSA", r"\bSLH[-_]?DSA\b", 0.98),
]


COMPILED_ALGORITHMS = [
    (
        name,
        re.compile(pattern, re.IGNORECASE),
        confidence
    )
    for name, pattern, confidence in ALGORITHMS
]


def is_binary(data: bytes) -> bool:
    """Detect likely binary files using a simple NUL-byte check."""
    return b"\x00" in data[:8192]


def iter_files(root: Path):
    """Recursively find supported files while skipping unnecessary folders."""
    for directory, dirnames, filenames in os.walk(root):

        dirnames[:] = [
            d for d in dirnames
            if d not in SKIP_DIRECTORIES
        ]

        for filename in filenames:
            path = Path(directory) / filename

            try:
                if (
                    path.suffix.lower() in SUPPORTED_EXTENSIONS
                    and path.stat().st_size <= MAX_FILE_SIZE
                ):
                    yield path
            except OSError:
                continue


def create_finding_id(
    file_path: str,
    line_number: int,
    algorithm: str,
    matched_text: str
) -> str:
    """Create a stable ID for a cryptographic finding."""

    value = f"{file_path}:{line_number}:{algorithm}:{matched_text}"

    return hashlib.sha256(
        value.encode("utf-8")
    ).hexdigest()[:12]


def scan_directory(root: str | Path) -> list[dict]:
    """
    Recursively scan a directory for cryptographic algorithms.

    Returns a list of JSON-compatible findings.
    """

    root = Path(root)

    if not root.is_dir():
        raise NotADirectoryError(
            f"Directory not found: {root}"
        )

    findings = []

    for path in iter_files(root):

        try:
            raw_data = path.read_bytes()
        except OSError:
            continue

        if is_binary(raw_data):
            continue

        text = raw_data.decode(
            "utf-8",
            errors="replace"
        )

        relative_path = path.relative_to(root).as_posix()

        for line_number, line in enumerate(
            text.splitlines(),
            start=1
        ):

            for (
                name,
                pattern,
                confidence
            ) in COMPILED_ALGORITHMS:

                match = pattern.search(line)

                if not match:
                    continue

                matched_text = match.group(0)

                info = get_algorithm_info(name)
                direction = migration_direction(name)

                findings.append({
                    "id": create_finding_id(
                        relative_path,
                        line_number,
                        name,
                        matched_text
                    ),
                    "algorithm": name,
                    "file": relative_path,
                    "line": line_number,
                    "matched_text": matched_text,
                    "category": info["category"],
                    "quantum_vulnerable": info["quantum_vulnerable"],
                    "quantum_status": info["quantum_status"],
                    "role": info["role"],
                    "explanation": info["explanation"],
                    "migration_guidance": info["migration_guidance"],
                    "migration_target": direction["target"],
                    "migration_phase": direction["phase"],
                    "confidence": confidence,
                })

    return findings


if __name__ == "__main__":
    import argparse
    import json

    parser = argparse.ArgumentParser(
        description="QuantumDNA cryptographic scanner"
    )

    parser.add_argument(
        "path",
        help="Directory to scan"
    )

    args = parser.parse_args()

    results = scan_directory(args.path)

    print(
        json.dumps(
            results,
            indent=2
        )
    )