"""Tests for the QuantumDNA cryptographic scanner."""

from __future__ import annotations

from pathlib import Path

import pytest

from crypto_knowledge import get_algorithm_info
from scanner import scan_directory


def write(root: Path, name: str, content: str) -> Path:
    """Write a file into a temp tree and return its path."""

    path = root / name
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    return path


# ------------------------------------------------------------------
# Detection
# ------------------------------------------------------------------

@pytest.mark.parametrize(
    "algorithm",
    [
        "RSA",
        "RSA-2048",
        "RSA-3072",
        "RSA-4096",
        "ECDSA",
        "ECDH",
        "AES-256",
        "SHA-256",
        "SHA-384",
        "SHA-512",
        "ML-KEM",
        "ML-DSA",
    ],
)
def test_detects_algorithm(temp_target, algorithm):
    write(temp_target, "app.py", f'algorithm = "{algorithm}"\n')
    findings = scan_directory(temp_target)
    detected = {f["algorithm"] for f in findings}
    assert algorithm in detected


def test_detects_bare_aes_without_false_positive(temp_target):
    write(temp_target, "app.py", 'cipher = "AES"\n')
    findings = scan_directory(temp_target)
    names = [f["algorithm"] for f in findings]
    assert "AES" in names
    # Bare AES must not swallow the sized variants.
    assert "AES-256" not in names and "AES-128" not in names


def test_aes_256_not_matched_as_bare_aes(temp_target):
    write(temp_target, "app.py", 'cipher = "AES-256"\n')
    findings = scan_directory(temp_target)
    names = [f["algorithm"] for f in findings]
    assert "AES-256" in names
    assert "AES" not in names


# ------------------------------------------------------------------
# Classification via the knowledge base
# ------------------------------------------------------------------

@pytest.mark.parametrize(
    "algorithm,expected_status",
    [
        ("RSA", "quantum vulnerable"),
        ("RSA-2048", "quantum vulnerable"),
        ("ECDSA", "quantum vulnerable"),
        ("ECDH", "quantum vulnerable"),
        ("AES-256", "comparatively quantum resilient"),
        ("SHA-256", "comparatively quantum resilient"),
        ("ML-KEM", "post-quantum ready"),
        ("ML-DSA", "post-quantum ready"),
    ],
)
def test_quantum_classification(algorithm, expected_status):
    info = get_algorithm_info(algorithm)
    assert info["quantum_status"] == expected_status


def test_findings_carry_knowledge_fields(temp_target):
    write(temp_target, "app.py", 'sig = "ECDSA"\n')
    finding = scan_directory(temp_target)[0]
    assert finding["role"] == "digital signature"
    assert finding["quantum_status"] == "quantum vulnerable"
    assert finding["explanation"]
    assert finding["migration_guidance"]


# ------------------------------------------------------------------
# Recursive scanning and file types
# ------------------------------------------------------------------

def test_recursive_scanning(temp_target):
    write(temp_target, "a.py", "x = 'RSA-2048'\n")
    write(temp_target, "nested/deep/b.py", "x = 'ML-KEM'\n")
    findings = scan_directory(temp_target)
    files = {f["file"] for f in findings}
    assert "a.py" in files
    assert "nested/deep/b.py" in files


@pytest.mark.parametrize(
    "ext",
    [".py", ".js", ".ts", ".java", ".cpp", ".yaml", ".yml",
     ".json", ".xml", ".c", ".h"],
)
def test_supported_extensions(temp_target, ext):
    write(temp_target, f"config{ext}", 'algo: "RSA-2048"\n')
    findings = scan_directory(temp_target)
    assert any(f["file"] == f"config{ext}" for f in findings)


def test_skips_generated_directories(temp_target):
    write(temp_target, "real.py", "x = 'RSA-2048'\n")
    write(temp_target, "node_modules/pkg/index.js", "x = 'ML-KEM'\n")
    write(temp_target, "venv/lib/site.py", "x = 'ECDH'\n")
    write(temp_target, ".git/config", "x = 'ECDSA'\n")
    write(temp_target, "build/out.js", "x = 'AES-256'\n")
    write(temp_target, "__pycache__/mod.py", "x = 'SHA-256'\n")

    findings = scan_directory(temp_target)
    files = {f["file"] for f in findings}
    assert files == {"real.py"}


def test_skips_binary_files(temp_target):
    write(temp_target, "real.py", "x = 'RSA-2048'\n")
    binary = temp_target / "blob.bin"
    binary.write_bytes(b"\x00\x01\x02RSA-2048\x00\xff")
    findings = scan_directory(temp_target)
    files = {f["file"] for f in findings}
    assert files == {"real.py"}


def test_unsupported_extension_ignored(temp_target):
    write(temp_target, "real.py", "x = 'RSA-2048'\n")
    write(temp_target, "data.xyz", "x = 'ML-KEM'\n")
    findings = scan_directory(temp_target)
    files = {f["file"] for f in findings}
    assert files == {"real.py"}


# ------------------------------------------------------------------
# Invalid and empty targets
# ------------------------------------------------------------------

def test_invalid_target_raises(temp_target):
    with pytest.raises(NotADirectoryError):
        scan_directory(temp_target / "does-not-exist")


def test_empty_target_returns_no_findings(temp_target):
    assert scan_directory(temp_target) == []


def test_no_findings_directory(temp_target):
    write(temp_target, "plain.py", "x = 1 + 1\n")
    assert scan_directory(temp_target) == []


def test_finding_id_is_stable(temp_target):
    write(temp_target, "app.py", "x = 'RSA-2048'\n")
    first = scan_directory(temp_target)
    second = scan_directory(temp_target)
    assert first[0]["id"] == second[0]["id"]
