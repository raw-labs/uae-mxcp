#!/usr/bin/env python3

import boto3
import argparse
from pathlib import Path
import sys

def download_real_data(output_path):
    """Download the real license data from S3."""
    try:
        s3 = boto3.client('s3')
        bucket = 'rawlabs-private-test-data'
        key = 'projects/uae_business_licenses/licenses.csv'
        
        print(f"Downloading real data from s3://{bucket}/{key}...")
        s3.download_file(bucket, key, output_path)
        print(f"Successfully downloaded to {output_path}")
        
    except Exception as e:
        print(f"Error downloading data: {e}", file=sys.stderr)
        print("\nMake sure you have:")
        print("1. AWS credentials configured")
        print("2. Access to the rawlabs-private-test-data bucket")
        print("3. Write permissions in the output directory")
        sys.exit(1)

def main():
    parser = argparse.ArgumentParser(description='Download real UAE business license data from S3')
    parser.add_argument('--output', type=str, required=True,
                      help='Output file path (e.g., seeds/licenses.csv)')
    
    args = parser.parse_args()
    
    # Create output directory if it doesn't exist
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    download_real_data(str(output_path))

if __name__ == '__main__':
    main() 