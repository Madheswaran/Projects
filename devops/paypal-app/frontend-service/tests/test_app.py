import os
import sys
from unittest.mock import patch, Mock

# ---------------------------------------------------------
# Test Configuration
# ---------------------------------------------------------

os.environ["TESTING"] = "true"

sys.path.append(
    os.path.abspath(
        os.path.join(
            os.path.dirname(__file__),
            ".."
        )
    )
)

from app import app


# ---------------------------------------------------------
# Home
# ---------------------------------------------------------

def test_home_redirect():

    client = app.test_client()

    response = client.get("/")

    assert response.status_code == 302


# ---------------------------------------------------------
# Login Page
# ---------------------------------------------------------

def test_login_page():

    client = app.test_client()

    response = client.get("/login")

    assert response.status_code == 200
    assert b"Login" in response.data


# ---------------------------------------------------------
# Login Success
# ---------------------------------------------------------

@patch("app.requests.post")
def test_login_success(mock_post):

    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "id": 1,
        "name": "Ganesha",
        "wallet": 1000.0
    }

    mock_post.return_value = mock_response

    client = app.test_client()

    response = client.post(
        "/login",
        data={
            "email": "ganesha@test.com",
            "password": "password"
        }
    )

    assert response.status_code == 200
    assert b"Ganesha" in response.data


# ---------------------------------------------------------
# Login Failure
# ---------------------------------------------------------

@patch("app.requests.post")
def test_login_failure(mock_post):

    mock_response = Mock()
    mock_response.status_code = 401

    mock_post.return_value = mock_response

    client = app.test_client()

    response = client.post(
        "/login",
        data={
            "email": "wrong@test.com",
            "password": "wrong"
        }
    )

    assert response.status_code == 200
    assert b"Invalid Email or Password" in response.data


# ---------------------------------------------------------
# Health
# ---------------------------------------------------------

def test_health():

    client = app.test_client()

    response = client.get("/health")

    assert response.status_code == 200


# ---------------------------------------------------------
# Readiness
# ---------------------------------------------------------

def test_ready():

    client = app.test_client()

    response = client.get("/ready")

    assert response.status_code == 200