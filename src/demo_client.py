# src/demo_client.py

from optilogic.pioneer import Api
from requests.exceptions import HTTPError


def get_client_appkey(app_key: str) -> Api:
    """Returns an Optilogic API client using appkey authentication."""
    return Api(appkey=app_key, auth_legacy=False)

def get_client_legacy(username: str, password: str) -> Api:
    """Returns an Optilogic API client using legacy username/password authentication."""
    return Api(un=username, pw=password, auth_legacy=True)

def create_database(client, name, desc=None):
    if not isinstance(name, str):
        raise TypeError("Database name must be a string")

    params = {"name": name}
    if desc is not None:
        params["desc"] = desc

    try:
        response = client.database_create(**params)
        return response
    except HTTPError as e:
        return {
            "crash": True,
            "exception": e,
            "resp": getattr(e.response, 'status_code', None),
            "result": "error",
            "url": getattr(e.response, 'url', None),
        }
    except Exception as e:
        return {
            "crash": True,
            "exception": e,
            "result": "error",
        }
