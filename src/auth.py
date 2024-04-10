import os
import requests
import yaml
from getpass import getpass
from utils import get_url_from_env
from dotenv import load_dotenv

# TODO(henry) - this currently writes and reads from the same file for
# every environment. Figure out how it works in the ruby client and mimic
# that behavior.

CONF_FILE = os.path.expanduser("~/.api3_tokens.yaml")


def read_conf():
    if os.path.exists(CONF_FILE):
        with open(CONF_FILE, "r") as file:
            return yaml.safe_load(file)
    return {}


def write_conf(env, data):
    if os.path.exists(CONF_FILE):
        with open(CONF_FILE, "r") as file:
            conf_data = yaml.safe_load(file)
        conf_data[env] = data
    else:
        conf_data = {env: data}
    with open(CONF_FILE, "w") as file:
        yaml.dump(conf_data, file, default_flow_style=False)


def refresh_auth(refresh_token, env):
    endpoint = get_url_from_env(env)
    response = requests.post(
        f"{endpoint}/oauth2/token",
        data={
            "grant_type": "refresh_token",
            "refresh_token": refresh_token,
            "response_type": "token",
            "client_id": "api3_comparator",
        },
    )
    if response.status_code < 300:
        print("Refreshed auth token")
        data = response.json()
        auth_token = data["access_token"]
        refresh_token = data.get("refresh_token")
        write_conf(env, {"auth_token": auth_token, "refresh_token": refresh_token})
        return auth_token
    else:
        print("Refresh token has expired, please authenticate again.")
        return password_auth(env)


def password_auth(env):
    # Check if username and password are in environment variables
    load_dotenv()
    username = os.getenv("USERNAME")
    password = os.getenv("PASSWORD")
    if not username or not password:
        # If not, prompt user for username and password
        username = input("Username: ")
        password = getpass("Password: ")
    else:
        print(f"Using username and password {username} from environment variable")
    # Ask for TOTP token
    totp = getpass("Token: ")

    endpoint = get_url_from_env(env)
    response = requests.post(
        f"{endpoint}/oauth2/token",
        data={
            "grant_type": "password",
            "username": username,
            "password": password,
            "totp": totp,
            "response_type": "token",
            "client_id": "api3_comparator",
        },
    )
    if response.status_code < 300:
        print("Authentication successful")
        data = response.json()
        write_conf(
            env,
            {
                "auth_token": data["access_token"],
                "refresh_token": data.get("refresh_token"),
            },
        )
        return data["access_token"]
    else:
        print("Failed to authenticate")
        return password_auth(env)


def get_auth_token(env, refresh=False):
    conf = read_conf()
    auth_token = conf.get(env, {}).get("auth_token")
    refresh_token = conf.get(env, {}).get("refresh_token")

    if auth_token and refresh_token:
        if refresh:
            return refresh_auth(refresh_token, env)
        return auth_token
    else:
        return password_auth(env)
