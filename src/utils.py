import os
import json
import math
from datetime import datetime
from output import c_print
from db import get_responses, set_difference
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


def compare_responses(test_run_dir, db_path, cids, endpoints):
    for cid in cids:
        for endpoint in endpoints:
            c_print.time(
                "Comparing responses for customer ID:", cid, "Endpoint:", endpoint
            )
            response_before, response_after = get_responses(db_path, cid, endpoint)

            diff = "Missing response data"

            if response_before and response_after:
                diff = DeepDiff(
                    response_before,
                    response_after,
                    ignore_order=True,
                    exclude_paths={"root['request_id']"},
                )

                if not diff:
                    diff = "nil"
                else:
                    diff = json.dumps(diff, cls=CustomJSONEncoder)
                    c_print.warn("Differences found.")

            set_difference(db_path, cid, endpoint, diff)
            record_result(test_run_dir, cid, endpoint, diff)
            c_print.blue(f"See the complete results in {test_run_dir}/results.json")


def report_run_duration(test_run_dir):
    with open(f"{test_run_dir}/config.json", "r") as file:
        data = json.load(file)
        data["run_end"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    run_duration = datetime.strptime(
        data["run_end"], "%Y-%m-%d %H:%M:%S"
    ) - datetime.strptime(data["run_start"], "%Y-%m-%d %H:%M:%S")

    c_print.ok(f"Test run completed in {run_duration}")

    with open(f"{test_run_dir}/config.json", "w") as file:
        json.dump(data, file, indent=4)


def record_result(test_run_dir, cid, endpoint, result):
    # check if the results.json exists
    results_file = os.path.join(test_run_dir, "results.json")
    if os.path.exists(results_file):
        with open(results_file, "r") as file:
            results = json.load(file)
    else:
        results = {}

    # update the results with the new result
    if result == "nil":
        results[f"{cid}_{endpoint}"] = json.loads(result)

    # write the updated results back to the file
    with open(results_file, "w") as file:
        json.dump(results, file, indent=4)
