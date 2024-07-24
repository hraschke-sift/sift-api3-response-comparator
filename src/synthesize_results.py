from typing import Any, Dict, List


def calculate_percentage_difference(old_value: Any, new_value: Any) -> float:
    try:
        if isinstance(old_value, (int, float)) and isinstance(new_value, (int, float)):
            return (
                abs(new_value - old_value) / max(abs(old_value), abs(new_value))
            ) * 100
        else:
            return 0.0
    except ZeroDivisionError:
        # choosing not to do infinite percentage difference, rather 0.0
        return 0.0


def process_arrays(old_items: List[Dict], new_items: List[Dict]) -> float:
    changes = []
    for idx, (old, new) in enumerate(zip(old_items, new_items)):
        for key in set(old.keys()).union(new.keys()):
            old_val = old.get(key)
            new_val = new.get(key)
            if isinstance(old_val, (int, float)) and isinstance(new_val, (int, float)):
                change_percentage = calculate_percentage_difference(old_val, new_val)
                changes.append(change_percentage)
    return sum(changes) / len(changes) if changes else 0.0


def append_threshold_warning(
    change_magnitude: float,
    identifier_string: str,
    change_path_string,
    threshold_warnings: Dict[str, Dict[str, float]],
) -> Dict[str, Dict[str, float]]:
    if change_magnitude > 5:
        if not threshold_warnings.get(identifier_string):
            threshold_warnings[identifier_string] = {}
        threshold_warnings[identifier_string][change_path_string] = change_magnitude
    return threshold_warnings


def summarize_all_changes(deepdiff_results: Dict[str, Any]) -> Dict[str, float]:
    results = {}
    threshold_warnings = {}
    for cid_index_endpoint, change_obj in deepdiff_results["all_results"].items():
        all_changes = []
        values_changed = change_obj.get("values_changed")
        if values_changed:  # There are changes to process
            for change_path_string, change_value_object in values_changed.items():
                old_value = change_value_object["old_value"]
                new_value = change_value_object["new_value"]
                if isinstance(old_value, list) and isinstance(new_value, list):
                    array_change_averages = process_arrays(old_value, new_value)
                    threshold_warnings = append_threshold_warning(
                        array_change_averages,
                        cid_index_endpoint,
                        change_path_string,
                        threshold_warnings,
                    )
                    all_changes.append(array_change_averages)
                elif isinstance(old_value, (int, float)) and isinstance(
                    new_value, (int, float)
                ):
                    change_percentage = calculate_percentage_difference(
                        old_value, new_value
                    )
                    threshold_warnings = append_threshold_warning(
                        change_percentage,
                        cid_index_endpoint,
                        change_path_string,
                        threshold_warnings,
                    )
                    all_changes.append(change_percentage)
        else:  # No changes, treat as 0 change
            all_changes.append(0.0)
        if all_changes:
            # Calculate average of all changes for this cid_index_endpoint
            results[cid_index_endpoint] = sum(all_changes) / len(all_changes)
    return results, threshold_warnings


def summarize_changes_by_endpoint(deepdiff_results: Dict[str, Any]) -> Dict[str, float]:
    results = {}
    threshold_warnings = {}
    for endpoint, cid_changes in deepdiff_results["results_by_endpoint"].items():
        magnitude_changes = []
        degree_changes = []
        counts_by_customer = {}
        for cid, change_obj in cid_changes.items():
            # just do table changes, ignore chart changes for now
            data_counts = change_obj.get("data_counts", {})
            change_counts = 0
            values_changed = change_obj.get("values_changed")
            if values_changed:  # There are changes to process
                for change_path_string, change_value_object in values_changed.items():
                    # just do table changes, ignore chart changes for now
                    if change_path_string.startswith("root['table']['data']"):
                        change_counts += 1
                    old_value = change_value_object["old_value"]
                    new_value = change_value_object["new_value"]
                    if isinstance(old_value, list) and isinstance(new_value, list):
                        magnitude_changes.append(process_arrays(old_value, new_value))
                    elif isinstance(old_value, (int, float)) and isinstance(
                        new_value, (int, float)
                    ):
                        percentage_difference = calculate_percentage_difference(
                            old_value, new_value
                        )
                        threshold_warnings = append_threshold_warning(
                            percentage_difference,
                            f"{endpoint}-{cid}",
                            change_path_string,
                            threshold_warnings,
                        )
                        magnitude_changes.append(percentage_difference)
            else:  # No changes, treat as 0 change
                magnitude_changes.append(0.0)
            # just do table changes, ignore chart changes for now
            degree_changes.append(
                change_counts / data_counts.get("table")
                if data_counts.get("table")
                else 0.0
            )
            counts_by_customer[cid] = {
                "total": data_counts.get("table", 0),
                "changed": change_counts,
            }

        results[endpoint] = {
            "magnitude": (
                sum(magnitude_changes) / len(magnitude_changes)
                if len(magnitude_changes) != 0
                else 0
            ),
            "degree": (
                sum(degree_changes) / len(degree_changes)
                if len(degree_changes) != 0
                else 0
            ),
            "data_counts": counts_by_customer,
        }
    return results, threshold_warnings


def summarize_changes_by_cid(deepdiff_results: Dict[str, Any]) -> Dict[str, float]:
    results = {}
    threshold_change = {}
    for cid, endpoints_changes in deepdiff_results["results_by_cid"].items():
        all_changes = []
        for endpoint, change_obj in endpoints_changes.items():
            values_changed = change_obj.get("values_changed")
            if values_changed:  # There are changes to process
                for change_path_string, change_value_object in values_changed.items():
                    old_value = change_value_object["old_value"]
                    new_value = change_value_object["new_value"]
                    if isinstance(old_value, list) and isinstance(new_value, list):
                        all_changes.append(process_arrays(old_value, new_value))
                    elif isinstance(old_value, (int, float)) and isinstance(
                        new_value, (int, float)
                    ):
                        percentage_change = calculate_percentage_difference(
                            old_value, new_value
                        )
                        threshold_change = append_threshold_warning(
                            percentage_change,
                            f"{cid}-{endpoint}",
                            change_path_string,
                            threshold_change,
                        )
                        all_changes.append(percentage_change)
            else:  # No changes, treat as 0 change
                all_changes.append(0.0)
        if all_changes:
            results[cid] = sum(all_changes) / len(all_changes)
    return results, threshold_change


def process_deepdiff_output(
    deepdiff_results: Dict[str, Any], summary_type: str = "endpoint"
) -> Dict[str, float]:
    if not summary_type or summary_type == "endpoint":
        return summarize_changes_by_endpoint(deepdiff_results)
    elif summary_type == "cid":
        return summarize_changes_by_cid(deepdiff_results)
    elif summary_type == "changes":
        return summarize_all_changes(deepdiff_results)
