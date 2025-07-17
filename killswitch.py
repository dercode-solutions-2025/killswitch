# KILLSWITCH v1.5 - Totality of Obliteration
import os
import json
import shutil
import random
import string
import getpass
from pathlib import Path
from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes

# Constants
CONFIG_FILE = "killswitch_data.json"
QUARANTINE_FOLDER = "quarantine"
AES_KEY = get_random_bytes(32)  # AES-256
BLOCK_SIZE = AES.block_size

SUSPICIOUS_KEYWORDS = [
    "trojan", "malware", "virus", "worm", "spyware", "ransomware",
    "backdoor", "keylogger", "botnet", "adware", "rootkit",
    "danger", "hacktool", "stealer", "dropper", "suspicious"
]

ULTRA_ENCRYPTED_NAME = "~|!@#$%^&*()_+=-{}[]<>.,/"

# Load or initialize config
def load_config():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r") as f:
            return json.load(f)
    else:
        return {
            "username": "",
            "kills": 0,
            "trophies": []
        }

# Save config
def save_config(config):
    with open(CONFIG_FILE, "w") as f:
        json.dump(config, f, indent=4)

# Padding for AES
def pad(s):
    pad_len = BLOCK_SIZE - len(s) % BLOCK_SIZE
    return s + bytes([pad_len] * pad_len)

def encrypt_file(input_path, output_path):
    cipher = AES.new(AES_KEY, AES.MODE_CBC)
    with open(input_path, "rb") as f:
        data = pad(f.read())
    with open(output_path, "wb") as f:
        f.write(cipher.iv)
        f.write(cipher.encrypt(data))

# Banner
def print_banner():
    print("""
▀████▀ ▀███▀▀████▀████▀   ▀████▀    ▄█▀▀▀█▄█████▀     █     ▀███▀████▀██▀▀██▀▀███ ▄▄█▀▀▀█▄█████▀  ▀████▀▀
  ██   ▄█▀    ██   ██       ██     ▄██    ▀█ ▀██     ▄██     ▄█   ██ █▀   ██   ▀███▀     ▀█ ██      ██   
  ██ ▄█▀      ██   ██       ██     ▀███▄      ██▄   ▄███▄   ▄█    ██      ██    ██▀       ▀ ██      ██   
  █████▄      ██   ██       ██       ▀█████▄   ██▄  █▀ ██▄  █▀    ██      ██    ██          ██████████   
  ██  ███     ██   ██     ▄ ██     ▄     ▀██   ▀██ █▀  ▀██ █▀     ██      ██    ██▄         ██      ██   
  ██   ▀██▄   ██   ██    ▄█ ██    ▄██     ██    ▄██▄    ▄██▄      ██      ██    ▀██▄     ▄▀ ██      ██   
▄████▄   ███▄████▄██████████████████▀█████▀      ██      ██     ▄████▄  ▄████▄    ▀▀█████▀▄████▄  ▄████▄▄
    """)

# Ask for name if needed
def get_username(config):
    if not config["username"]:
        config["username"] = input("Welcome! What's your name? ")
        save_config(config)
    return config["username"]

# Scan and handle files
def scan_directory(root_dir, config):
    suspicious_files = []
    for root, dirs, files in os.walk(root_dir):
        for file in files:
            file_path = os.path.join(root, file)
            filename_lower = file.lower()
            for keyword in SUSPICIOUS_KEYWORDS:
                if keyword in filename_lower:
                    suspicious_files.append(file_path)
                    break

    if not suspicious_files:
        print("No threats found.")
        return

    print(f"\nFound {len(suspicious_files)} suspicious file(s):")
    os.makedirs(QUARANTINE_FOLDER, exist_ok=True)

    for fpath in suspicious_files:
        print(f"\nThreat detected: {fpath}")
        choice = input("(D)elete, (Q)uarantine, or (I)gnore? ").strip().lower()

        if choice == 'd':
            try:
                os.remove(fpath)
                config["kills"] += 1
                print("File deleted.")
            except:
                print("Failed to delete file.")
        elif choice == 'q':
            try:
                new_name = ULTRA_ENCRYPTED_NAME
                enc_path = os.path.join(QUARANTINE_FOLDER, new_name)
                encrypt_file(fpath, enc_path)
                os.remove(fpath)
                config["kills"] += 1
                print("File quarantined and encrypted.")
            except Exception as e:
                print("Quarantine failed:", e)
        else:
            print("Ignored.")

    # Trophy examples
    if config["kills"] >= 5 and "5 Kills" not in config["trophies"]:
        config["trophies"].append("5 Kills")
        print("🏆 Achievement Unlocked: 5 Kills!")
    if config["kills"] >= 10 and "10 Kills" not in config["trophies"]:
        config["trophies"].append("10 Kills")
        print("🏆 Achievement Unlocked: 10 Kills!")

    save_config(config)

# Main function
def main():
    print_banner()
    config = load_config()
    username = get_username(config)
    print(f"Welcome back, {username}!")
    print(f"Total threats neutralized: {config['kills']}")
    if config['trophies']:
        print("Trophies:", ", ".join(config['trophies']))

    scan_path = input("\nEnter the full path of the directory to scan: ").strip()
    if not os.path.isdir(scan_path):
        print("Invalid directory.")
        return

    scan_directory(scan_path, config)
    print("\nKILLSWITCH scan complete.")

if __name__ == "__main__":
    main()
