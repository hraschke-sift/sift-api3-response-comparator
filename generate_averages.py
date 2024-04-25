import json
import os
from collections import defaultdict

def calculate_averages(runs_dir):
    # Initialize a dictionary to store the sum of values and the count of reports
    sums = defaultdict(lambda: {'value': 0, 'count': 0})
    report_count = 0

    # Iterate through all files in the specified directory
    for test_run_dir in os.listdir(runs_dir):
        if not os.path.isdir(os.path.join(runs_dir, test_run_dir)):
            continue
        for filename in os.listdir(os.path.join(runs_dir, test_run_dir)):
          if filename.endswith('.json') and filename.startswith('report'):
              filepath = os.path.join(runs_dir, test_run_dir, filename)
              with open(filepath, 'r') as file:
                  data = json.load(file)
                  report_count += 1
                  # Sum the values for each key
                  for key, value in data.items():
                      key = key.split('_')[1] # remove leading index
                      sums[key]['value'] += value
                      sums[key]['count'] += 1

    # Calculate averages
    averages = {key: sum['value'] / sum['count'] for key, sum in sums.items()}

    # Calculate the standard deviation
    # Initialize a dictionary to store the sum of squared differences
    squared_diff_sums = defaultdict(lambda: {'value': 0, 'count': 0})
    for test_run_dir in os.listdir(runs_dir):
      if not os.path.isdir(os.path.join(runs_dir, test_run_dir)):
        continue
      for filename in os.listdir(os.path.join(runs_dir, test_run_dir)):
        if filename.endswith('.json') and filename.startswith('report'):
          filepath = os.path.join(runs_dir, test_run_dir, filename)
          with open(filepath, 'r') as file:
            data = json.load(file)
            # Sum the squared differences for each key
            for key, value in data.items():
              key = key.split('_')[1] # remove leading index
              squared_diff_sums[key]['value'] += (value - averages[key]) ** 2
              squared_diff_sums[key]['count'] += 1

    print("total reports processed: ", report_count)

    # Save the averages to a new JSON file
    data = {}
    for key, sum in sums.items():
        data[key] = {
            "average": averages[key],
            "standard_deviation": (squared_diff_sums[key]['value'] / squared_diff_sums[key]['count']) ** 0.5,
            "count": sum['count']
        }
    with open('averages.json', 'w') as file:
        json.dump(data, file, indent=4)

    print("Averages calculated and saved to averages.json.")

# Usage example:
# Replace '/path/to/reports/directory' with the actual path to your reports directory
calculate_averages('runs/')
