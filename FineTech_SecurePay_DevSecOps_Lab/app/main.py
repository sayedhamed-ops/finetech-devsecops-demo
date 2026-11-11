"""TRAINING ONLY: in-memory payment simulation, not a real financial system."""
import os
import secrets
from threading import Lock
from typing import Annotated

from fastapi import Depends, FastAPI, Header, HTTPException
from pydantic import BaseModel, Field

app = FastAPI(title="Fine Tech SecurePay Lab", version="0.1.0")

# Simplified ledger: resets on process restart, not suitable for real money.
_balances = {"alice": 10_000, "bob": 0}
_requests: dict[str, tuple[int, dict]] = {}
_ledger_lock = Lock()


class TransferRequest(BaseModel):
    amount_minor: int = Field(ge=1, le=10_000, description="Demo cents/piasters")


def _require_demo_auth(authorization: Annotated[str | None, Header()] = None):
    """One demo account, with a secret supplied ONLY through environment."""
    expected_token = os.getenv("DEMO_API_TOKEN")
    if not expected_token:
        raise HTTPException(status_code=503, detail="Demo token is not configured")
    prefix = "Bearer "
    if not authorization or not authorization.startswith(prefix):
        raise HTTPException(status_code=401, detail="Missing bearer token")
    presented = authorization[len(prefix):]
    if not secrets.compare_digest(presented, expected_token):
        raise HTTPException(status_code=401, detail="Invalid bearer token")
    return "alice"


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/balances")
def balances(_user: Annotated[str, Depends(_require_demo_auth)]):
    with _ledger_lock:
        return dict(_balances)


@app.post("/transfer")
def transfer(
    body: TransferRequest,
    user: Annotated[str, Depends(_require_demo_auth)],
    idempotency_key: Annotated[str, Header(alias="Idempotency-Key", min_length=8, max_length=120)],
):
    """Send demo funds from alice to bob, idempotently within one process."""
    with _ledger_lock:
        previous = _requests.get(idempotency_key)
        if previous:
            prior_amount, prior_result = previous
            if prior_amount != body.amount_minor:
                raise HTTPException(409, "Idempotency key reused for different amount")
            return prior_result
        if _balances[user] < body.amount_minor:
            raise HTTPException(409, "Insufficient demo balance")
        _balances[user] -= body.amount_minor
        _balances["bob"] += body.amount_minor
        result = {
            "status": "completed",
            "from": user,
            "to": "bob",
            "amount_minor": body.amount_minor,
            "balance_minor": _balances[user],
        }
        _requests[idempotency_key] = (body.amount_minor, result)
        return result


def _reset_for_tests():
    """Internal test helper; not available over HTTP."""
    with _ledger_lock:
        _balances.clear()
        _balances.update({"alice": 10_000, "bob": 0})
        _requests.clear()
