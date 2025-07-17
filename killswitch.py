# KillSwitch v1.1, "Only God can stop us."
# Terminal-based antivirus tool with pattern detection, quarantine, achievements, and user logging

import os
import json
import time
import re
import sys

# --------------------------- CONFIGURATION ---------------------------
SUSPICIOUS_KEYWORDS = ["trojan", "virus", "malware", "spyware", "worm", "keylogger", "backdoor", "adware", "shareware"]
SUSPICIOUS_PATTERNS = [
    r"troj[a@]n", r"vir[u0]s", r"spy[-_]?ware", r"key[-_]?logger",
    r"mal[-_]?ware", r"back[-_]?door", r"ad[-_]?ware", r"shell.*\\.bat",
    r"(install|setup).*\\.exe", r"(hack|crack).*"
]
# Dangerous extensions check is now ignored for quarantine, but left for info.
DANGEROUS_EXTENSIONS = [".exe", ".bat", ".dll", ".scr", ".vbs", ".cmd"]
PROTECTED_PATHS = ["C:\\Windows", "C:\\Program Files", "/usr", "/etc"]
QUARANTINE_DIR = "Quarantine"
DATA_FILE = "aether_data.json"
THREAT_LOG_FILE = "threat_log.json"

ACHIEVEMENTS = {
    "Identity Crisis Solved": lambda d: d["name"] != "",
    "Cleanup Crew": lambda d: len(d["deletions"]) >= 5,
    "Digital Exorcist": lambda d: "trojan.exe" in d["deletions"],
    "Bug Hunter": lambda d: d.get("runs", 0) >= 10,
    "Firewall of Justice": lambda d: d.get("quarantined", 0) >= 3,
}

# --------------------------- UTILITIES ---------------------------
def load_user_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r') as f:
            return json.load(f)
    return {"name": "", "deletions": [], "auto_delete": False, "achievements": [], "runs": 0, "quarantined": 0}

def save_user_data(data):
    with open(DATA_FILE, 'w') as f:
        json.dump(data, f, indent=4)

def log_threat(filename, reason, action):
    entry = {"timestamp": time.ctime(), "file": filename, "reason": reason, "action": action}
    if not os.path.exists(THREAT_LOG_FILE):
        with open(THREAT_LOG_FILE, 'w') as f:
            json.dump([entry], f, indent=4)
    else:
        with open(THREAT_LOG_FILE, 'r+') as f:
            data = json.load(f)
            data.append(entry)
            f.seek(0)
            json.dump(data, f, indent=4)

def quarantine_file(path):
    if not os.path.exists(QUARANTINE_DIR):
        os.makedirs(QUARANTINE_DIR)
    filename = os.path.basename(path)
    timestamp = time.strftime("%Y%m%d_%H%M%S")
    new_path = os.path.join(QUARANTINE_DIR, f"{timestamp}_{filename}")
    try:
        os.rename(path, new_path)
        print(f"🔒 Quarantined: {filename}")
    except Exception as e:
        print(f"[!] Failed to quarantine file {filename}: {e}")
        new_path = None
    return new_path

def is_protected_path(path):
    for protected in PROTECTED_PATHS:
        if path.lower().startswith(protected.lower()):
            return True
    return False

# --------------------------- FILE SCANNING ---------------------------
def matches_suspicious_pattern(filename):
    for pattern in SUSPICIOUS_PATTERNS:
        if re.search(pattern, filename.lower()):
            return True
    return False

def has_dangerous_extension(filename):
    # This function is now informational only and does NOT trigger quarantine.
    return os.path.splitext(filename)[1].lower() in DANGEROUS_EXTENSIONS

def check_file_size(filepath):
    try:
        size = os.path.getsize(filepath)
        if size == 0:
            return "File is empty (possible malware stub)"
        elif size > 500 * 1024 * 1024:
            return "Suspiciously large file"
    except:
        return None
    return None

def scan_file(filepath):
    name = os.path.basename(filepath)
    # ONLY filename based detection (ignore extension quarantining)
    if matches_suspicious_pattern(name):
        return f"Filename matches suspicious pattern"
    # Commenting out extension quarantining:
    # if has_dangerous_extension(name):
    #     return f"Dangerous file extension"
    size_reason = check_file_size(filepath)
    if size_reason:
        return size_reason
    try:
        with open(filepath, 'r', errors='ignore') as f:
            content = f.read().lower()
            for keyword in SUSPICIOUS_KEYWORDS:
                if keyword in content:
                    return f"File content contains '{keyword}'"
    except:
        pass
    return None

def scan_folder(folder, data):
    print(f"\n[+] Scanning: {folder}")
    for root, dirs, files in os.walk(folder):
        for file in files:
            path = os.path.join(root, file)
            print(f"Scanning file: {path}")  # DEBUG
            if is_protected_path(path):
                print(f"[-] Skipping protected system path: {path}")
                continue
            reason = scan_file(path)
            print(f"Reason found: {reason}")  # DEBUG
            if reason:
                print(f"[!] Suspicious file: {path} — {reason}")
                try:
                    new_path = quarantine_file(path)
                    if new_path:
                        data["quarantined"] += 1
                        log_threat(file, reason, "quarantined")
                except Exception as e:
                    print(f"[!] Failed to quarantine file {path}: {e}")

# --------------------------- USER & TROPHIES ---------------------------
def greet_user(data):
    if not data["name"]:
        try:
            name = input("Welcome to AetherCleaner! What is your name? ").strip()
        except (EOFError, OSError):
            name = "Guest"
        data["name"] = name
    print(f"Welcome back, {data['name']}!")
    if data["deletions"]:
        print("\n🧹 Files you've removed:")
        for f in data["deletions"]:
            print(f" - {f}")
    if data["achievements"]:
        print("\n🏆 Achievements:")
        for a in data["achievements"]:
            print(f" • {a}")

def ask_auto_delete(data):
    # Auto delete is forced True, no input needed
    data["auto_delete"] = True

def check_achievements(data):
    unlocked = []
    for name, check in ACHIEVEMENTS.items():
        if check(data) and name not in data["achievements"]:
            data["achievements"].append(name)
            unlocked.append(name)
    return unlocked

def display_new_achievements(achs):
    if achs:
        print("\n🎉 New Achievements Unlocked:")
        for a in achs:
            print(f" 🏅 {a}")

# --------------------------- MAIN ---------------------------
def main():
    data = load_user_data()
    data["runs"] += 1
    greet_user(data)
    ask_auto_delete(data)  # forced True

    try:
        start = input("\nStart scan? (y/n): ").strip().lower()
    except (EOFError, OSError):
        start = 'n'

    if start == 'y':
        try:
            path = input("Enter folder to scan: ").strip()
        except (EOFError, OSError):
            print("Unable to get folder path input.")
            path = ""
        if os.path.isdir(path):
            scan_folder(path, data)
        else:
            print("Invalid folder path.")

    new_achs = check_achievements(data)
    display_new_achievements(new_achs)
    save_user_data(data)

if __name__ == "__main__":
    main()
