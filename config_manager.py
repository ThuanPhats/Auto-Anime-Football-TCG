import json
import os
import sys

CONFIG_FILE = "config.json"

def load_config():
    if not os.path.exists(CONFIG_FILE):
        print(f"[LỖI] Không tìm thấy file {CONFIG_FILE}.")
        print("Hãy tạo file config.json theo mẫu trước khi chạy.")
        sys.exit(1)
        
    try:
        with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except json.JSONDecodeError as e:
        print(f"[LỖI] File {CONFIG_FILE} sai định dạng JSON: {e}")
        sys.exit(1)