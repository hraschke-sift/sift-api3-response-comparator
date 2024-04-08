# cli_tool.py

import argparse
import json

def main():
    parser = argparse.ArgumentParser(description="Generate calls.json for API call runs")
    parser.add_argument("-o", "--output", help="Output file path for calls.json", default="calls.json")
    args = parser.parse_args()

    env = input("Enter environment (dev/expr/stg1/prod): ")
    valid_env_options = ['dev', 'expr', 'stg1', 'prod']
    while env not in valid_env_options:
      print("Invalid environment. Please enter a valid environment (dev/expr/stg1/prod):")
      env = input("Enter environment (dev/expr/stg1/prod): ")

    url_options = {
      'dev': 'https://localhost:5323',
      'expr': 'https://experiment-console.sift.com',
      'stg1': 'https://staging-console.sift.com',
      'prod': 'https://console.sift.com'
    }
    url = url_options.get(env, '')

    cids = input("Enter customer IDs separated by comma: ").split(",")
    calls = []
    more_calls = True

    while more_calls:
        call = {}
        call['url'] = input(f"Enter call endpoint: {url}/v3/accounts/<cid>/")
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

    with open(args.output, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

    print(f"calls.json has been saved to {args.output}")

if __name__ == "__main__":
    main()
