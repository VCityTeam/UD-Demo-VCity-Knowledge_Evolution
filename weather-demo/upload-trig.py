#!/usr/bin/env python3
"""
TriG File Uploader.

This script uploads the weather knowledge graph (.trig file) for the current day
to a quads-loader service. The file is expected to be in the following location:
weather-data/YYYY/MM/DD/YYYY-MM-DD.trig

Required environment variables:
- QUADS_LOADER_URL: URL endpoint for the quads-loader service
"""

import os
import sys
from datetime import datetime

import requests
from dotenv import load_dotenv

load_dotenv()

def upload_trig_file():
    """Upload the .trig file for the current day to quads-loader."""
    
    # Validate environment variable
    base_url = os.getenv("QUADS_LOADER_URL")
    if not base_url:
        print("Error: QUADS_LOADER_URL environment variable is not set", file=sys.stderr)
        sys.exit(1)
    
    # Get current date
    now = datetime.now()
    year = now.strftime("%Y")
    month = now.strftime("%m")
    day = now.strftime("%d")
    
    directory = f"weather-data/{year}/{month}/{day}"
    metadata_path = f"{directory}/metadata.ttl"
    file_path = f"{directory}/{year}-{month}-{day}.trig"
    
    if not os.path.exists(file_path):
        print(f"Error: File not found: {file_path}", file=sys.stderr)
        sys.exit(1)

    if not os.path.exists(metadata_path):
        print(f"Error: Metadata file not found: {metadata_path}", file=sys.stderr)
        sys.exit(1)
    
    try:
        with open(file_path, 'rb') as f:
            files = {'file': (os.path.basename(file_path), f, 'application/trig')}
            
            response = requests.post(
                f"{base_url}/import/version",
                files=files,
                timeout=(180, None) 
            )
            
            response.raise_for_status()
            
            print(f"Successfully uploaded {file_path}")
            print(f"Status code: {response.status_code}")
            print(f"Response: {response.text}")

        with open(metadata_path, 'rb') as f:
            files = {'file': (os.path.basename(metadata_path), f, 'application/turtle')}
            
            response = requests.post(
                f"{base_url}/import/metadata",
                files=files,
                timeout=(180, None) 
            )
            
            response.raise_for_status()
            
            print(f"Successfully uploaded {metadata_path}")
            print(f"Status code: {response.status_code}")
            print(f"Response: {response.text}")
    except requests.exceptions.Timeout:
        print(f"Error: Connection timeout while uploading {file_path}", file=sys.stderr)
        sys.exit(1)
    except requests.exceptions.RequestException as e:
        print(f"Error: Failed to upload {file_path}: {e}", file=sys.stderr)
        sys.exit(1)
    except IOError as e:
        print(f"Error: Failed to read file {file_path}: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    upload_trig_file()
