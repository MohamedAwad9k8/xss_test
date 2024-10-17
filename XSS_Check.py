import os
import re
import csv

def scan_directory(directory):
    # Create or open the CSV file for writing findings
    with open('xss_findings.csv', 'w', newline='', encoding='utf-8') as csvfile:
        csv_writer = csv.writer(csvfile)
        # Write header row in CSV
        csv_writer.writerow(['File Path', 'Line Number', 'Vulnerability'])

        # Iterate through all files in the directory
        for root, _, files in os.walk(directory):
            for file in files:
                if file.endswith('.php'):
                    file_path = os.path.join(root, file)
                    print(f"Checking plugin: {file_path}")  # Print current plugin being checked
                    scan_file_for_xss(file_path, csv_writer)

def scan_file_for_xss(file_path, csv_writer):
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            lines = file.readlines()
    except UnicodeDecodeError:
        print(f"Skipping file due to encoding issues: {file_path}")
        return  # Skip this file if there's an encoding error

    for line_number, line in enumerate(lines, start=1):
        # Check for an echo statement
        if re.search(r'(?i)(echo|print|<\?=)', line):
            # Now check the next line for $_GET, $_POST, $_REQUEST, $_COOKIE
            if line_number + 1 < len(lines):
                next_line = lines[line_number + 1]  # Adjusted to access the next line correctly
                # Check if the next line contains any of the globals and does NOT contain restricted functions or 'nonce'
                if (re.search(r'\$_(GET|POST|REQUEST|COOKIE)', next_line) and 
                        not re.search(r'\b(esc_|admin_url|int\(|htmlentities|nonce)\b', next_line)):
                    finding = f"Potential usage of $_GET, $_POST, $_REQUEST, or $_COOKIE after echo in {file_path} at line {line_number + 1}:"
                    print(finding)
                    print(f"    {next_line.strip()}\n")

                    # Write finding to CSV
                    csv_writer.writerow([file_path, line_number + 1, next_line.strip()])

# Set the directory you want to scan
directory_to_scan = 'plugins2'  # Update this path
scan_directory(directory_to_scan)
