# API3 Data Quality Validation Tool

This Python tool automates the process of validating database migrations and API3 changes that specifically affect data in the console by comparing API responses before and after the migration. It's designed to ensure that changes in the database or code do not unintentionally affect the outputs of various API calls.

This tool was built specifically for the [Snowflake Insights Migration in 2024](https://sift.atlassian.net/wiki/spaces/RNDTEAM/pages/2257289611/Standardize+Console+Reporting+Data). It assumes all endpoints will begin with `/v3/accounts/{{customer_id}}/`. It could therefore be used to test any call that starts with that combination.

## Features
This project uses the same config file as the ruby [api3 client](https://github.com/SiftScience/ruby/tree/main/ruby/api3_client), so if you have authenticated with this tool or the other, they will share a bearer token.
NOTE: This is no longer true. Instead of `~/.api3_client.yaml`, it now uses `~/.api3_tokens.yaml`, which stores environment-specific tokens.

Authentication supports storing `USERNAME` and `PASSWORD` variables in a local `.env` file. Here is an example structure:

```sh
# .env

USERNAME="my_user@siftscience.com"
PASSWORD="myConsolePassword123!"
```

If these variables exist, they will not be prompted when authentication is made. You will still need to enter your six-digit TOTP.

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
```sh
python3 -m venv venv
source venv/bin/activate
```

3. **Install Dependencies**:
```
pip install .
```
This command installs the package and all dependencies as specified in setup.py. It's recommended for most users who just need to run the tool.

## Development Installation
If you plan to modify the code, run tests, or contribute to the project, you'll want to install the development dependencies as well.

Follow steps 1 and 2 above to clone the repository and set up a virtual environment.

Install the package with development dependencies:

```sh
pip install -e .[dev]
```

This command installs the package in editable mode and includes extra dependencies necessary for development such as linters and testing tools.

## Usage

### Intended Use Case
This tool assumes that you are running a series of requests for a series of Customers. You can run the tool in any of four environments:
* "dev": https://localhost:5323
* "expr": https://experiment-console.sift.com
* "stg1": https://staging-console.siftscience.com
* "prod": https://console.siftscience.com

Before you begin, collect the CIDs for the customers that you want to run these requests for and make sure you have access to their data ([Request Spoofing](https://sift.atlassian.net/wiki/spaces/RNDTEAM/pages/1821803264/Sift+Admin+Permissions+Policy#Requesting-Access-(employee))).

You will also want to compile a list of the API3 endpoints that you will want to hit. All of them will need to begin with `/v3/accounts/{{cid}}/`, where `cid` will be filled in with the customer ids you collected. Copy all requests starting with the text after the customer id and paste them into a list. You will add them one-by-one using the prompter.

### Running the Tool

After installation, you can run the tool from any directory using the command-line interface:

```sh
api3-comparator [COMMAND] [OPTIONS]
For help on the available commands and options, run:
```

```sh
api3-comparator --help
```

#### Specify Options with CLI
It is recommended you run the CLI with the following options:
* `--env [dev/expr/stg1/prod]`
* `--config-path [path-to-config-json]`

If you do so, you can skip the's tool's manual entry functionality.

#### Manual Input
If you do not enter options for environment and/or config path, you will be lead through a series of prompts:

1. **Enter Environment**: You must choose your environment by entering one of dev, expr,stg1, or prod. If you enter an invalid string, the tool will prompt you again.

At this point, the test tool will make a directory in `runs/` with your chosed environment and the timestamp of the test run. It is in here where all of your data will be stored.

2. **Skip Manual Entry**: If you have a completed config file, you can add it now to the test run directory. This is useful if you want to copy the same test run from a previous one. To do this, type "y" when prompted and add the file. You will be asked to press return to continue. __The environment will then be overwritten with your selection from the previous prompt__. This is helpful for running the same test in other environments. The start time will also be overwritten.

3. **Enter Customer IDs**: Enter a list of CIDs, with commas separating them. Whitespace is ignored.

4. **Enter Calls**: The prompter will next allow you to enter calls, one-by-one. Each call will include the following:
  * Endpoint: The url suffix will be populated for you automatically. Complete the endpoint with the desired extension (and parameters, for GET calls).
  * Method: Choose GET or POST
  * (Optional) Body: If you chose POST, enter a JSON-formatted body now. Keep in mind it must be a single line of valid JSON.

The prompt will then ask if you want to enter a new call. If you enter "y", you will go through the above steps again. Enter "n" and you will proceed to the test execution.

The tool will then make a json file at `runs/config.json`. This will include all test data and will be used during execution to make all the necessary requests.

#### Text execution
**Test Run**: At this point, all the calls will be made for each customer and retrieved data will be stored in a local `sqlite` database file.

You may be asked to enter your username and password for the Sift Console, as well as a TOTP token. __Make sure to use your sift console credentials and OTP! Not Okta.__

After all the calls have been executed, you will see a prompt telling you the following:

```Please complete the database migration now. Press Enter to continue once done...```

It's at this point that you should deploy any underlying code or database changes. Hit return to continue.

The test tool will then make the same calls again, storing the outputs in a new column for each entry in the db.

Once it has finished, the tool will compare the `before_results` and `after_results` columns in the db. If there is a difference, it will record that to the `results.json` file (also found in the `runs/directory`, as a peer to `config.json`).

**Results Summary**: After your test run, the `results.json` output will be summarized into an average of the magnitude of all detected changes, organized by endpoint.

A `report.json` file will be generated that will show the averages of all the changes per entity. If you specified `--summary_type endpoint`, then it will show aggregated for 


## Project Structure

Below is an overview of the key directories and files within the Database Migration Validation Tool project:
```
sift-api3-response-comparator/
│
├── cli.py # CLI entry point
│
├── src/ # Source code for the tool
│ ├── api_client.py # Module for making API requests
│ ├── auth.py # Authentication module for API calls
│ ├── db.py # Module for interacting with the SQLite database
│ ├── user_input_client.py # tool for taking inputs & generating config.json
│ ├── main.py # Main script for orchestrating the validation process
│ ├── synthesize_results.py # Data handling for summarizing results.json by entity
│ └── utils.py # Utility functions, including file operations and comparison logic
│
├── runs/ # Directory for storing test run configs and results
├── venv/ # Virtual environment for the project (not tracked by Git)
│
├── .gitignore
├── requirements.txt
└── README.md
```

## Notes / Known Issues

## Changelog
### [0.0.1] - 2024-04-08
Initial version. Known bugs:
- in non-production environments, we always get 401s

### [0.1.0] - 2024-04-09
- Bug fix for 401s in other environments. Now uses environment-specific auth.

### [0.1.1] - 2024-04-10
- Changed naming conventions for runs directory
- Functionality for using .env for storing username and password
- Added execution time tracking
- Removed rerun functionality (not practical)

### [0.2.0] - 2024-04-10
- Added sqlite3 support to address performance issues
- Bug fixes
- Added color-coded command line outputs

### [0.2.1] - 2024-04-12
- Added change synthesis to see summary by endpoint, cid, or all changes

### [0.2.2] - 2024-04-14
- Added cli support
- packaged with setup.py
- updated readme