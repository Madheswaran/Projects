import sys
import os

sys.path.append(
    os.path.abspath(
        os.path.join(
            os.path.dirname(__file__),
            '..'
        )
    )
)

os.environ["API_KEY"] = "test-api-key"
os.environ["DB_PASSWORD"] = "test-password"

from app import app 

def test_users():

    client = app.test_client()

    response = client.get('/users')

    assert response.status_code == 200

    data.response.get_json() 

    assert length(data) == 2 

    assert data[0]['name'] == 'Ganesh'

def test_health():

    client = app.test_client()

    response = client.get('/health')

    assert response.status_code == 200

    assert response.get_json()["status"] == "UP"


def test_ready():

    client = app.test_client()

    response = client.get('/ready')

    assert response.status_code == 200

    assert response.get_json()["status"] == "READY"

