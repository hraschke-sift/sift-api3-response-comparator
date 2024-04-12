import json
from typing import Any, Dict, List


def calculate_percentage_difference(old_value: Any, new_value: Any) -> float:
    try:
        if isinstance(old_value, (int, float)) and isinstance(new_value, (int, float)):
            return (
                ((new_value - old_value) / abs(old_value)) * 100
                if old_value
                else float("inf")
            )
        else:
            return 0.0  # Return 0 or other logic for non-numeric types
    except ZeroDivisionError:
        return float("inf")


def process_arrays(old_items: List[Dict], new_items: List[Dict]) -> float:
    """Process arrays of dictionaries and calculate a summarized change percentage."""
    changes = []
    # Create dictionaries by an identifiable unique key, or use the index if no clear key exists
    key = "name"  # Example key, could dynamically determine this or use index if not consistent
    old_by_key = {item.get(key, idx): item for idx, item in enumerate(old_items)}
    new_by_key = {item.get(key, idx): item for idx, item in enumerate(new_items)}

    all_keys = set(old_by_key.keys()).union(new_by_key.keys())
    for key in all_keys:
        old = old_by_key.get(key, {})
        new = new_by_key.get(key, {})
        for subkey in set(old.keys()).union(new.keys()):
            old_val = old.get(subkey)
            new_val = new.get(subkey)
            if isinstance(old_val, (int, float)) and isinstance(new_val, (int, float)):
                changes.append(calculate_percentage_difference(old_val, new_val))

    if not changes:
        return 0.0
    return sum(changes) / len(changes)  # Average percentage change across all items


def summarize_changes(changes: Dict[str, Any], results: Dict[str, float]) -> None:
    """Recursively summarize changes to compute percentage differences."""
    for cid_index_endpoint, change_obj in changes["all_results"].items():
        for change_path, value_change in change_obj["values_changed"].items():
            old_value = value_change["old_value"]
            new_value = value_change["new_value"]
            if isinstance(old_value, list) and isinstance(new_value, list):
                # Handle any list of dictionaries as a special case
                percentage_change = process_arrays(old_value, new_value)
                results[f"{cid_index_endpoint} | {change_path}"] = percentage_change
            elif isinstance(old_value, (int, float)) and isinstance(
                new_value, (int, float)
            ):
                # Handle simple numeric changes
                results[f"{cid_index_endpoint} | {change_path}"] = (
                    calculate_percentage_difference(old_value, new_value)
                )


def process_deepdiff_output(deepdiff_results: Dict[str, Any]) -> Dict[str, float]:
    """Process the structured deepdiff results based on provided interfaces."""
    results_summary = {}
    summarize_changes(deepdiff_results, results_summary)
    return results_summary


# Example usage
deepdiff_results = json.load(open("runs/1712944999_stg1/results.json"))
results_summary = process_deepdiff_output(deepdiff_results)

# Output the results
print(json.dumps(results_summary, indent=4))
