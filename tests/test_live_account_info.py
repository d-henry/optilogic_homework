# tests/test_live_account_info.py

import pytest
from src.demo_client import get_client_appkey
from dotenv import load_dotenv
import os

def test_live_account_info():
    api_key = os.getenv("OPTILOGIC_APP_KEY")
    assert api_key is not None, "API key not found in envirionment variables!"

    client = get_client_appkey(api_key)
    info = client.account_info()

    assert "user" in info or "username" in info
    print(info)