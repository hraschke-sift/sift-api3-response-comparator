from utils import load_json_file, update_response_file
from api_client import make_api_call
import os

auth_endpoint = "https://api3.siftscience.com"

def execute_api_calls(run_order, auth_endpoint, calls_file_path='calls.json', run_directory=''):
    calls_config = load_json_file(calls_file_path)
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
                full_run_path = os.path.join(run_directory, run_order)
                update_response_file(run_order, cid, response_data, full_run_path)

    print(f"API calls for {run_order} completed and stored in {run_directory}.")


