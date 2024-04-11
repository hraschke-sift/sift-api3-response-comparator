import json
import datetime
from output import c_print
from utils import get_url_from_env
import os


def make_calls_list(calls):
    return [
        {
            "eid": f"{index}_{call['url'.split('?')[0]]}",
            "url": call["url"],
            "method": call["method"],
            "body": call.get("body"),
        }
        for index, call in enumerate(calls)
    ]


def generate_config_json(test_run_dir="runs", env="dev"):
    """
    Generates a config.json file based on user input.

    Parameters:
    - output: Output file path for config.json
    - env: Environment specifier, used to determine the base URL
    """

    url = get_url_from_env(env)
    current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    data_input_method = input(
        "Do you want load an existing JSON config file? (y/N): "
    ).lower()

    if data_input_method == "y":
        valid_json = False
        while not valid_json:
            # Create the config.json file if it doesn't already exist
            config_file = f"{test_run_dir}/config.json"
            if not os.path.exists(config_file):
                open(config_file, "w").close()

            # Open the file in editor
            input("Press enter to open the editor...")
            os.system(f"vim {config_file}")

            try:
                config_file = f"{test_run_dir}/config.json"
                with open(config_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                if isinstance(data, dict):
                    if isinstance(data.get("cids"), list) and isinstance(
                        data.get("calls"), list
                    ):
                        valid_json = True
                    else:
                        c_print.warn("Ensure config.json contains 'cids' and 'calls'.")
            except:
                c_print.warn("Invalid JSON file. Please try again.")

        data = {
            "base_url": url,
            "run_start": current_time,
            "cids": data.get("cids"),
            "calls": make_calls_list(data.get("calls")),
        }

    else:
        cids = (
            input("Enter customer IDs separated by comma: ").replace(" ", "").split(",")
        )
        calls = []
        more_calls = True

        while more_calls:
            call = {}
            call_endpoint = input(f"Enter call endpoint: {url}/v3/accounts/<cid>/")
            call["url"] = call_endpoint
            call["method"] = input("Enter call method (GET/POST): ").upper()
            if call["method"] == "POST":
                call["body"] = input("Enter call body (JSON format): ")
            calls.append(call)
            more_calls = input("Add another call? (y/N): ").lower() == "y"

        data = {
            "run_start": current_time,
            "base_url": url,
            "cids": cids,
            "calls": make_calls_list(calls),
        }

    config_file = f"{test_run_dir}/config.json"
    with open(config_file, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

    c_print.ok(f"config.json has been saved to {config_file}")
    print("")
