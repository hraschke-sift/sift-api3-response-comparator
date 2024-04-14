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


def create_run_directory(env, output_dir):
    if not output_dir:
        timestamp = math.floor(datetime.now().timestamp())
        output_dir = os.path.join("runs/", f"{timestamp}_{env}")
    os.makedirs(output_dir, exist_ok=True)
    return output_dir


def get_url_from_env(env):
    url_options = {
        "dev": "https://localhost:5323",
        "expr": "https://experiment-console.sift.com",
        "stg1": "https://staging-console.siftscience.com",
        "prod": "https://console.sift.com",
    }
    return url_options.get(env, "")


def compare_responses(test_run_dir, db_path, cids, calls):
    for cid in cids:
        for call in calls:
            c_print.time(
                "Comparing responses for customer ID:", cid, "Endpoint:", call["url"]
            )

            eid = call["eid"]
            response_before, response_after = get_responses(db_path, cid, eid)

            diff = "Missing response data"

            response_before = json.loads(response_before)
            response_after = json.loads(response_after)
            if response_before and response_after:
                exclude_paths = call.get("exclude_paths", [])
                diff = DeepDiff(
                    response_before,
                    response_after,
                    ignore_order=True,
                    exclude_paths=exclude_paths,
                )

                if not diff:
                    diff = {}
                else:
                    # diff = json.dumps(diff, cls=CustomJSONEncoder)
                    c_print.warn("Differences found.")

            set_difference(db_path, cid, eid, str(diff))
            record_result(test_run_dir, cid, eid, diff)
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
        results = {
            "all_results": {},
            "results_by_cid": {},
            "results_by_endpoint": {},
            "total_diffs": 0,
        }

    # update the results with the new result
    results["all_results"][f"{cid}_{endpoint}"] = result
    results["results_by_cid"].setdefault(cid, {})[endpoint] = result
    results["results_by_endpoint"].setdefault(endpoint, {})[cid] = result
    if not result == {}:
        results["total_diffs"] += 1

    # write the updated results back to the file
    with open(results_file, "w") as file:
        json.dump(results, file, indent=4)


# TODO(henry) make a class with methods for loads and dumps that employ these functions
# We can programatically decide whether we want PrettyOrderedSet or JSON output
class CustomJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, PrettyOrderedSet):
            return list(obj)  # Convert PrettyOrderedSet to list
        # Let the base class default method raise the TypeError
        return json.JSONEncoder.default(self, obj)


def decode_json_recursively(data):
    if isinstance(data, str):
        try:
            data = json.loads(data)
        except json.JSONDecodeError:
            return data

    if isinstance(data, dict):
        return {key: decode_json_recursively(value) for key, value in data.items()}
    elif isinstance(data, list):
        return [decode_json_recursively(item) for item in data]
    else:
        return data
