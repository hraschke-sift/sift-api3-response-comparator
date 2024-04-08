from api_client import make_api_call
from cli_tool import generate_calls_json
from utils import create_run_directory, load_json_file, update_response_file, compare_responses
import os

auth_endpoint = "https://api3.siftscience.com"

def execute_api_calls(run_order, test_run_dir='runs/'):
    calls_config = load_json_file(f"{test_run_dir}/calls.json")
    base_url = calls_config['base_url']
    cids = calls_config['cids']
    calls = calls_config['calls']

    for cid in cids:
        for call in calls:
            # Construct the full API endpoint URL
            url = f"/v3/accounts/{cid}/{call['url'].lstrip('/')}"  # Ensure no double slashes
            response_data = make_api_call(url, call['method'], body=call.get('body'), base_url=base_url, auth_endpoint=auth_endpoint)

            # Save response data
            if response_data:
                update_response_file(test_run_dir, run_order, cid, response_data)

    print(f"API calls for {run_order} completed and stored in {run_directory}.")


def main():
    # Get environment and create test run directory
    env = input("Enter environment (dev/expr/stg1/prod): ")
    valid_env_options = ['dev', 'expr', 'stg1', 'prod']
    while env not in valid_env_options:
      print("Invalid environment. Please enter a valid environment (dev/expr/stg1/prod):")
      env = input("Enter environment (dev/expr/stg1/prod): ")

    test_run_dir = create_run_directory("runs/", env)

    # Generate calls.json via CLI prompts
    generate_calls_json(test_run_dir, env)

    # Execute API calls for "before"
    print("Executing 'before' API calls...")
    execute_api_calls("before", test_run_dir)

    # Pause for database migration
    input("Please complete the database migration now. Press Enter to continue once done...")

    # Execute API calls for "after"
    print("Executing 'after' API calls...")
    execute_api_calls("after", test_run_dir)

    # Compare the results
    print("Comparing 'before' and 'after' API calls...")
    compare_responses(test_run_dir)

if __name__ == "__main__":
    main()
