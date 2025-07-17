import os
import shutil
import json
import random
import string
from datetime import datetime
from organizer import organize_files

# Settings
TRIGGERWORDS_FILE = 'triggerwords.txt'
KILL_LOG_FILE = 'kill_log.json'
QUARANTINE_FOLDER = 'quarantine'
USER_ACCEPT_FILE = 'user_accepted.txt'

# Load trigger words
with open(TRIGGERWORDS_FILE, 'r') as f:
    TRIGGER_WORDS = f.read().split()

# Create folders if not exist
os.makedirs(QUARANTINE_FOLDER, exist_ok=True)

# Accept terms and conditions
if not os.path.exists(USER_ACCEPT_FILE):
    print("🚨 " + "_"*160)
    print("⚠️ WARNING — REMOVE ANY IMPORTANT FILES YOU KNOW ARE SAFE. IF NOT, OUR SYSTEM WILL DETECT ONE OR MORE OF THE FOLLOWING COMMON KEYWORDS AND NEUTRALIZE YOUR FILE:")
    print("|")
    print("|", '   '.join(TRIGGER_WORDS))
    print("🚫 " + "_"*160)
    print("⚠️ WARNING — KILLSWITCH IS NOT RESPONSIBLE FOR LOST FILES. PROCEED ONLY IF YOU ACCEPT.")
    accept = input("🖊️ Type 'I ACCEPT' to continue: ")
    if accept.strip().upper() != "I ACCEPT":
        print("❌ Access denied. Exiting.")
        exit()
    with open(USER_ACCEPT_FILE, 'w') as f:
        f.write("Accepted on: " + str(datetime.now()))

# Function to generate encrypted extension
def generate_encrypted_extension(length=8):
    chars = string.ascii_lowercase + string.digits
    return '.' + ''.join(random.choice(chars) for _ in range(length))

# Load or initialize kill log
if os.path.exists(KILL_LOG_FILE):
    with open(KILL_LOG_FILE, 'r') as f:
        kill_log = json.load(f)
else:
    username = input("👤 Enter your name for the trophy wall: ")
    kill_log = {"kills": [], "achievements": [], "username": username}

# Perform scan and quarantine
def scan_directory(path):
    print(f"\n🔍 Scanning directory: {path}")
    file_list = os.listdir(path)
    neutralized_count = 0

    for file in file_list:
        if os.path.isfile(os.path.join(path, file)):
            for word in TRIGGER_WORDS:
                if word.lower() in file.lower():
                    print(f"⚠️ Potential threat found: {file}")
                    choice = input("🛡️ Do you want to quarantine this file? (Y/N): ").strip().upper()
                    if choice == 'Y':
                        ext = generate_encrypted_extension()
                        new_name = ''.join(random.choices(string.ascii_letters + string.digits, k=10)) + ext
                        src = os.path.join(path, file)
                        dst = os.path.join(QUARANTINE_FOLDER, new_name)
                        shutil.move(src, dst)
                        print(f"✅ Quarantined as: {new_name}")

                        kill_log['kills'].append({
                            "original": file,
                            "quarantined_as": new_name,
                            "timestamp": str(datetime.now())
                        })

                        neutralized_count += 1

                        # Achievements
                        kills_len = len(kill_log['kills'])
                        if kills_len == 5 and "Slayer I: 5 files neutralized." not in kill_log['achievements']:
                            kill_log['achievements'].append("🏅 Slayer I: 5 files neutralized.")
                            print("🎉 Achievement unlocked: Slayer I")
                        if kills_len == 10 and "Obliterator X: 10+ confirmed threats." not in kill_log['achievements']:
                            kill_log['achievements'].append("🏆 Obliterator X: 10+ confirmed threats.")
                            print("🎉 Achievement unlocked: Obliterator X")

    return neutralized_count

# Save kill log
def save_log():
    with open(KILL_LOG_FILE, 'w') as f:
        json.dump(kill_log, f, indent=4)

# Launch screen
def launch_ascii():
    banner = r"""
 _  _____ _     _     ______        _____ _____ ____ _   _ 
| |/ /_ _| |   | |   / ___\ \      / /_ _|_   _/ ___| | | |
| ' / | || |   | |   \___ \\ \ /\ / / | |  | || |   | |_| |
| . \ | || |___| |___ ___) |\ V  V /  | |  | || |___|  _  |
|_|\_\___|_____|_____|____/  \_/\_/  |___| |_| \____|_| |_|

               KILLSWITCH v1.5: Totality of Obliteration
"""
    print(banner)

# Main execution
if __name__ == "__main__":
    launch_ascii()
    organize_files('.')  # Auto organize before scan
    neutralized = scan_directory('.')
    save_log()
    print(f"\n🛡️ Scan complete. {neutralized} suspicious file(s) neutralized.")
    print(f"🏆 Achievements: {', '.join(kill_log['achievements']) if kill_log['achievements'] else 'None yet'}")
    print(f"📁 Neutralized files are in the folder: {os.path.abspath(QUARANTINE_FOLDER)}")
