import subprocess
import pandas as pd
import re
import argparse
import os

def get_pod_uid_mapping():
    """Fetch running pod names and their UIDs from Kubernetes."""
    result = subprocess.run(
        ["kubectl", "get", "pods", "--all-namespaces", "-o", "custom-columns=Name:.metadata.name,UID:.metadata.uid"],
        capture_output=True, text=True
    )

    pod_uid_map = {}
    lines = result.stdout.strip().split("\n")[1:]  # Skip header
    
    for line in lines:
        parts = line.split()
        if len(parts) == 2:
            pod_name, pod_uid = parts
            pod_uid_map[pod_name] = pod_uid
    return pod_uid_map

def normalize_pod_name(pod_name):
    """Convert pod name format in CSV to match Kubernetes format (underscores to dashes)."""
    if isinstance(pod_name, str):
        return re.sub(r'_', '-', pod_name[3:])
    return ""  # Return an empty string for NaN or None values

def filter_csv(input_file, output_file, pod_uid_map):
    """Filter CSV to keep rows where pod's UID matches a running Kubernetes pod."""
    df = pd.read_csv(input_file)

    # Normalize pod names from CSV to match Kubernetes pod names
    df["normalized_name"] = df["uid"].apply(normalize_pod_name)
    # Replace pod names with their corresponding UIDs
    uid_to_pod_name = {v: k for k, v in pod_uid_map.items()}
    df["pod_name"] = df["normalized_name"].map(uid_to_pod_name)

    # Filter rows where a valid UID was found
    filtered_df = df[df["pod_name"].notna()]
    filtered_df = filtered_df[["metric", "timestamp", "value", "pod_name"]]
    # Drop temporary columns and save output
    filtered_df.to_csv(output_file, index=False)
    print(f"Filtered data saved to {output_file}")

def main():
    # Set up argument parser
    parser = argparse.ArgumentParser(description="Filter CSV based on Kubernetes pod UIDs.")
    parser.add_argument("--input_file", default="alumet-output.csv", help="Path to the input CSV file")
    parser.add_argument("--output_file", default="output.csv", help="Path to the output CSV file")
   

    # Parse arguments
    args = parser.parse_args()
    if not os.path.exists(args.input_file):
        parser.error(f"Input file '{args.input_file}' does not exist.")
    # Get pod UID mapping
    pod_uid_map = get_pod_uid_mapping()
    
    # Filter CSV with provided input and output files
    filter_csv(args.input_file, args.output_file, pod_uid_map)

if __name__ == "__main__":
    main()