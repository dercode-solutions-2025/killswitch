import os
import json
import getpass
import shutil
import string
import random
from datetime import datetime

# === ASCII Banner ===
banner = r"""
 _  _____ _     _     ______        _____ _____ ____ _   _ 
| |/ /_ _| |   | |   / ___\ \      / /_ _|_   _/ ___| | | |
| ' / | || |   | |   \___ \\ \ /\ / / | |  | || |   | |_| |
| . \ | || |___| |___ ___) |\ V  V /  | |  | || |___|  _  |
|_|\_\___|_____|_____|____/  \_/\_/  |___| |_| \____|_| |_|
              v1.5 - Totality of Obliteration
"""

print(banner)

# === Settings ===
keywords = ["trojan", "malware", "virus", "keylogger", "worm", "spyware", "malware", "adware", "ware", "ransomware"]
quarantine_folder = "quarantine"
log_file = "killswitch_data.json"
neutralized_extension = ".~|!@#$%^&*()_+=-{}[]<>.,/,"

# === Load or initialize log file ===
if not os.path.exists(log_file):
    data = {
        "runs": 0,
        "kills": 0,
        "quarantined": [],
        "user": getpass.getuser()
    }
else:
    with open(log_file, "r") as f:
        data = json.load(f)

data["runs"] += 1

print(f"\nWelcome back, {data['user']}! This is run #{data['runs']}.")
print(f"Total threats neutralized: {data['kills']}\n")

# === Ensure quarantine folder exists ===
if not os.path.exists(quarantine_folder):
    os.makedirs(quarantine_folder)

# === Ask for scan path ===
scan_path = input("Enter the full path of the folder to scan: (e.g., C:\Users\You\Download) ").strip()

if not os.path.exists(scan_path):
    print("Invalid path. Exiting.")
    exit()

# === Scan files ===
suspicious_files = []

for root, _, files in os.walk(scan_path):
    for file in files:
        name_only = os.path.splitext(file)[0].lower()
        if any(keyword in name_only for keyword in keywords):
            full_path = os.path.join(root, file)
            suspicious_files.append(full_path)

if not suspicious_files:
    print("✅ No suspicious files found.")
else:
    print(f"\n⚠️ Found {len(suspicious_files)} suspicious file(s):")
    for i, path in enumerate(suspicious_files, 1):
        print(f"  {i}. {path}")

    action = input("\nDo you want to NEUTRALIZE and QUARANTINE these files? (yes/no): ").strip().lower()
    if action == "yes":
        for file_path in suspicious_files:
            try:
                filename = os.path.basename(file_path)
                new_name = ''.join(random.choices(string.ascii_letters + string.digits, k=32)) + neutralized_extension
                new_path = os.path.join(quarantine_folder, new_name)

                shutil.move(file_path, new_path)
                data["quarantined"].append({
                    "original_name": filename,
                    "quarantined_name": new_name,
                    "time": datetime.now().isoformat()
                })
                data["kills"] += 1
                print(f"☣️ Neutralized: {filename} ➜ {new_name}")
            except Exception as e:
                print(f"❌ Error neutralizing {file_path}: {e}")

# === Save data ===
with open(log_file, "w") as f:
    json.dump(data, f, indent=2)

# === Exit message ===
print("\n💀 KILLSWITCH v1.5: Totality of Obliteration complete.")
print(f"💾 {data['kills']} total file(s) neutralized across all runs.\n")
