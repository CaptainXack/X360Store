import configparser
import json
import os
import shutil
import zipfile
from ftplib import FTP
from pathlib import Path

import requests

CONFIG_PATH = os.path.join("config", "config.ini")


def load_config():
    config = configparser.ConfigParser()
    config.read(CONFIG_PATH)
    ftp_ip = config.get("XBOX", "ip", fallback="192.168.1.247")
    ftp_port = config.getint("XBOX", "ftp_port", fallback=21)
    ftp_user = config.get("XBOX", "user", fallback="xbox")
    ftp_pass = config.get("XBOX", "pass", fallback="xbox")
    ftp_dir = config.get("XBOX", "dest_root", fallback="Hdd1/Games")
    staging_dir = config.get("PC", "staging", fallback="temp")
    temp_dir = config.get("PC", "temp", fallback="temp")
    game_links_path = config.get(
        "PC",
        "game_links",
        fallback=os.path.join("config", "game_links.json"),
    )
    notify_endpoint = config.get("XBOX", "notify_endpoint", fallback="").strip()
    return {
        "ftp_ip": ftp_ip,
        "ftp_port": ftp_port,
        "ftp_user": ftp_user,
        "ftp_pass": ftp_pass,
        "ftp_dir": ftp_dir,
        "staging_dir": staging_dir,
        "temp_dir": temp_dir,
        "game_links_path": game_links_path,
        "notify_endpoint": notify_endpoint,
    }

def download_game(game_url, download_dir):
    # Download game ISO (You can add more download logic here)
    response = requests.get(game_url, stream=True)
    file_name = os.path.join(download_dir, game_url.split("/")[-1])
    
    with open(file_name, "wb") as f:
        for chunk in response.iter_content(chunk_size=1024):
            if chunk:
                f.write(chunk)
    return file_name

def extract_game(file_path, extract_dir):
    # Assuming the file is a ZIP containing the ISO
    with zipfile.ZipFile(file_path, "r") as zip_ref:
        zip_ref.extractall(extract_dir)

def ensure_remote_dir(ftp, remote_dir):
    parts = [p for p in remote_dir.replace("\\", "/").split("/") if p]
    current = ""
    for part in parts:
        current = f"{current}/{part}" if current else part
        try:
            ftp.cwd(current)
        except Exception:
            ftp.mkd(current)
            ftp.cwd(current)


def upload_to_xbox(local_dir, remote_dir, ftp_config):
    # FTP upload to Xbox 360
    ftp = FTP()
    ftp.connect(ftp_config["ftp_ip"], ftp_config["ftp_port"])
    ftp.login(ftp_config["ftp_user"], ftp_config["ftp_pass"])
    ensure_remote_dir(ftp, remote_dir)

    for root, dirs, files in os.walk(local_dir):
        relative_root = os.path.relpath(root, local_dir)
        ftp.cwd(remote_dir)
        if relative_root != ".":
            ensure_remote_dir(ftp, os.path.join(remote_dir, relative_root))
        for file in files:
            local_file = os.path.join(root, file)
            remote_file = os.path.join(remote_dir, relative_root, file).replace("\\", "/")
            with open(local_file, "rb") as f:
                ftp.storbinary(f"STOR {remote_file}", f)

    ftp.quit()


def notify_dashboard(message, notify_endpoint):
    if not notify_endpoint:
        print(f"[Notify] {message}")
        return
    try:
        requests.post(notify_endpoint, json={"message": message}, timeout=10)
    except requests.RequestException as exc:
        print(f"[Notify] Failed to send notification: {exc}")


def sanitize_title(title):
    sanitized = "".join(c for c in title if c.isalnum() or c in (" ", "-", "_")).strip()
    return sanitized.replace(" ", "_")


def has_default_xex(extract_dir):
    for root, _, files in os.walk(extract_dir):
        if "default.xex" in files:
            return True
    return False


def process_game(game, config, games_list):
    # Process the game based on the URL in game_links.json
    temp_dir = Path(config["temp_dir"])
    download_dir = temp_dir / "downloads"
    extract_dir = temp_dir / "extracted"
    uploads_dir = temp_dir / "uploads"
    
    # Ensure the directories exist
    download_dir.mkdir(parents=True, exist_ok=True)
    extract_dir.mkdir(parents=True, exist_ok=True)
    uploads_dir.mkdir(parents=True, exist_ok=True)

    # Download the game
    print(f"Downloading {game['title']}...")
    notify_dashboard(f"Downloading {game['title']}...", config["notify_endpoint"])
    downloaded_game = download_game(game["href"], str(download_dir))

    # Extract the downloaded ISO
    print(f"Extracting {game['title']}...")
    notify_dashboard(f"Extracting {game['title']}...", config["notify_endpoint"])
    extract_game(downloaded_game, str(extract_dir))

    # Check if `default.xex` exists and rename folder
    if not has_default_xex(str(extract_dir)):
        notify_dashboard(
            f"{game['title']} missing default.xex. Skipping.",
            config["notify_endpoint"],
        )
        shutil.rmtree(download_dir, ignore_errors=True)
        shutil.rmtree(extract_dir, ignore_errors=True)
        return False

    extracted_folder = os.path.join(extract_dir, sanitize_title(game["title"]))
    if not os.path.exists(extracted_folder):
        os.makedirs(extracted_folder, exist_ok=True)
        for entry in os.listdir(extract_dir):
            full_path = os.path.join(extract_dir, entry)
            if full_path == extracted_folder:
                continue
            shutil.move(full_path, extracted_folder)
    
    # Upload to Xbox
    print(f"Uploading {game['title']} to Xbox...")
    notify_dashboard(f"Uploading {game['title']} to Xbox...", config["notify_endpoint"])
    upload_to_xbox(extracted_folder, config["ftp_dir"], config)

    # Clean up downloaded and extracted files
    shutil.rmtree(download_dir, ignore_errors=True)
    shutil.rmtree(extract_dir, ignore_errors=True)
    shutil.rmtree(uploads_dir, ignore_errors=True)
    notify_dashboard(
        f"{game['title']} upload complete.",
        config["notify_endpoint"],
    )
    print(f"{game['title']} has been uploaded successfully!")
    games_list.remove(game)
    return True

def main():
    config = load_config()
    # Read game_links.json
    with open(config["game_links_path"], "r", encoding="utf-8") as f:
        games = json.load(f)
    
    # Process each game
    for game in list(games):
        if process_game(game, config, games):
            with open(config["game_links_path"], "w", encoding="utf-8") as f:
                json.dump(games, f, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    main()

