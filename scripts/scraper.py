import requests
from bs4 import BeautifulSoup
import json
from urllib.parse import urljoin
import time  # For time intervals

# Hardcoded URL and output filename
GAME_URL = "https://myrient.erista.me/files/Redump/Microsoft%20-%20Xbox%20360/"  # Replace with your scraping source
JSON_FILENAME = "C:\\X360Store\\config\\game_links.json"  # Absolute path to game_links.json

def update_game_links():
    try:
        # Load the existing game_links.json file if it exists
        with open(JSON_FILENAME, "r", encoding='utf-8') as f:
            game_links = json.load(f)

    except (FileNotFoundError, json.JSONDecodeError):
        # If the file does not exist or is empty, initialize an empty list
        game_links = []

    # Scrape new game data
    new_game_data = scrape_game_data(GAME_URL)

    # Add new games to the list, checking if they already exist
    for game in new_game_data:
        if game not in game_links:
            game_links.append(game)

    # Write updated game links back to the same game_links.json file
    try:
        # Ensure the directory exists before writing the file
        os.makedirs(os.path.dirname(JSON_FILENAME), exist_ok=True)
        
        with open(JSON_FILENAME, "w", encoding='utf-8') as f:
            json.dump(game_links, f, ensure_ascii=False, indent=4)
        print(f"Updated game links in '{JSON_FILENAME}'. Total games: {len(game_links)}")

    except Exception as e:
        print(f"Error writing to file: {e}")

def scrape_game_data(url):
    # Send GET request to the URL
    response = requests.get(url)
    
    # Check if the response is valid (status code 200)
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, "html.parser")
        
        # Find all <td> tags with the class "link"
        game_data = []
        for link in soup.find_all("a", href=True):
            game_url = link["href"]
            if "xbox" in game_url:  # Filter for Xbox-related links
                game_info = {
                    "title": link.text.strip(),
                    "region": "Unknown",  # You can update this if regions are part of the data
                    "href": game_url
                }
                game_data.append(game_info)

        return game_data
    else:
        print(f"Error: Unable to retrieve data. Status code: {response.status_code}")
        return []

if __name__ == "__main__":
    while True:  # Infinite loop to keep running the scraper
        update_game_links()
        time.sleep(86400)  # Wait for 24 hours (86400 seconds) before running again

