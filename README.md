Certainly! Here's the updated **README** including the correct **folder structure** for your project:

---

# Xbox 360 Automated Game Catalog System for Aurora

## **Project Overview**

This system automates the process of managing Xbox 360 games, including downloading, extracting, renaming, and uploading games directly to your Xbox 360 using **Aurora** as the interface. It ensures the Xbox 360 catalog stays updated, supports **Wake-on-LAN** (WOL) for remote operations, and allows filtering based on game regions (UK, Europe, Worldwide).

## **Key Features**

* **Automated Downloading**: Games are automatically downloaded based on URLs in **`game_links.json`**.
* **Extraction**: The system automatically extracts ISO files and checks for the `default.xex` file.
* **Game Renaming**: Unwanted characters in the game folder names are automatically removed for consistency.
* **Uploading to Xbox 360**: Once extracted and renamed, the game is uploaded to the Xbox 360's HDD via FTP.
* **Post-Processing**: After the game is uploaded, downloaded files are deleted to save disk space, and the game entry is removed from **`game_links.json`**.
* **Wake-on-LAN (WOL)**: If the PC is off, the system automatically wakes up the PC to process the selected game and shuts it down again once completed.
* **Region Filtering**: Only UK, Europe, and Worldwide versions of games are included in the list for Aurora.

## **Folder Structure**

Here is the correct **folder structure** for the project:

```
C:.
│   readme.txt               # Project documentation (README)
│
├───config                   # Configuration files for settings
│   ├───config.ini           # Contains FTP settings, game metadata, and paths
│   └───game_links.json      # List of game URLs and metadata (filtered for UK, EU, Worldwide)
│
├───extractors               # ISO extraction tools
│   ├───extract-xiso.exe     # Command-line tool for ISO extraction
│   ├───extract-xiso-gui.exe # GUI tool for ISO extraction
│   └───extract-xiso-gui.exe.config  # Configuration for GUI extractor
│
├───logs                     # Logs to track system operations
│
├───scripts                  # Automation scripts
│   ├───scraper.py           # Scrapes and updates the game links
│   └───worker.py            # Handles download, extraction, renaming, and upload
│
├───staging                  # Temporary folder for game downloads and testing
│   └───_FTPTest             # Test folder with sample data for verifying the process
│
├───temp                     # Temporary folder for handling downloaded and extracted files
│   ├───downloads            # Holds downloaded game ISO files
│   ├───extracted           # Holds extracted game files
│   └───uploads              # Holds renamed and ready-to-upload game folders
```

### **Folder Descriptions:**

1. **`config`**: Contains configuration files for the FTP server and game metadata.

   * **`config.ini`**: Contains the FTP settings (Xbox IP, credentials) and other configuration parameters for the game catalog.
   * **`game_links.json`**: Stores the metadata of the games available for download, including URLs, titles, and regions.

2. **`extractors`**: Contains the tools used for extracting game ISO files.

   * **`extract-xiso.exe`**: Command-line tool for extracting ISO files.
   * **`extract-xiso-gui.exe`**: GUI tool for extracting ISO files.
   * **`extract-xiso-gui.exe.config`**: Configuration file for the GUI extractor.

3. **`scripts`**: Contains the automation scripts.

   * **`scraper.py`**: Script that scrapes game URLs and updates **`game_links.json`**.
   * **`worker.py`**: Main automation script that handles the process of downloading, extracting, renaming, and uploading the game to the Xbox 360.

4. **`staging`**: Temporary folder used for downloading and testing the process.

   * **`_FTPTest`**: A folder that contains sample test data (a game with the correct structure and files) to validate the process.

5. **`temp`**: Temporary folder for processing downloaded and extracted game files.

   * **`downloads/`**: Holds the downloaded ISO files before they are extracted.
   * **`extracted/`**: Stores the extracted game files before they are renamed and uploaded to the Xbox.
   * **`uploads/`**: Holds the renamed and prepared game folders, ready to be uploaded to the Xbox.

6. **`logs`**: Stores logs for tracking the progress and status of game downloads, extractions, uploads, and errors.

---

### **Process Flow**

1. **Catalog Selection in Aurora**:

   * Aurora displays the games from **`game_links.json`**. Only games from **UK**, **Europe**, and **Worldwide** are shown, based on filtering.

2. **Game Download**:

   * After selecting a game, the **PC** retrieves the download URL from **`game_links.json`** and downloads the game to the **`temp/downloads/`** folder.

3. **Game Extraction & Validation**:

   * The downloaded ISO file is extracted using the **`extract-xiso.exe`** or **`extract-xiso-gui.exe`** tool in the **`temp/extracted/`** folder.
   * The script checks if a `default.xex` file is present. If so, it renames the extracted folder to ensure consistency (removes unwanted characters).

4. **Upload to Xbox 360**:

   * The renamed game folder is uploaded to the Xbox 360 via FTP, using the settings from **`config.ini`**.

5. **Post-Processing**:

   * After uploading, the game files are deleted from the **`temp`** and **`staging`** folders.
   * The game entry is removed from **`game_links.json`** to prevent re-downloading.

6. **Wake-on-LAN (WOL)**:

   * If the **PC** is powered off, the **WOL** feature automatically wakes it up when a game is selected in Aurora.
   * After the process is complete, the **PC** shuts down automatically.

---

### **Setup Instructions**

1. **Folder Setup**:

   * Ensure the directory structure is created as shown above.
   * **`config.ini`** should be populated with your Xbox 360’s FTP details (IP address, username, password, and game destination folder).
   * **`game_links.json`** should contain the list of games you want to download, along with their download URLs.

2. **Running the Scripts**:

   * **`scraper.py`**: Scrapes new game links and updates **`game_links.json`**.
   * **`worker.py`**: Handles downloading, extracting, renaming, and uploading the games to the Xbox.

---

### **Log Files**

* **`download_log.txt`**: Logs the download process, including timestamps and URLs.
* **`upload_log.txt`**: Logs the status of the upload process (success or failure).
* **`error_log.txt`**: Captures any errors encountered during the process (e.g., missing files, FTP connection errors).

---

### **Maintenance and Updates**

* **Update `game_links.json`**: Regularly update this file using **`scraper.py`** to ensure the game catalog stays fresh.
* **Monitor Logs**: Check the **`logs`** folder periodically for any errors or issues.

---

### **Conclusion**

This system automates the management of Xbox 360 games by handling the download, extraction, renaming, and upload process to the Xbox 360's HDD, all while ensuring the **Aurora** catalog remains up-to-date. With **Wake-on-LAN** support, minimal manual intervention is required, and the system is designed to run smoothly in the background.

---

Let me know if you need any further adjustments or clarifications!

