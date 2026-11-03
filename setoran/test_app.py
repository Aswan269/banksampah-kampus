import os
os.environ["SKIP_DB_INIT"] = "1"
from app import app, hitung_poin


def test_hitung_poin():
    assert hitung_poin(2.5, 100) == 250
    assert hitung_poin(0.5, 60) == 30


def test_health():
    assert app.test_client().get("/health").status_code == 200


def test_ajukan_tanpa_token_ditolak():
    assert app.test_client().post("/ajukan", json={}).status_code == 401
