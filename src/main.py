from api_client import make_api_call
from user_input_client import generate_config_json
from utils import (
    create_run_directory,
    load_json_file,
    update_response_file,
    compare_responses,
    report_run_duration,
)


def execute_api_calls(run_order, test_run_dir="runs/", env="prod"):
    config_config = load_json_file(f"{test_run_dir}/config.json")
    base_url = config_config["base_url"]
    cids = config_config["cids"]
    calls = config_config["calls"]

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
                update_response_file(
                    test_run_dir, run_order, cid, call_string, response_data
                )
            else:
                update_response_file(
                    test_run_dir,
                    run_order,
                    cid,
                    call_string,
                    {"error": "API call failed"},
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

    # Generate config.json via CLI prompts
    generate_config_json(test_run_dir, env)
    input("Files generated. Press Enter to execute API calls...")

    # Execute API calls for "before"
    print("Executing 'before' API calls...")
    execute_api_calls("before", test_run_dir, env)

    # Pause for database migration
    input(
        "Please complete the database migration now. Press Enter to continue once done..."
    )

    # Execute API calls for "after"
    print("Executing 'after' API calls...")
    execute_api_calls("after", test_run_dir, env)

    # Compare the results
    print("Comparing 'before' and 'after' API calls...")
    compare_responses(test_run_dir)

    # Report duration and record end time to config.json
    report_run_duration(test_run_dir)


if __name__ == "__main__":
    main()
