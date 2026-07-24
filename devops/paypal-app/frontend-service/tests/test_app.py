import sys
import os

sys.path.append(
    os.path.abspath(
        os.path.join(
            os.path.dirname(__file__),
            ".."
        )
    )
)

from app import app


def test_home_redirect():

    client = app.test_client()

    response = client.get("/")

    assert response.status_code == 302


def test_login_page():

    client = app.test_client()

    response = client.get("/login")

    assert response.status_code == 200

    assert b"Login" in response.data


def test_health():

    client = app.test_client()

    response = client.get("/health")

    assert response.status_code == 200


def test_ready():

    client = app.test_client()

    response = client.get("/ready")

    assert response.status_code == 200