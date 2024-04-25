import re
import json
import csv
import csv


def make_path_string(path, warnings_entry):
    path_string = re.sub(r"root\['(.*?)'\]", r"\1", path).replace("']['", " > ")
    if path_string in warnings_entry.keys():
        path_string += f" ({warnings_entry[path_string]}% change detected)"
    path_string = " > ".join(
        [part.replace("_", " ").title() for part in path_string.split(" > ")]
    )
    return path_string


customer_name_mapping = {
    "54c57697c06fd48799000405": "Doordash",
    "60aeb07bbe968e78ea29d9d5": "McDonald's Corporation (US)",
    "5da8a1994f0c1789dd5a826e": "McDonald's Corporation (UK)",
    "517195f6c06fd4670b008051": "Remitly",
    "62ffe9d3980dc259d981eb5e": "Draftkings (non-NJ)",
    "62ffe64415ec912f7c94c7a8": "Draftkings (NJ)",
    "5e41957def0aa956dad5700a": "Kraken",
    "5af8c1844f0c269f4289bb29": "The Estee Lauder Companies Inc.",
    "5a8f507f4f0c42ea22d66f0c": "TapTap Send",
    "60f88a09293fb116c8220750": "FanDuel",
    "5ecea9fbef0a3f7a488c0d50": "Uphold",
    "589cf354e4b054e606d8845b": "Poshmark",
    "4e1a50e172beb95cf1e4ae54": "siftscience",
    "5e8e233bef0a760715782023": "demousers",
}

with open("./results-to-parse.json", "r") as f:
    data_entries = json.load(f)

with open("runs/1713278139_stg1/warnings.json", "r") as f:
    warnings = json.load(f)

with open("runs/1713278139_stg1/type_changes.json", "r") as f:
    type_changes = json.load(f).get("type_changes_by_endpoint", {})


formatted_data = []
for endpoint, cid_entry in data_entries.items():
    for cid, details in cid_entry.items():
        customer_name = customer_name_mapping.get(cid, "Unknown Company")
        warnings_entry = warnings.get(f"{endpoint}-{cid}", {})

        affected_paths = []
        change_types = []
        for key, changes in details.items():
            if key == "values_changed":
                for path, changes in changes.items():

                    # Add the path to the list of affected paths
                    affected_paths.append(make_path_string(path, warnings_entry))

                    # Determine the type and magnitude of change
                    if isinstance(changes["new_value"], (int, float)) and isinstance(
                        changes["old_value"], (int, float)
                    ):
                        if changes["new_value"] > changes["old_value"]:
                            if changes["new_value"] > 1.1 * changes["old_value"]:
                                change_types.append("Significant Increase")
                            else:
                                change_types.append("Increase")
                        if changes["new_value"] < changes["old_value"]:
                            if changes["new_value"] < 0.9 * changes["old_value"]:
                                change_types.append("Significant Decrease")
                            else:
                                change_types.append("Decrease")

                    elif isinstance(changes["new_value"], dict) and isinstance(
                        changes["old_value"], dict
                    ):
                        for key, val in changes["new_value"].items():
                            if val == changes["old_value"][key]:
                                continue
                            if not isinstance(val, (int, float)) or not isinstance(
                                changes["old_value"][key], (int, float)
                            ):
                                continue
                            if val > changes["old_value"][key]:
                                if val > 1.1 * changes["old_value"][key]:
                                    change_types.append("Significant Increase")
                                else:
                                    change_types.append("Increase")
                            if val < changes["old_value"][key]:
                                if val < 0.9 * changes["old_value"][key]:
                                    change_types.append("Significant Decrease")
                                else:
                                    change_types.append("Decrease")
                    elif isinstance(changes["new_value"], str) and isinstance(
                        changes["old_value"], str
                    ):
                        change_types.append("String Change")
                    else:
                        change_types.append("Unknown Change")

            if key == "iterable_item_added":
                for path in changes.keys():
                    affected_paths.append(make_path_string(path, warnings_entry))
                    change_types.append("Addition")

            if key == "iterable_item_removed":
                for path in changes.keys():
                    affected_paths.append(make_path_string(path, warnings_entry))
                    change_types.append("Removal of entry")

            # parse type changes
            associated_type_changes = type_changes.get(endpoint, {}).get(cid, {})
            for path, changes in associated_type_changes.items():
                affected_paths.append(make_path_string(path, warnings_entry))
                change_types.append("Type Change")

            # de-dedupe array entries in affected paths
            array_type_paths = {}
            paths_to_remove = []
            for path in affected_paths:
                if re.search(r"\[\d+\]", path):
                    array_path = re.sub(r"\[\d+\]", "?", path)
                    if array_path not in array_type_paths:
                        array_type_paths[array_path] = 0
                    array_type_paths[array_path] += 1
                    paths_to_remove.append(path)

            for path in paths_to_remove:
                affected_paths.remove(path)

            for path, count in array_type_paths.items():
                unique_path = f"{path} ({count} entries)"
                # Remove question mark from the end of the string
                if unique_path.endswith("?"):
                    unique_path = unique_path[:-1]
                # Replace question mark in the middle of the string
                unique_path = unique_path.replace("?", " array entries - ")
                affected_paths.append(unique_path)

            # determine change types
            change_assessment = ""
            unique_change_types = sorted(
                set(change_types), key=lambda ct: change_types.count(ct), reverse=True
            )
            if len(change_types) == 0:
                change_assessment = "No changes"
            elif len(unique_change_types) == 1:
                change_assessment = f"All {unique_change_types[0]}s"
            else:
                for ct in unique_change_types:
                    if change_types.count(ct) > len(change_types) / 2:
                        change_assessment += f"Mostly {ct}s"
                    elif change_types.count(ct) > len(change_types) / 3:
                        change_assessment += f"Many {ct}s"
                    elif change_types.count(ct) > len(change_types) / 4:
                        change_assessment += f"Some {ct}s"
                    else:
                        change_assessment += f"A few {ct}s"
                    if ct != unique_change_types[-1]:
                        change_assessment += ", "

            # add to formatted data
            formatted_data.append(
                {
                    "Endpoint": endpoint,
                    "Customer Name": customer_name,
                    "Affected Keys": affected_paths,
                    "Warning": "Yes" if warnings_entry else "No",
                    "Change Assessment": change_assessment,
                }
            )

with open("formatted_results.json", "w") as f:
    json.dump(formatted_data, f, indent=4)

# CSV formatting
header = formatted_data[0].keys()
rows = [
    list(
        str(value) if not isinstance(value, list) else "\n".join(value)
        for value in d.values()
    )
    for d in formatted_data
]

# Write to CSV file
with open("formatted_results.csv", "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(header)
    writer.writerows(rows)
