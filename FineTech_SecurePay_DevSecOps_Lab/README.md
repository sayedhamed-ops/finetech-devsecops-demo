# Fine Tech — SecurePay DevSecOps Lab

An intentionally small, **non-production** payment-style API to practice the DevSecOps lifecycle.
No real money, no external payment provider, no actual customer data.

## Learning milestones

1. Understand the business: mock transfer from Alice to Bob.
2. Threat model: read `THREAT_MODEL.md`.
3. Run application tests + Semgrep SAST locally.
4. Run the same checks from a Jenkins Pipeline.
5. Add Gitleaks and Trivy scanners.
6. Later: Docker Compose local staging (without Docker Desktop) and a simulated release approval.

## Run locally in Ubuntu WSL (no Docker required)

```bash
cd ~/finetech-devsecops-demo
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt -r requirements-dev.txt
.venv/bin/pytest -q
/home/sayed/finetech-semgrep/bin/semgrep scan --config .semgrep.yml --metrics=off --error app
```

Expected: **8 tests passed** and **0 Semgrep findings**.

## Run the mock API

Open one Ubuntu terminal:

```bash
cd ~/finetech-devsecops-demo
export DEMO_API_TOKEN="$(python3 -c 'import secrets; print(secrets.token_hex(24))')"
.venv/bin/uvicorn app.main:app --host 127.0.0.1 --port 8000
```

Open `http://127.0.0.1:8000/docs` from your Windows browser if WSL forwarding works.

The token lives only in that terminal environment. Avoid logging or copying it to chat.

## Jenkins Lab

The included `Jenkinsfile` is a *training-only* example. It assumes Jenkins
checks out this repository via a trusted Pipeline-from-SCM configuration, and
Semgrep is installed at `/home/sayed/finetech-semgrep/bin/semgrep`.

Do **not** run untrusted PRs with `agent any` on Jenkins controller in a real system.
The `Jenkinsfile.full.example` is a future target requiring Gitleaks and Trivy.

## Later Docker Compose staging

Only after a separate Docker Engine is available on a controlled Linux host:

```bash
export DEMO_API_TOKEN="$(python3 -c 'import secrets; print(secrets.token_hex(24))')"
docker compose -f compose.staging.yml up --build -d
```

Production cloud VPS deployment is intentionally **not implemented** in this lab.
For Fine Tech, the target architecture remains on-prem Docker Compose staging,
cloud Docker Compose production, VPN/restricted SSH deployment, an approved image
digest in a private registry, and separate credentials/approval.
