import pytest
from fastapi.testclient import TestClient

from app.main import _reset_for_tests, app

client = TestClient(app)
DEMO_TOKEN = "training-fixture-value-not-a-live-secret"


@pytest.fixture(autouse=True)
def reset_ledger(monkeypatch):
    monkeypatch.setenv("DEMO_API_TOKEN", DEMO_TOKEN)
    _reset_for_tests()


def headers(key="demo-request-0001", token=DEMO_TOKEN):
    return {"Authorization": f"Bearer {token}", "Idempotency-Key": key}


def test_health():
    assert client.get("/health").json() == {"status": "ok"}


def test_transfer_with_valid_token():
    response = client.post("/transfer", json={"amount_minor": 250}, headers=headers())
    assert response.status_code == 200
    assert response.json()["balance_minor"] == 9750


def test_authentication_required():
    response = client.post("/transfer", json={"amount_minor": 100}, headers={"Idempotency-Key": "demo-request-0001"})
    assert response.status_code == 401


def test_wrong_token_denied():
    response = client.post("/transfer", json={"amount_minor": 100}, headers=headers(token="wrong"))
    assert response.status_code == 401


def test_idempotent_retry_does_not_double_debit():
    first = client.post("/transfer", json={"amount_minor": 300}, headers=headers())
    second = client.post("/transfer", json={"amount_minor": 300}, headers=headers())
    assert first.status_code == 200
    assert second.status_code == 200
    assert first.json() == second.json()
    assert client.get("/balances", headers=headers()).json() == {"alice": 9700, "bob": 300}


def test_reusing_key_for_different_amount_rejected():
    assert client.post("/transfer", json={"amount_minor": 200}, headers=headers()).status_code == 200
    response = client.post("/transfer", json={"amount_minor": 500}, headers=headers())
    assert response.status_code == 409


def test_negative_amount_rejected():
    response = client.post("/transfer", json={"amount_minor": -100}, headers=headers())
    assert response.status_code == 422


def test_insufficient_balance_rejected():
    assert client.post("/transfer", json={"amount_minor": 10000}, headers=headers()).status_code == 200
    response = client.post("/transfer", json={"amount_minor": 1}, headers=headers("demo-request-0002"))
    assert response.status_code == 409
