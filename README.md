# QuantumDNA

**Quantum Readiness & Cryptographic Blast-Radius Platform — "Cryptographic Genome Intelligence"**

QuantumDNA scans a software target, detects cryptographic algorithms in source
code and configuration files, classifies their quantum-resilience, and
evaluates contextual risk: Harvest-Now-Decrypt-Later (HNDL) exposure,
cryptographic blast radius, and migration priority.

> This is a **proof-of-concept** built for a hackathon. It is not
> enterprise-grade coverage, not a formal compliance certification, and it
> does not run a real quantum computer. RSA and ECC are **not** claimed to be
> broken today — they are classified as *quantum vulnerable* against
> sufficiently capable future quantum attacks.

---

## Architecture

```
React (Vite) frontend            Python FastAPI backend
+---------------------+          +------------------------------+
| TopBar / TargetPanel|  REST    | main.py       (orchestration) |
| GenomeVisualization | <------> | scanner.py    (discovery)     |
| AssetInspector      |  JSON    | crypto_knowledge.py (KB)      |
| InventoryTable      |  POST    | risk_engine.py (priority)     |
| PostureView         |  /scan   | hndl_engine.py (HNDL)         |
| RoadmapView         |          | blast_radius.py (impact)     |
+---------------------+          +------------------------------+
         |                                 |
         +----------- sample-target -------+
```

- **Frontend:** React 19 + Vite (existing tooling preserved, no new runtime deps).
- **Backend:** Python 3 + FastAPI + Uvicorn. This is the real analysis engine.
  Node.js is only frontend build tooling and never replaces the backend.
- **Communication:** REST over JSON. The frontend calls `POST /scan`.

### Data flow

1. User clicks **SEQUENCE SYSTEM** in the UI.
2. `POST /scan` with `{"path": "../sample-target"}` is sent to FastAPI.
3. `scanner.scan_directory()` recursively walks the target, skipping
   generated folders (`node_modules`, `venv`, `.git`, `build`, `dist`,
   `__pycache__`) and binary files.
4. Each detected algorithm is enriched from `crypto_knowledge.py`
   (category, role, quantum status, explanation, migration guidance).
5. `risk_engine`, `hndl_engine` and `blast_radius` score each finding.
6. The UI reconstructs the "cryptographic genome" and analysis panels.

---

## Running the project

### Backend (FastAPI)

```bash
cd backend
python -m venv venv                       # first time only
./venv/Scripts/python.exe -m pip install -r requirements.txt
./venv/Scripts/python.exe -m uvicorn main:app --host 127.0.0.1 --port 8000
```

- API: `http://127.0.0.1:8000` (docs at `/docs`)
- Scan a directory: `POST /scan` with `{"path": "../sample-target"}`

### Frontend (React + Vite)

```bash
cd frontend
npm install                               # first time only
npm run dev                               # http://localhost:5173
```

CORS is pre-configured for `localhost:5173` / `127.0.0.1:5173` and ports
`3000`. If the backend runs elsewhere, set `VITE_API_URL`.

### Tests

```bash
cd backend
./venv/Scripts/python.exe -m pytest tests -q
```

The suite covers algorithm detection, quantum classification, recursive
scanning, configuration files, invalid/empty targets, the scan API, and all
three scoring engines.

---

## Supported algorithms

| Algorithm  | Role                      | Quantum status                    | Direction          |
|------------|---------------------------|-----------------------------------|--------------------|
| RSA / RSA-2048 / 3072 / 4096 | public-key cryptography | quantum vulnerable (Shor) | ML-KEM / ML-DSA |
| ECDSA, DSA | digital signature         | quantum vulnerable (Shor)         | ML-DSA             |
| ECDH, DH   | key exchange              | quantum vulnerable (Shor)         | ML-KEM             |
| AES-128 / AES-256 | symmetric encryption | comparatively quantum resilient   | retain + PQ key exchange |
| SHA-1       | cryptographic hash       | deprecated (classical collisions) | SHA-256+           |
| SHA-256 / SHA-384 / SHA-512 | cryptographic hash | comparatively quantum resilient | retain |
| ML-KEM     | post-quantum key establishment | post-quantum ready          | —                  |
| ML-DSA, SLH-DSA | post-quantum digital signature | post-quantum ready          | —                  |

Supported file types: `.py .js .jsx .ts .tsx .java .cpp .c .h .hpp .json
.yaml .yml .xml .pem .conf .cfg .txt`. Detection is regex-based per line and
does **not** depend on filenames being hardcoded.

**Note:** ML-KEM and ML-DSA are deliberately **not interchangeable** — key
establishment migrates toward ML-KEM, signatures toward ML-DSA.

---

## What the measurements mean

### HNDL (Harvest-Now, Decrypt-Later)

An attacker can capture encrypted traffic today and decrypt it later once a
capable quantum computer exists. HNDL concern rises when the cryptography is
quantum vulnerable, the data is sensitive, and confidentiality must last for
many years. The HNDL score combines future decryptability, harvest value and
retention risk into an `exposure` level (LOW → CRITICAL).

### POC risk score

The 0–100 score is a **QuantumDNA Internal Prioritization Model**, not an
official NIST formula. It combines:

- quantum vulnerability (30)
- data sensitivity (20)
- retention / HNDL (20)
- internet exposure (15)
- dependency / blast-radius impact (15)

Every score ships with a plain-language `explanation` and a per-factor
breakdown so prioritization is explainable.

### Blast radius

A BFS over a demonstration dependency graph computes direct + downstream
affected assets, maximum dependency depth and a 0–100 score. The graph is
currently a **fixed DEMO model** (labeled `mode: "DEMO"` in the API) — it is
*not* inferred from arbitrary source code yet.

---

## Limitations (honest)

- Regex line scanning detects algorithm names; it does not prove real
  cryptographic usage or key size enforcement.
- Dependency graph and per-category sensitivity are demonstration inputs,
  not discovered from code.
- No real quantum computer is involved; "vulnerable" means vulnerable to
  *sufficiently capable future* quantum attacks.
- Migration views are UI simulations showing direction only — QuantumDNA
  does not migrate cryptography automatically.
- No persistence, authentication, or multi-tenant features.
