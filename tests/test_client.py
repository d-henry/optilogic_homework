# tests/test_client.py

import pytest
from src.demo_client import get_client_appkey
from unittest.mock import patch
from dotenv import load_dotenv
import os


@patch("optilogic.pioneer.api.api.Api.account_info")
def test_account_info_called(mock_account_info):
    api_key = os.getenv("OPTILOGIC_APP_KEY")
    assert api_key is not None, "API key not found in envirionment variables!"

    mock_account_info.return_value = {"user": "testuser"}

    client = get_client_appkey(api_key)
    info = client.account_info()

    assert info["user"] == "testuser"
    mock_account_info.assert_called_once()
