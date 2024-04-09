# API3 Data Quality Validation Tool

This Python tool automates the process of validating database migrations and API3 changes that specifically affect data in the console by comparing API responses before and after the migration. It's designed to ensure that changes in the database or code do not unintentionally affect the outputs of various API calls.

This tool was built specifically for the [Snowflake Insights Migration in 2024](https://sift.atlassian.net/wiki/spaces/RNDTEAM/pages/2257289611/Standardize+Console+Reporting+Data). It assumes all endpoints will begin with `/v3/accounts/{{customer_id}}/`. It could therefore be used to test any call that starts with that combination.

## Features
This project uses the same config file as the ruby [api3 client](https://github.com/SiftScience/ruby/tree/main/ruby/api3_client), so if you have authenticated with this tool or the other, they will share a bearer token.
NOTE: This is no longer true. Instead of `~/.api3_client.yaml`, it now uses `~/.api3_tokens.yaml`, which stores environment-specific tokens.

## Prerequisites
Before you begin, ensure you have met the following requirements:

- Python 3.8+
- `pip` for installing Python packages

## Installation
1. **Clone the repository**:

```sh
git clone git@github.com:hraschke-sift/sift-api3-response-comparator.git
cd sift-api3-response-comparator
```
2. **Set up a virtual environment** (recommended):
```
sh
Copy code
python3 -m venv venv
source venv/bin/activate
```
3. **Install Dependencies**:
```
pip install -r requirements.txt
```

## Usage

### Intended Use Case
This tool assumes that you are running a series of requests for a series of Customers. You can run the tool in any of four environments:
* "dev": https://localhost:5323
* "expr": https://experiment-console.sift.com
* "stg1": https://staging-console.siftscience.com
* "prod": https://console.siftscience.com

Before you begin, collect the CIDs for the customers that you want to run these requests for and make sure you have access to their data ([Request Spoofing](https://sift.atlassian.net/wiki/spaces/RNDTEAM/pages/1821803264/Sift+Admin+Permissions+Policy#Requesting-Access-(employee))).

You will also want to compile a list of the API3 endpoints that you will want to hit. All of them will need to begin with `/v3/accounts/{{cid}}/`, where `cid` will be filled in with the customer ids you collected. Copy all requests starting with the text after the customer id and paste them into a list. You will add them one-by-one using the prompter.

### Execution

Run the tool by running the following from the root directory.
```
python src/main.py
```

You will be lead through a series of prompts:

1. **Enter Environment**: You must choose your environment by entering one of dev, expr,stg1, or prod. If you enter an invalid string, the tool will prompt you again.

At this point, the test tool will make a directory in `runs/` with your chosed environment and the timestamp of the test run. It is in here where all of your data will be stored.

2. **Paste Completed JSON**: If you want to execute a past test with the same CID and Request options, you can copy the contents of a `rerun.json` file inside a previous run and paste it here. The environment you selected and the run timestamp will replace the one in the previous run (for example, selecting `prod` in the last step will mean this run will execute in `prod`, even if the `reruns.json` specifies `stg1`).

To enter CIDs and Requests manually, ignore this step.

3. **Enter Customer IDs**: Enter a list of CIDs, with commas separating them. Whitespace is ignored.

4. **Enter Calls**: The prompter will next allow you to enter calls, one-by-one. Each call will include the following:
  * Endpoint: The url suffix will be populated for you automatically. Complete the endpoint with the desired extension (and parameters, for GET calls).
  * Method: Choose GET or POST
  * (Optional) Body: If you chose POST, enter a JSON-formatted body now. Keep in mind it must be a single line of valid JSON.

The prompt will then ask if you want to enter a new call. If you enter "y", you will go through the above steps again. Enter "n" and you will proceed to the test execution.

The tool will then make a json file at `runs/calls.json`. This will include all test data and will be used during execution to make all the necessary requests.

5. **Test Run**: At this point, all the calls will be made for each customer and retrieved data will be stored in `runs/before.json`. You may be asked to enter your username and password for the Sift Console, as well as a TOTP token. __Make sure to use your sift console credentials and OTP! Not Okta.__

After all the calls have been executed, you will see a prompt telling you the following:

```Please complete the database migration now. Press Enter to continue once done...```

It's at this point that you should deploy any underlying code or database changes. Hit return to continue.

The test tool will then make the same calls again, storing the outputs in `runs/after.json`.

Once it has finished, the tool will compare the `before.json` and `after.json` files. If there is a difference, it will record that to the `results.json` file (also in the `runs/directory`).


## Project Structure

Below is an overview of the key directories and files within the Database Migration Validation Tool project:
```
sift-api3-response-comparator/
│
├── src/ # Source code for the tool
│ ├── api_client.py # Module for making API requests
│ ├── auth.py # Authentication module for API calls
│ ├── user_input_client.py # tool for taking inputs & generating calls.json configuration
│ ├── main.py # Main script for orchestrating the validation process
│ └── utils.py # Utility functions, including file operations and comparison logic
│
├── runs/ # Directory for storing run configurations and results
│ ├── calls.json # Configuration file generated by cli_tool.py
│ ├── before.json # API responses collected before the database migration
│ ├── after.json # API responses collected after the database migration
│ ├── results.json # Results of comparing before and after responses
│ └── rerun.json # Formatted json that can be copied and pasted for reruns
│
├── venv/ # Virtual environment for the project (not tracked by Git)
│
├── .gitignore
├── requirements.txt
└── README.md
```

- **src/**: Contains all the Python source files needed to run and manage the tool.
- **runs/**: This directory is used to store the config for each run (`calls.json`) along with the responses before and after the migration (`before.json` and `after.json`), and the comparison results (`results.json`). It also holds a file with formatted json that can be copied and pasted in a subsequent run to make it match the configs (`rerun.json`).
- **venv/**: Recommended directory for the Python virtual environment to ensure dependencies are isolated from the system's Python environment.

Please note, the `runs/` and `venv/` directories are generated during the use of the tool and should not be included in version control (as specified in `.gitignore`).

## Changelog
### [0.0.1] - 2024-04-08
Initial version. Known bugs:
- in non-production environments, we always get 401s

### [0.1.0] - 2024-04-08
Bug fix for 401s in other environments. Now uses environment-specific auth.