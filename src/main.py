from api_client import make_api_call
from user_input_client import generate_config_json
from utils import (
    create_run_directory,
    load_json_file,
    compare_responses,
    report_run_duration,
)

from db import create_database, insert_or_update_response


def execute_api_calls(
    cids, calls, base_url, run_order, test_run_dir="runs/", env="prod", db_path="responses.db"
):

    total_calls = len(cids) * len(calls)

    for cid in cids:
        cid_index = cids.index(cid)
        for call in calls:
            # Construct the full API endpoint URL
            url = f"/v3/accounts/{cid}/{call['url'].lstrip('/')}"  # Ensure no double slashes
            call_index = calls.index(call)

            print(
                f"Making request {(cid_index + 1) * (call_index + 1)} of {total_calls} API: {url}"
            )
            print("")

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

    print(f"API calls for {run_order} completed and stored in {test_run_dir}.")


def main():
    # Get environment and create test run directory
    env = input("Enter environment (dev/expr/stg1/prod): ").lower()
    valid_env_options = ["dev", "expr", "stg1", "prod"]
    while env not in valid_env_options:
        env = input(
            "Invalid environment. Please enter a valid environment (dev/expr/stg1/prod)"
        ).lower()

    test_run_dir = create_run_directory("runs/", env)
    print(f"Test run directory created at {test_run_dir}")

    # Create DB
    db_path = "responses.db"
    create_database(db_path)

    # Generate config.json via CLI prompts
    generate_config_json(test_run_dir, env)
    input("Files generated. Press Enter to execute API calls...")

    config_file = load_json_file(f"{test_run_dir}/config.json")
    base_url = config_file["base_url"]
    cids = config_file["cids"]
    calls = config_file["calls"]

    # Execute API calls for "before"
    print("Executing 'before' API calls...")
    execute_api_calls(cids, calls, base_url, "before", test_run_dir, env, db_path)

    # Pause for database migration
    input(
        "Please complete the change to be validated now. Press Enter to continue once done..."
    )

    # Execute API calls for "after"
    print("Executing 'after' API calls...")
    execute_api_calls(cids, calls, base_url, "after", test_run_dir, env, db_path)

    # Compare the results
    print("Comparing 'before' and 'after' API calls...")
    compare_responses(test_run_dir, db_path, )

    # Report duration and record end time to config.json
    report_run_duration(test_run_dir)


if __name__ == "__main__":
    main()
