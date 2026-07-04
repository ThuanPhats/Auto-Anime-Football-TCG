import json
import os
import sys

CONFIG_FILE = "config/config.json"

def load_config():
    if not os.path.exists(CONFIG_FILE):
        print(f"[ERROR] File {CONFIG_FILE} not found.")
        print("Please create config.json from the template before running.")
        sys.exit(1)
        
    try:
        with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except json.JSONDecodeError as e:
        print(f"[ERROR] File {CONFIG_FILE} has invalid JSON format: {e}")
        sys.exit(1)