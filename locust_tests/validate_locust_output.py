#!/usr/bin/env python3
import json
import sys
import os
import re

def validate_locust_output(output_file=None):
    """
    Validate the Locust output to ensure:
    1. Two stats are printed (performance metrics and locust stats)
    2. There are some names in the stats
    3. Requests are successful
    4. Performance metrics are not 0
    """
    # Read the output file if provided, otherwise read from stdin
    if output_file and os.path.exists(output_file):
        with open(output_file, 'r') as f:
            output = f.read()
    else:
        output = sys.stdin.read()

    # Extract the two JSON outputs using regex
    json_pattern = r'\[\n\s+\{.*?\}\n\]'
    json_matches = re.findall(json_pattern, output, re.DOTALL)
    
    if len(json_matches) < 2:
        print(f"Error: Expected at least 2 JSON outputs, but found {len(json_matches)}")
        return False
    
    # Parse the JSON outputs
    try:
        performance_metrics = json.loads(json_matches[0])
        locust_stats = json.loads(json_matches[1])
    except json.JSONDecodeError as e:
        print(f"Error parsing JSON: {e}")
        return False
    
    # Validate performance metrics
    if not performance_metrics:
        print("Error: No performance metrics found")
        return False
    
    # Check that there are some names in the performance metrics
    if not all('name' in metric for metric in performance_metrics):
        print("Error: Not all performance metrics have a 'name' field")
        return False
    
    # Check that performance metrics are not 0
    for metric in performance_metrics:
        if metric.get('sql_count', 0) == 0 and metric.get('cpu_time', 0) == 0:
            print(f"Error: Performance metrics are 0 for {metric.get('name')}")
            return False
    
    # Validate locust stats
    if not locust_stats:
        print("Error: No locust stats found")
        return False
    
    # Check that there are some names in the locust stats
    if not all('name' in stat for stat in locust_stats):
        print("Error: Not all locust stats have a 'name' field")
        return False
    
    # Check that requests are successful
    for stat in locust_stats:
        if stat.get('num_failures', 0) > 0:
            print(f"Error: Found failures for {stat.get('name')}")
            return False
    
    print("Validation successful!")
    return True

if __name__ == "__main__":
    # If an output file is provided as an argument, use it
    output_file = sys.argv[1] if len(sys.argv) > 1 else None
    
    if not validate_locust_output(output_file):
        sys.exit(1)