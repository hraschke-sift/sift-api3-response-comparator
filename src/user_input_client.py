import json

def generate_calls_json(test_run_dir="runs", env="dev"):
    """
    Generates a calls.json file based on user input.

    Parameters:
    - output: Output file path for calls.json
    - env: Environment specifier, used to determine the base URL
    """

    output = f"{test_run_dir}/calls.json"

    url_options = {
        'dev': 'https://localhost:5323',
        'expr': 'https://experiment-console.sift.com',
        'stg1': 'https://staging-console.sift.com',
        'prod': 'https://console.sift.com'
    }
    url = url_options.get(env, '')

    data_input_method = input("Do you want to paste completed JSON? (y/n): ").lower()

    if data_input_method == 'y':
        valid_json = False
        while not valid_json:
          data = json.loads(input("Paste your JSON here: "))

          # Validate the data JSON
          if not isinstance(data, dict):
            print("Invalid data JSON: Must be an object. Make sure it is a single line before posting.")
          elif not isinstance(data.get("base_url"), str):
            print("Invalid data JSON: 'base_url' must be a string")
          elif not isinstance(data.get("cids"), list):
            print("Invalid data JSON: 'cids' must be a list")
          elif not isinstance(data.get("calls"), list):
            print("Invalid data JSON: 'calls' must be a list")
          else: 
            valid_json = True

    else:
        cids = input("Enter customer IDs separated by comma: ").replace(" ", "").split(",")
        calls = []
        more_calls = True

        while more_calls:
            call = {}
            call_endpoint = input(f"Enter call endpoint: {url}/v3/accounts/<cid>/")
            call['url'] = call_endpoint
            call['method'] = input("Enter call method (GET/POST): ").upper()
            if call['method'] == 'POST':
                call['body'] = input("Enter call body (JSON format): ")
            calls.append(call)
            more_calls = input("Add another call? (y/n): ").lower() == 'y'

        data = {
            "base_url": url,
            "cids": cids,
            "calls": calls
        }
        data["rerun"] = json.dumps(data, separators=(',', ':'))

    with open(output, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

    print(f"calls.json has been saved to {output}")