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

def test_home():

    client = app.test_client()

    response = client.get('/')

    assert response.status_code == 200
