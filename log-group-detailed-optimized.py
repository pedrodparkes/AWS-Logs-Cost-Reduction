import json
import subprocess
from datetime import datetime
import csv

def run_aws_command(command):
    result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
    if result.returncode != 0:
        print(f"Error running command: {command}")
        print(result.stderr.decode())
        return None
    return json.loads(result.stdout.decode())

def get_log_groups(region):
    command = f"aws logs describe-log-groups --region {region} --query 'logGroups[*].[logGroupName,retentionInDays,storedBytes,lastIngestionTime]' --output json"
    return run_aws_command(command)

def get_latest_log_stream(log_group_name, region):
    command = f"aws logs describe-log-streams --log-group-name {log_group_name} --region {region} --order-by LastEventTime --descending --limit 1 --query 'logStreams[*].lastIngestionTime' --output json"
    return run_aws_command(command)

def get_log_group_streams(log_group_name, region):
    command = f"aws logs describe-log-streams --log-group-name {log_group_name} --region {region} --query 'logStreams[*].[lastIngestionTime]' --output json"
    return run_aws_command(command)

def format_timestamp(timestamp):
    return datetime.utcfromtimestamp(timestamp / 1000).strftime('%Y-%m-%d') if timestamp else "N/A"

def bytes_to_gb(bytes_size):
    return bytes_size / (1024 ** 3)

def main():
    regions = [
        'us-east-1', 'us-east-2', 'us-west-1', 'us-west-2', 'ap-south-1',
        'ap-northeast-1', 'ap-northeast-2', 'ap-northeast-3', 'ap-southeast-1', 'ap-southeast-2',
        'ca-central-1', 'eu-central-1', 'eu-west-1', 'eu-west-2', 'eu-west-3', 'eu-north-1', 'sa-east-1'
    ]

    table = []

    for region in regions:
        print(f"Processing region: {region}")
        log_groups = get_log_groups(region)
        if not log_groups:
            print(f"No log groups found in region {region}.")
            continue

        for log_group in log_groups:
            print(f"--> {log_group}")
            log_group_name = log_group[0]
            retention_period = log_group[1] if log_group[1] is not None else "Never Expire"
            stored_bytes = log_group[2] if log_group[2] is not None else 0
            total_size_gb = bytes_to_gb(stored_bytes)

            # Get the latest log stream to find the last ingestion time
            latest_log_stream = get_latest_log_stream(log_group_name, region)
            if latest_log_stream:
                last_ingestion_time = latest_log_stream[0] if latest_log_stream[0] is not None else None
                last_ingestion_date = format_timestamp(last_ingestion_time)
            else:
                last_ingestion_date = "N/A"

            row = {
                "region": region,
                "retention_period": retention_period,
                "log-group name": log_group_name,
                "log group stored data size (GB)": total_size_gb,
                "last ingestion time": last_ingestion_date
            }
            table.append(row)

    # Write the table to a CSV file
    csv_file = "log_groups_report-sec-ple.csv"
    with open(csv_file, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["Region", "Retention Period", "Log Group Name", "Stored Data Size (GB)", "Last Ingestion Time"])
        for row in table:
            writer.writerow([row['region'], row['retention_period'], row['log-group name'], f"{row['log group stored data size (GB)']:.2f}", row['last ingestion time']])

    print(f"Report has been saved to {csv_file}")

if __name__ == "__main__":
    main()