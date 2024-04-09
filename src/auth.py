import os
import requests
import yaml
from getpass import getpass

# TODO(henry) - this currently writes and reads from the same file for
# every environment. Figure out how it works in the ruby client and mimic
# that behavior.

CONF_FILE = os.path.expanduser('~/.api3_client.yaml')

def read_conf():
    if os.path.exists(CONF_FILE):
        with open(CONF_FILE, 'r') as file:
            return yaml.safe_load(file)
    return {}

def write_conf(data):
    with open(CONF_FILE, 'w') as file:
        yaml.dump(data, file, default_flow_style=False)

def refresh_auth(refresh_token, endpoint):
    response = requests.post(f"{endpoint}/oauth2/token", data={
        'grant_type': 'refresh_token',
        'refresh_token': refresh_token,
        'response_type': 'token',
        'client_id': 'api3_client',
    })
    if response.status_code < 300:
        print("Refreshed auth token")
        data = response.json()
        auth_token = data['access_token']
        refresh_token = data.get('refresh_token')
        write_conf({'auth_token': auth_token, 'refresh_token': refresh_token})
        return auth_token
    else:
        print("Refresh token has expired, please authenticate again.")
        return password_auth(endpoint)

def password_auth(endpoint):
    username = input("Username: ")
    password = getpass("Password: ")
    totp = getpass("Token: ")

    response = requests.post(f"{endpoint}/oauth2/token", data={
        'grant_type': 'password',
        'username': username,
        'password': password,
        'totp': totp,
        'response_type': 'token',
        'client_id': 'api3_client',
    })
    if response.status_code < 300:
        print("Authentication successful")
        data = response.json()
        write_conf({'auth_token': data['access_token'], 'refresh_token': data.get('refresh_token')})
        return data['access_token']
    else:
        print("Failed to authenticate")
        return password_auth(endpoint)

def get_auth_token(endpoint):
    conf = read_conf()
    auth_token = conf.get('auth_token')
    refresh_token = conf.get('refresh_token')

    if auth_token and refresh_token:
        return refresh_auth(refresh_token, endpoint)
    else:
        return password_auth(endpoint)
