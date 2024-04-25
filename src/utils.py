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
            if "segments" in call["url"]:
                c_print.warn('skipping segments response comparison')
                continue
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

                # set_difference(db_path, cid, eid, str(diff))
                # try:
                record_result(test_run_dir, cid, eid, diff)
            # except:
            # c_print.fail(f"Error recording result for {cid}_{eid}")
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
    results = {
        "all_results": {},
        "results_by_cid": {},
        "results_by_endpoint": {},
        "total_diffs": 0,
    }
    if os.path.exists(results_file):
        try:
            with open(results_file, "r") as file:
                results = json.load(file)
        except:
            c_print.fail(f"Error reading results.json for {cid}_{endpoint}")

    # Type changes in results show as `<class 'Type'>` in the diff
    # Remove the non-JSON serializable type changes
    if "type_changes" in result:
        try:
            record_type_change(test_run_dir, cid, endpoint, result["type_changes"])
        except:
            c_print.fail(f"Error recording type changes for {cid}_{endpoint}")
        result.pop("type_changes")

    if "dictionary_item_added" in result:
        try:
            record_items_added(test_run_dir, cid, endpoint, result["dictionary_item_added"])
        except:
            c_print.fail(f"Error recording items added for {cid}_{endpoint}")
        result.pop("dictionary_item_added")

    # update the results with the new result
    results["all_results"][f"{cid}_{endpoint}"] = result
    results["results_by_cid"].setdefault(cid, {})[endpoint] = result
    results["results_by_endpoint"].setdefault(endpoint, {})[cid] = result
    if not result == {}:
        results["total_diffs"] += 1

    # write the updated results back to the file
    try:
        with open(results_file, "w") as file:
            json.dump(results, file, indent=4)
    except:
        c_print.fail(f"Error writing results.json for {cid}_{endpoint}")


def record_type_change(test_run_dir, cid, endpoint, type_change):
    for changes_obj in type_change.values():
        changes_obj["old_type"] = str(changes_obj["old_type"]).replace("<class '", "").replace("'>", "")
        changes_obj["new_type"] = str(changes_obj["new_type"]).replace("<class '", "").replace("'>", "")

    # check if the type_changes.json exists
    type_changes_file = os.path.join(test_run_dir, "type_changes.json")
    type_changes = {
        "all_type_changes": {},
        "type_changes_by_cid": {},
        "type_changes_by_endpoint": {},
        "total_diffs": 0,
    }
    if os.path.exists(type_changes_file):
        try:
            with open(type_changes_file, "r") as file:
                type_changes = json.load(file)
        except:
            c_print.fail(f"Error reading type_changes.json for {cid}_{endpoint}")

    # update the type_changes with the new type_change
    type_changes["all_type_changes"][f"{cid}_{endpoint}"] = type_change
    type_changes["type_changes_by_cid"].setdefault(cid, {})[endpoint] = type_change
    type_changes["type_changes_by_endpoint"].setdefault(endpoint, {})[
        cid
    ] = type_change
    if not type_changes == {}:
        type_changes["total_diffs"] += 1


    # write the updated type_changes back to the file
    with open(type_changes_file, "w") as file:
        json.dump(type_changes, file, indent=4)

def record_items_added(test_run_dir, cid, endpoint, items_added):
    items_added_data = {
        "all_items_added": {},
        "items_added_by_cid": {},
        "items_added_by_endpoint": {},
        "total_diffs": 0,
    }

    items_added_file = os.path.join(test_run_dir, "items_added.json")
    if os.path.exists(items_added_file):
        try:
            with open(items_added_file, "r") as file:
                items_added_data = json.load(file)
        except:
            c_print.fail(f"Error reading items_added.json for {cid}_{endpoint}")
    items_added_data["all_items_added"][f"{cid}_{endpoint}"] = str(items_added)
    items_added_data["items_added_by_cid"].setdefault(cid, {})[endpoint] = str(items_added)
    items_added_data["items_added_by_endpoint"].setdefault(endpoint, {})[cid] = str(items_added)

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
