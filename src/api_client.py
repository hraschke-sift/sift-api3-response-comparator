import requests
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
        return make_api_call(retry + 1) if retry < max_retries else None
