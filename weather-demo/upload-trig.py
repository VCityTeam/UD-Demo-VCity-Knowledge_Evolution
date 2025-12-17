#!/usr/bin/env python3
import os
import sys
from datetime import datetime
import requests
from dotenv import load_dotenv

load_dotenv()

def upload_trig_file():
    """Upload the .trig file for the current day to quads-loader."""
    
    # Get current date
    now = datetime.now()
    year = now.strftime("%Y")
    month = now.strftime("%m")
    day = now.strftime("%d")
    
    file_path = f"weather-data/{year}/{month}/{day}/{year}-{month}-{day}.trig"
    
    if not os.path.exists(file_path):
        print(f"Error: File not found: {file_path}", file=sys.stderr)
        sys.exit(1)
    
    url = os.getenv("QUADS_LOADER_URL")
    
    try:
        with open(file_path, 'rb') as f:
            files = {'file': (os.path.basename(file_path), f, 'application/trig')}
            
            response = requests.post(
                url,
                files=files,
                timeout=(180, None) 
            )
            
            response.raise_for_status()
            
            print(f"Successfully uploaded {file_path}")
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
