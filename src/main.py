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
                f"Making request {(cid_index * len(cids)) + (call_index + 1)} of {total_calls} API: {url}"
            )

            response_data = make_api_call(
                url,
                call["method"],
                body=call.get("body"),
                base_url=base_url,
                env=env,
            )

            call_string = f"{str(call_index)}_{call['url'].split('?')[0]}"

            # Save response data
            if response_data:
                insert_or_update_response(
                    db_path, cid, call_string, response_data, run_order == "before"
                )
            else:
                insert_or_update_response(
                    db_path,
                    cid,
                    call_string,
                    {"error": "API call failed"},
                    run_order == "before",
                )

    c_print.ok(f"API calls for {run_order} completed.")
    print("")


def main():
    # Get environment and create test run directory
    env = input("Enter environment (dev/expr/stg1/prod): ").lower()
    valid_env_options = ["dev", "expr", "stg1", "prod"]
    while env not in valid_env_options:
        env = input(
            "Invalid environment. Please enter a valid environment (dev/expr/stg1/prod)"
        ).lower()

    test_run_dir = create_run_directory("runs/", env)
    c_print.blue(f"Test run directory created at {test_run_dir}")

    # Create DB
    db_path = "db/responses.db"
    create_database(db_path)

    # Generate config.json via CLI prompts
    generate_config_json(test_run_dir, env)
    input("Files generated. Press Enter to execute API calls...")
    print("")

    config_file = load_json_file(f"{test_run_dir}/config.json")
    base_url = config_file["base_url"]
    cids = config_file["cids"]
    calls = config_file["calls"]

    # Execute API calls for "before"
    c_print.blue("Executing 'before' API calls...")
    execute_api_calls(cids, calls, base_url, "before", env, db_path)

    # Pause for database migration
    input(
        "Please complete the change to be validated now. Press Enter to continue once done..."
    )
    print("")

    # Execute API calls for "after"
    c_print.blue("Executing 'after' API calls...")
    execute_api_calls(cids, calls, base_url, "after", test_run_dir, env, db_path)

    # Compare the results
    c_print.blue("Comparing 'before' and 'after' API calls...")
    call_strings_array = [
        f"{str(calls.index(call))}_{call['url'].split('?')[0]}" for call in calls
    ]
    compare_responses(test_run_dir, db_path, cids, call_strings_array)

    # Report duration and record end time to config.json
    report_run_duration(test_run_dir)


if __name__ == "__main__":
    main()
