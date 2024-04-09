import requests
import time
from auth import get_auth_token

max_retries = 3


def make_api_call(
    url,
    method,
    headers=None,
    body=None,
    base_url="",
    auth_endpoint="https://console.sift.com",
    retry=0,
):
    # Include the bearer token in headers
    token = get_auth_token(auth_endpoint, retry > 0)
    if not headers:
        headers = {}
    headers["Authorization"] = f"Bearer {token}"

    full_url = f"{base_url}{url}"

    try:
        if method == "GET":
            response = requests.get(full_url, headers=headers)
        elif method == "POST":
            response = requests.post(full_url, json=body, headers=headers)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")
        # If the response is a 401, no retry (user doesn't have access)
        if response.status_code == 401:
            return None
        # if the response is a 404, no retry (resource doesn't exist)
        if response.status_code == 404:
            return None
        # Otherwise, retry the request if it failed
        time.sleep(2)
        return make_api_call(retry + 1) if retry < max_retries else None
