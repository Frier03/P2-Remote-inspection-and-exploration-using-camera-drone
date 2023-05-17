'''A FastAPI test file for testing the frontend `/login` URL.

This file is for testing the URL `/v1/api/fronted/login` with valid credentials,
invalid credentials and missing credentials. Note that this is the test for the
requirement §2.1 and §3.2. 
'''

# Our FastAPI application to test on.
from main import app

# We are using the `TestClient` from FastAPI.
from fastapi.testclient import TestClient

client = TestClient(app)
LOGIN_URL = '/v1/api/frontend/login'


def test_login_with_valid_credentials():
    # Validate name and password.
    payload = {
        "name": "admin",
        "password": "123"
    }

    # Post to the login.
    response = client.post(LOGIN_URL, json=payload)

    # Do we get a 200 OK?
    assert response.status_code == 200

    # Convert to json.
    data = response.json()

    # Test if we have a `'access_toke'`.
    assert 'access_token' in data

    # Is the token of the right type?
    assert data["access_token"].startswith("Bearer")


def test_login_with_invalid_credentials():
    # Validate the name and password.
    payload = {
        "name": "wrong_user",
        "password": "wrong_password"
    }

    # Post to the login.
    response = client.post(LOGIN_URL, json=payload)

    # Do we get a 401? Wrong user or password.
    assert response.status_code == 401


def test_login_with_missing_credentials():
    # Missing username and password
    payload = {}

    # Post to the login.
    response = client.post(LOGIN_URL, json=payload)

    # Do we get a 422 Unprocessable Content?
    assert response.status_code == 422


if __name__ == '__main__':
    print(f'Starting tests on {LOGIN_URL}...')
    test_login_with_valid_credentials()
    test_login_with_invalid_credentials()
    test_login_with_missing_credentials()
    print('Test completed!')
