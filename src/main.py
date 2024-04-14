import json
from api_client import make_api_call
from user_input_client import generate_config_json
from utils import (
    create_run_directory,
    load_json_file,
    compare_responses,
    report_run_duration,
)
from output import c_print
from db import create_database, insert_or_update_response
from synthesize_results import process_deepdiff_output


def execute_api_calls(
    cids,
    calls,
    base_url,
    run_order,
    env="prod",
    db_path="db/responses.db",
):

    total_calls = len(cids) * len(calls)

    for cid in cids:
        cid_index = cids.index(cid)
        for call in calls:
            # Construct the full API endpoint URL
            url = f"/v3/accounts/{cid}/{call['url'].lstrip('/')}"  # Ensure no double slashes
            call_index = calls.index(call)
            c_print.time(
                f"Making request {(cid_index * len(calls)) + (call_index + 1)} of {total_calls} API: {url}"
            )

            response_data = make_api_call(
                url,
                call["method"],
                body=call.get("body"),
                base_url=base_url,
                env=env,
            )

            eid = call["eid"]

            # Save response data
            if response_data:
                insert_or_update_response(
                    db_path, cid, eid, response_data, run_order == "before"
                )
            else:
                insert_or_update_response(
                    db_path,
                    cid,
                    eid,
                    {"error": "API call failed"},
                    run_order == "before",
                )

    c_print.ok(f"API calls for {run_order} completed.")
    print("")


def run_test_tool(env, config_path, output_dir, summary_type="eid", no_pause=False):
    # Get environment and create test run directory
    if not env:
        env = input("Enter environment (dev/expr/stg1/prod): ").lower()
        valid_env_options = ["dev", "expr", "stg1", "prod"]
        while env not in valid_env_options:
            env = input(
                "Invalid environment. Please enter a valid environment (dev/expr/stg1/prod)"
            ).lower()

    test_run_dir = create_run_directory(env, output_dir)
    c_print.blue(f"Test run will output at {test_run_dir}")

    # Create DB
    db_path = f"{test_run_dir}/responses.db"
    create_database(db_path)

    # Generate config.json via CLI prompts
    generate_config_json(test_run_dir, env, config_path)
    input("Config file validated. Press Enter to execute API calls...")
    print("")

    config_file = load_json_file(f"{test_run_dir}/config.json")
    base_url = config_file["base_url"]
    cids = config_file["cids"]
    calls = config_file["calls"]

    # Execute API calls for "before"
    c_print.blue("Executing 'before' API calls...")
    execute_api_calls(cids, calls, base_url, "before", env, db_path)

    # Pause for database migration
    if not no_pause:
        input(
            "Please complete the change to be validated now. Press Enter to continue once done..."
        )
        print("")

    # Execute API calls for "after"
    c_print.blue("Executing 'after' API calls...")
    execute_api_calls(cids, calls, base_url, "after", env, db_path)

    # Compare the results
    c_print.blue("Comparing 'before' and 'after' API calls...")
    compare_responses(test_run_dir, db_path, cids, calls)

    # Process the output to summarized results
    deepdiff_results = load_json_file(f"{test_run_dir}/results.json")
    results_summary = process_deepdiff_output(deepdiff_results, summary_type)
    report_file = f"{test_run_dir}/report.json"
    with open(report_file, "w") as f:
        json.dump(results_summary, f, indent=4)
    c_print.blue(f"Results summary written to {report_file}")

    # Report duration and record end time to config.json
    report_run_duration(test_run_dir)


if __name__ == "__main__":
    print("This script should be run via the CLI.")
