import json
import os
import shutil
import requests
from ftplib import FTP
import zipfile

# FTP settings from config.ini
FTP_IP = "192.168.1.247"  # Replace with your Xbox IP
FTP_USER = "xbox"         # Replace with your FTP username
FTP_PASS = "xbox"     # Replace with your FTP password
FTP_DIR = "/Hdd1/Games"   # Destination folder on Xbox

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

def upload_to_xbox(local_dir, remote_dir):
    # FTP upload to Xbox 360
    ftp = FTP(FTP_IP)
    ftp.login(FTP_USER, FTP_PASS)
    ftp.cwd(remote_dir)

    for root, dirs, files in os.walk(local_dir):
        for file in files:
            local_file = os.path.join(root, file)
            remote_file = os.path.join(remote_dir, file)
            with open(local_file, "rb") as f:
                ftp.storbinary(f"STOR {remote_file}", f)

    ftp.quit()

def process_game(game):
    # Process the game based on the URL in game_links.json
    download_dir = "temp/downloads"
    extract_dir = "temp/extracted"
    uploads_dir = "temp/uploads"
    
    # Ensure the directories exist
    os.makedirs(download_dir, exist_ok=True)
    os.makedirs(extract_dir, exist_ok=True)
    os.makedirs(uploads_dir, exist_ok=True)

    # Download the game
    print(f"Downloading {game['title']}...")
    downloaded_game = download_game(game['href'], download_dir)

    # Extract the downloaded ISO
    print(f"Extracting {game['title']}...")
    extract_game(downloaded_game, extract_dir)

    # Check if `default.xex` exists and rename folder
    extracted_folder = os.path.join(extract_dir, game['title'])
    if os.path.exists(os.path.join(extracted_folder, "default.xex")):
        # Rename the folder (remove unwanted characters if necessary)
        new_folder_name = game['title'].replace(" ", "_")  # Example renaming rule
        os.rename(extracted_folder, os.path.join(extract_dir, new_folder_name))
        extracted_folder = os.path.join(extract_dir, new_folder_name)
    
    # Upload to Xbox
    print(f"Uploading {game['title']} to Xbox...")
    upload_to_xbox(extracted_folder, FTP_DIR)

    # Clean up downloaded and extracted files
    shutil.rmtree(download_dir)
    shutil.rmtree(extract_dir)
    print(f"{game['title']} has been uploaded successfully!")

def main():
    # Read game_links.json
    with open("config/game_links.json", "r") as f:
        games = json.load(f)
    
    # Process each game
    for game in games:
        process_game(game)

if __name__ == "__main__":
    main()

