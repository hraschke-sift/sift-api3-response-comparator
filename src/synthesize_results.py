import json
from typing import Any, Dict, List


def calculate_percentage_difference(old_value: Any, new_value: Any) -> float:
    try:
        if isinstance(old_value, (int, float)) and isinstance(new_value, (int, float)):
            return ((new_value - old_value) / max(abs(old_value), abs(new_value))) * 100
        else:
            return 0.0
    except ZeroDivisionError:
        # choosing not to do infinite percentage difference, rather 0.0
        return 0.0


def process_arrays(old_items: List[Dict], new_items: List[Dict]) -> float:
    """Process arrays of dictionaries and calculate a summarized change percentage."""
    changes = []
    for idx, (old, new) in enumerate(zip(old_items, new_items)):
        for key in set(old.keys()).union(new.keys()):
            old_val = old.get(key)
            new_val = new.get(key)
            if isinstance(old_val, (int, float)) and isinstance(new_val, (int, float)):
                changes.append(calculate_percentage_difference(old_val, new_val))
    return sum(changes) / len(changes) if changes else 0.0


def summarize_all_changes(deepdiff_results: Dict[str, Any]) -> Dict[str, float]:
    results = {}
    for cid_index_endpoint, change_obj in deepdiff_results["all_results"].items():
        all_changes = []
        values_changed = change_obj.get("values_changed")
        if values_changed:  # There are changes to process
            for value_change in values_changed.values():
                old_value = value_change["old_value"]
                new_value = value_change["new_value"]
                if isinstance(old_value, list) and isinstance(new_value, list):
                    all_changes.append(process_arrays(old_value, new_value))
                elif isinstance(old_value, (int, float)) and isinstance(
                    new_value, (int, float)
                ):
                    all_changes.append(
                        calculate_percentage_difference(old_value, new_value)
                    )
        else:  # No changes, treat as 0 change
            all_changes.append(0.0)
        if all_changes:
            # Calculate average of all changes for this cid_index_endpoint
            results[cid_index_endpoint] = sum(all_changes) / len(all_changes)
    return results


def summarize_changes_by_endpoint(deepdiff_results: Dict[str, Any]) -> Dict[str, float]:
    results = {}
    for endpoint, cid_changes in deepdiff_results["results_by_endpoint"].items():
        all_changes = []
        for cid, change_obj in cid_changes.items():
            values_changed = change_obj.get("values_changed")
            if values_changed:  # There are changes to process
                for value_change in values_changed.values():
                    old_value = value_change["old_value"]
                    new_value = value_change["new_value"]
                    if isinstance(old_value, list) and isinstance(new_value, list):
                        all_changes.append(process_arrays(old_value, new_value))
                    elif isinstance(old_value, (int, float)) and isinstance(
                        new_value, (int, float)
                    ):
                        all_changes.append(
                            calculate_percentage_difference(old_value, new_value)
                        )
            else:  # No changes, treat as 0 change
                all_changes.append(0.0)
        if all_changes:
            results[endpoint] = sum(all_changes) / len(all_changes)
    return results


def process_deepdiff_output(deepdiff_results: Dict[str, Any]) -> Dict[str, float]:
    """Process the structured deepdiff results based on provided interfaces."""
    return summarize_changes_by_endpoint(deepdiff_results)


# Example usage
deepdiff_results = json.load(open("runs/1712944999_stg1/results.json"))
results_summary = process_deepdiff_output(deepdiff_results)

# Output the results
print(json.dumps(results_summary, indent=4))
