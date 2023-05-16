'''A FastAPI test file for testing the relay `/handshake` URL.

This file is for testing the URL `/v1/api/relay/handshake` with valid, invalid
and with wrong password with the right name. Note that this is the test for the
requirement §3.3
'''

# Our FastAPI application to test on.
from main import app

# We are using the `TestClient` from FastAPI.
from fastapi.testclient import TestClient

client = TestClient(app)
HANDSHAKE_URL = '/v1/api/relay/handshake'


def test_handshake_with_valid_relay():
    # Validate new relay.
    payload = {
        "name": "relay_0001",
        "password": "123"
    }

    # Post the handshake.
    response = client.post(HANDSHAKE_URL, json=payload)

    # Do we get a 200 OK?
    assert response.status_code == 200

    # Convert to json.
    data = response.json()

    # Test if we have a `'access_toke'`.
    assert 'access_token' in data

    # Is the token of the right type?
    assert data["access_token"].startswith("Bearer")


def test_handshake_with_invalid_relay():
    # Invalid relay data
    payload = {
        "name": "invalid_relay",
        "password": "wrong_password"
    }
    response = client.post(HANDSHAKE_URL, json=payload)

    # We should be unauthorized (401).
    assert response.status_code == 401


def test_handshake_with_existing_relay():
    # Existing relay data
    payload = {
        "name": "relay_0001",
        "password": "123"
    }
    response = client.post(HANDSHAKE_URL, json=payload)
    print(response.json())


def test_handshake_with_wrong_password():
    # This for the wrong password with the right name.
    payload = {
        "name": "relay_0001",
        "password": "this_is_not_the_right_password"
    }

    # Post to the handshake.
    response = client.post(HANDSHAKE_URL, json=payload)

    # We should be unauthorized (401).
    assert response.status_code == 401


if __name__ == '__main__':
    print(f'Starting tests on {HANDSHAKE_URL}...')
    test_handshake_with_valid_relay()
    test_handshake_with_invalid_relay()
    test_handshake_with_wrong_password()
    print('Test completed')
