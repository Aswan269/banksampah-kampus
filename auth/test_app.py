import os
os.environ["SKIP_DB_INIT"] = "1"
from app import app


def test_health():
    assert app.test_client().get("/health").status_code == 200


def test_me_tanpa_token_ditolak():
    assert app.test_client().get("/me").status_code == 401
