import json
import os

from output import c_print
from synthesize_results import process_deepdiff_output
from utils import compare_responses, load_json_file, report_run_duration


def main():
    runs_dir = "runs"
    summary_type = "endpoint"
    skip_dirs = []

    for test_run_dir in os.listdir(runs_dir):
        for skip_dir in skip_dirs:
            if skip_dir in test_run_dir:
                print("skipping:", test_run_dir)
                continue
        print("recording results again for:", test_run_dir)
        if not os.path.isdir(os.path.join(runs_dir, test_run_dir)):
            continue
        record_results(f"runs/{test_run_dir}", summary_type)


def record_results(test_run_dir, summary_type="endpoint"):
    print(f"Recording results for {test_run_dir}...")
    config_file = load_json_file(f"{test_run_dir}/config.json")
    cids = config_file["cids"]
    calls = config_file["calls"]

    # Compare the results
    c_print.blue("Comparing 'before' and 'after' API calls...")
    compare_responses(test_run_dir, f"{test_run_dir}/responses.db", cids, calls)

    # Process the output to summarized results
    # TODO(henry): Error here loading json file
    deepdiff_results = load_json_file(f"{test_run_dir}/results.json")
    results_summary, threshold_warnings = process_deepdiff_output(
        deepdiff_results, summary_type
    )
    report_file = f"{test_run_dir}/report.json"
    with open(report_file, "w") as f:
        json.dump(results_summary, f, indent=4)
    c_print.blue(f"Results summary written to {report_file}")

    warnings_file = f"{test_run_dir}/warnings.json"
    with open(warnings_file, "w") as f:
        json.dump(threshold_warnings, f, indent=4)
    c_print.blue(f"Warnings written to {warnings_file}")


if __name__ == "__main__":
    main()
