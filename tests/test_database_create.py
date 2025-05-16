# tests/test_database_create.py

import os
import pytest
import uuid
from dotenv import load_dotenv
from src.demo_client import get_client_appkey, create_database
import time

# Load environment variables from .env file
load_dotenv()

# Global list to keep track of databases created during testing
_created_databases = []

# ---- Fixtures ----

@pytest.fixture
def client():
    """
    Returns a connected API client using the app key from environment variables.
    Fails fast if the key is missing.
    """
    api_key = os.getenv("OPTILOGIC_APP_KEY")
    assert api_key is not None, "API key not found in environment variables!"
    return get_client_appkey(api_key)

@pytest.fixture
def test_db_name():
    """
    Returns a unique test database name using a UUID.
    This avoids name collisions and keeps test behavior isolated.
    """
    return f"testdb{uuid.uuid4().hex[:8]}"

@pytest.fixture
def register_database_for_cleanup():
    """
    Adds database names to a global list so they can be deleted after tests finish.
    Call this in your test after successfully creating a database.
    """
    def register(name):
        _created_databases.append(name)
    return register

@pytest.fixture(scope="session", autouse=True)
def cleanup_all_test_databases():
    """
    Automatically runs once after all tests in this module complete.
    Iterates through the global list of test-created database names and deletes them.
    """
    yield  # Wait for all tests to complete before cleanup begins

    api_key = os.getenv("OPTILOGIC_APP_KEY")
    client = get_client_appkey(api_key)
    print("\n🔁 Cleaning up test databases...")

    for db_name in _created_databases:
        try:
            endpoint = f"{client.api_version.strip('/')}/storage/{db_name}"
            client._fetch_json('delete', endpoint)
            print(f"✔️ Deleted {db_name}")
        except Exception as e:
            print(f"⚠️ Failed to delete {db_name}: {e}")

# ---- Tests ----

def test_create_database_with_fixture(client, test_db_name, register_database_for_cleanup):
    """
    Tests creating a new database with a description. Confirms the expected response.
    """
    db_name = test_db_name
    register_database_for_cleanup(db_name)

    response = create_database(client, name=db_name, desc="Pytest-created test DB")
    print(response)
    assert "name" in response or "status" in response

def test_create_database_missing_name(client):
    """
    Ensure that calling the API without a required 'name' argument raises a TypeError.
    """
    with pytest.raises(TypeError):
        client.database_create()

def test_create_database_duplicate_name(client, register_database_for_cleanup):
    """
    Creating two databases with the same name should fail the second time
    with a 409 Conflict error.
    """
    db_name = f"duplicatedb{uuid.uuid4().hex[:8]}"
    register_database_for_cleanup(db_name)

    # First creation should succeed
    response1 = create_database(client, name=db_name)
    assert "crash" not in response1

    # Second creation should raise a conflict
    response2 = create_database(client, name=db_name)
    assert response2.get("crash") is True
    assert "409" in str(response2.get("exception", ""))
    assert "Conflict" in str(response2.get("exception", ""))

def test_create_database_invalid_type(client):
    """
    Passing an invalid type (int instead of str) for the database name should raise a TypeError.
    """
    with pytest.raises(TypeError):
        create_database(client, name=12345)

def test_create_database_without_description(client, register_database_for_cleanup):
    """
    Tests database creation without passing a description field (it's optional).
    """
    db_name = f"nodesc{uuid.uuid4().hex[:8]}"
    register_database_for_cleanup(db_name)

    response = create_database(client, name=db_name)
    assert "name" in response or "status" in response

def test_create_database_very_long_name(client):
    """
    Attempting to create a database with a very long name should fail,
    assuming the API has a max length limit.
    """
    long_name = "a" * 300  # Adjust if API documents an exact max length
    response = create_database(client, name=long_name)
    assert response.get("crash") is True

def test_create_database_with_invalid_api_key():
    """
    Passing an invalid API key should result in an error or crash response from the API.
    """
    invalid_key = "op_" + "x" * 48  # Fake API key format
    client = get_client_appkey(invalid_key)
    db_name = f"invalidkey{uuid.uuid4().hex[:8]}"
    response = create_database(client, name=db_name)

    print("Response with invalid API key:", response)
    assert response.get("crash") is True or "error" in str(response.get("result", "")).lower()

def test_delete_database_explicit(client, register_database_for_cleanup):
    """
    Manually creates and deletes a database, then re-creates it to confirm deletion worked.
    """
    db_name = f"todelete{uuid.uuid4().hex[:8]}"
    register_database_for_cleanup(db_name)

    # Create the DB
    response = create_database(client, name=db_name)
    assert "name" in response or "status" in response

    # Delete it
    try:
        endpoint = f"{client.api_version.strip('/')}/storage/{db_name}"
        client._fetch_json('delete', endpoint)
        time.sleep(1)  # Optional: small wait to avoid race condition
    except Exception as e:
        pytest.fail(f"Delete failed: {e}")

    # Try re-creating it to confirm deletion
    response2 = create_database(client, name=db_name)
    assert "crash" not in response2
