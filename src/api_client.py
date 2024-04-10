import requests
import time
from auth import get_auth_token
from output import c_print

max_retries = 2


def make_api_call(
    url,
    method,
    headers=None,
    body=None,
    base_url="",
    env="prod",
    retry=0,
):
    # Include the bearer token in headers
    token = get_auth_token(env)
    if not headers:
        headers = {}
    headers["Authorization"] = f"Bearer {token}"
    headers["Content-Type"] = "application/json"

    full_url = f"{base_url}{url}"

    try:
        if method == "GET":
            response = requests.get(full_url, headers=headers)
        elif method == "POST":
            response = requests.post(full_url, json=body, headers=headers)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        c_print.fail(f"Request failed: {e}")
        # if the response is a 404, no retry (resource doesn't exist)
        if response.status_code == 404:
            return None

        # if the response is a 401, refresh the auth token and retry
        if response.status_code == 401:
            c_print.warn("Refreshing auth token")
            get_auth_token(env, refresh=True)
            return (
                make_api_call(url, method, headers, body, base_url, env, retry + 1)
                if retry < max_retries
                else None
            )

        # Otherwise, retry the request if it failed
        time.sleep(2)
        return (
            make_api_call(url, method, headers, body, base_url, env, retry + 1)
            if retry < max_retries
            else None
        )
