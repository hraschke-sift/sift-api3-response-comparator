import os
import json
import math
from datetime import datetime
from deepdiff import DeepDiff
from deepdiff.model import PrettyOrderedSet


def load_json_file(file_path):
    with open(file_path, "r", encoding="utf-8") as file:
        return json.load(file)


def create_run_directory(base_path, env):
    """Create a directory for a new run."""
    timestamp = math.floor(datetime.now().timestamp())
    dir_path = os.path.join(base_path, f"{timestamp}_{env}")
    os.makedirs(dir_path, exist_ok=True)
    return dir_path


def get_url_from_env(env):
    url_options = {
        "dev": "https://localhost:5323",
        "expr": "https://experiment-console.sift.com",
        "stg1": "https://staging-console.siftscience.com",
        "prod": "https://console.sift.com",
    }
    return url_options.get(env, "")


def update_response_file(
    test_run_dir, run_order, customer_id, call_string, response_data
):
    """
    Updates the before.json or after.json file with the new response data for a given customer_id.

    Parameters:
    - run_order: 'before' or 'after', indicating which file to update.
    - customer_id: The customer ID for which the response is associated.
    - response_data: The JSON response data to append.
    - base_path: Base directory where the runs are stored.
    """
    # Define the path to the appropriate file based on the run order.
    file_path = os.path.join(test_run_dir, f"{run_order}.json")

    # Initialize an empty dictionary to hold our data.
    data = {}

    # If the file already exists, load its contents into the data dictionary.
    if os.path.exists(file_path):
        with open(file_path, "r", encoding="utf-8") as file:
            data = json.load(file)

    # Check if there's an entry for the given customer_id, append if there is, or create a new one if not.
    if customer_id in data:
        data[customer_id][call_string] = response_data
    else:
        data[customer_id] = {call_string: response_data}

    # Write the updated data back to the file.
    with open(file_path, "w", encoding="utf-8") as file:
        json.dump(data, file, indent=4, ensure_ascii=False)


class CustomJSONEncoder(json.JSONEncoder):
    """
    Custom JSON encoder that converts PrettyOrderedSet to list when encoding JSON.
    Everything else passes through to the base class.
    Can be extended to handle other custom types as needed.
    """

    def default(self, obj):
        if isinstance(obj, PrettyOrderedSet):
            return list(obj)  # Convert PrettyOrderedSet to list
        # Let the base class default method raise the TypeError
        return json.JSONEncoder.default(self, obj)


def compare_responses(test_run_dir):
    """
    Compares responses in before.json and after.json within a specific run directory,
    and writes the differences to results.json in the same directory.

    Parameters:
    - run_path: The path to the specific run directory.
    """
    before_path = os.path.join(test_run_dir, "before.json")
    after_path = os.path.join(test_run_dir, "after.json")
    results_path = os.path.join(test_run_dir, "results.json")

    # Load the data from before and after JSON files.
    with open(before_path, "r", encoding="utf-8") as before_file:
        before_data = json.load(before_file)

    with open(after_path, "r", encoding="utf-8") as after_file:
        after_data = json.load(after_file)

    # Compare the two sets of data.
    diff = DeepDiff(before_data, after_data, ignore_order=True).to_dict()

    # Write the comparison results to results.json.
    with open(results_path, "w", encoding="utf-8") as results_file:
        json.dump(
            diff, results_file, indent=4, ensure_ascii=False, cls=CustomJSONEncoder
        )

    if diff:
        print("Differences found. See results.json for details.")
    else:
        print("No differences found between before.json and after.json.")


def report_run_duration(test_run_dir):
    with open(f"{test_run_dir}/config.json", "r") as file:
        data = json.load(file)
        data["run_end"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    run_duration = datetime.strptime(
        data["run_end"], "%Y-%m-%d %H:%M:%S"
    ) - datetime.strptime(data["run_start"], "%Y-%m-%d %H:%M:%S")

    print(f"Test run completed in {run_duration}")

    with open(f"{test_run_dir}/config.json", "w") as file:
        json.dump(data, file, indent=4)
