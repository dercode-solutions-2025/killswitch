import os
import json
import shutil
from pathlib import Path
from tkinter import Tk, Label, Button, filedialog, messagebox
from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes

# ---------------- CONFIG ----------------
CONFIG_FILE = "killswitch_data.json"
QUARANTINE_FOLDER = "quarantine"
AES_KEY = get_random_bytes(32)  # AES-256
BLOCK_SIZE = AES.block_size
ULTRA_ENCRYPTED_NAME = "~|!@#$%^&*()_+=-{}[]<>.,/"
SUSPICIOUS_KEYWORDS = [
    "trojan", "malware", "virus", "worm", "spyware", "ransomware",
    "backdoor", "keylogger", "botnet", "adware", "rootkit",
    "danger", "hacktool", "stealer", "dropper", "suspicious"
]

# ---------------- HELPER FUNCTIONS ----------------
def load_config():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r") as f:
            return json.load(f)
    return {"username": "", "kills": 0, "trophies": []}

def save_config(config):
    with open(CONFIG_FILE, "w") as f:
        json.dump(config, f, indent=4)

def pad(data):
    pad_len = BLOCK_SIZE - len(data) % BLOCK_SIZE
    return data + bytes([pad_len] * pad_len)

def encrypt_file(input_path, output_path):
    cipher = AES.new(AES_KEY, AES.MODE_CBC)
    with open(input_path, "rb") as f:
        data = pad(f.read())
    with open(output_path, "wb") as f:
        f.write(cipher.iv)
        f.write(cipher.encrypt(data))

# ---------------- GUI CLASS ----------------
class KILLSWITCHGUI:
    def __init__(self, master):
        self.master = master
        master.title("KILLSWITCH 2.0 Watchdog")
        master.geometry("500x350")

        self.config = load_config()
        if not self.config["username"]:
            self.config["username"] = filedialog.askstring("Welcome", "Enter your name:")
            save_config(self.config)

        Label(master, text=f"KILLSWITCH 2.0 - Welcome {self.config['username']}", font=("Courier", 16)).pack(pady=10)
        Button(master, text="Scan Directory", command=self.scan_directory_gui).pack(pady=5)
        Button(master, text="View Quarantine", command=self.view_quarantine).pack(pady=5)
        Button(master, text="Exit", command=master.quit).pack(pady=10)

    def scan_directory_gui(self):
        folder = filedialog.askdirectory()
        if not folder:
            return
        threats = []
        for root, dirs, files in os.walk(folder):
            for file in files:
                if any(k in file.lower() for k in SUSPICIOUS_KEYWORDS):
                    threats.append(os.path.join(root, file))

        if not threats:
            messagebox.showinfo("Scan Result", "No threats detected.")
            return

        os.makedirs(QUARANTINE_FOLDER, exist_ok=True)
        for fpath in threats:
            choice = messagebox.askquestion("Threat Detected", f"File: {fpath}\nQuarantine it?")
            if choice == 'yes':
                try:
                    enc_path = os.path.join(QUARANTINE_FOLDER, ULTRA_ENCRYPTED_NAME)
                    encrypt_file(fpath, enc_path)
                    os.remove(fpath)
                    self.config["kills"] += 1
                except Exception as e:
                    messagebox.showerror("Error", f"Failed to quarantine: {fpath}\n{e}")
        save_config(self.config)
        messagebox.showinfo("Scan Complete", f"Scan finished. Total kills: {self.config['kills']}")

    def view_quarantine(self):
        if not os.path.exists(QUARANTINE_FOLDER):
            messagebox.showinfo("Quarantine", "No files quarantined yet.")
            return
        files = os.listdir(QUARANTINE_FOLDER)
        if not files:
            messagebox.showinfo("Quarantine", "No files quarantined yet.")
            return
        messagebox.showinfo("Quarantine", "\n".join(files))

# ---------------- MAIN ----------------
def main():
    root = Tk()
    app = KILLSWITCHGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()
