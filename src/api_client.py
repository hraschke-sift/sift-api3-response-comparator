import requests
from auth import get_auth_token

def make_api_call(url, method, headers=None, body=None, base_url='', auth_endpoint='https://api3.siftscience.com'):
    # Include the bearer token in headers
    token = get_auth_token(auth_endpoint)
    if not headers:
        headers = {}
    headers['Authorization'] = f'Bearer {token}'

    full_url = f"{base_url}{url}"

    try:
        if method == 'GET':
            response = requests.get(full_url, headers=headers)
        elif method == 'POST':
            response = requests.post(full_url, json=body, headers=headers)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")
        return None
