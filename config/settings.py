import os

def load_keys():
    base_dir = os.path.dirname(os.path.dirname(__file__))  # Goes one level up (from config/ to python-api/)
    key_file_path = os.path.join(base_dir, "key_secret.txt")
    
    with open(key_file_path, "r") as f:
        lines = [line.strip() for line in f.readlines()]
    
    return {
        "API_KEY": lines[0],
        "CLIENT_ID": lines[1],
        "USERNAME": lines[2],
        "PASSWORD": lines[3],
        "QR_CODE_KEY": lines[4]
    }
