import configparser
import json
import os
import time  # For time intervals
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup

CONFIG_PATH = os.path.join("config", "config.ini")


def load_config():
    config = configparser.ConfigParser()
    config.read(CONFIG_PATH)
    source_url = config.get(
        "SCRAPER",
        "source_url",
        fallback="https://myrient.erista.me/files/Redump/Microsoft%20-%20Xbox%20360/",
    )
    game_links_path = config.get(
        "PC",
        "game_links",
        fallback=os.path.join("config", "game_links.json"),
    )
    update_interval_hours = config.getint("SCRAPER", "update_interval_hours", fallback=24)
    allowed_regions_raw = config.get(
        "SCRAPER",
        "allowed_regions",
        fallback="UK,Europe,Worldwide,World",
    )
    include_other_regions = config.getboolean(
        "SCRAPER",
        "include_other_regions",
        fallback=False,
    )
    allowed_regions = {
        region.strip().lower()
        for region in allowed_regions_raw.split(",")
        if region.strip()
    }
    return (
        source_url,
        game_links_path,
        update_interval_hours,
        allowed_regions,
        include_other_regions,
    )

def update_game_links(
    game_url,
    json_filename,
    allowed_regions,
    include_other_regions,
):
    try:
        # Load the existing game_links.json file if it exists
        with open(json_filename, "r", encoding="utf-8") as f:
            game_links = json.load(f)

    except (FileNotFoundError, json.JSONDecodeError):
        # If the file does not exist or is empty, initialize an empty list
        game_links = []

    # Scrape new game data
    new_game_data = scrape_game_data(game_url, allowed_regions, include_other_regions)

    # Add new games to the list, checking if they already exist
    for game in new_game_data:
        if game not in game_links:
            game_links.append(game)

    # Write updated game links back to the same game_links.json file
    try:
        # Ensure the directory exists before writing the file
        os.makedirs(os.path.dirname(json_filename), exist_ok=True)

        with open(json_filename, "w", encoding="utf-8") as f:
            json.dump(game_links, f, ensure_ascii=False, indent=4)
        print(f"Updated game links in '{json_filename}'. Total games: {len(game_links)}")

    except Exception as e:
        print(f"Error writing to file: {e}")


def matches_region(title, allowed_regions, include_other_regions):
    if include_other_regions:
        return True
    lowered = title.lower()
    return any(f"({region})" in lowered for region in allowed_regions) or any(
        f", {region}" in lowered for region in allowed_regions
    )


def scrape_game_data(url, allowed_regions, include_other_regions):
    # Send GET request to the URL
    response = requests.get(url)
    
    # Check if the response is valid (status code 200)
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, "html.parser")
        
        # Find all <td> tags with the class "link"
        game_data = []
        for link in soup.find_all("a", href=True):
            game_url = urljoin(url, link["href"])
            title = link.text.strip()
            if not title or title in {".", ".."}:
                continue
            if not matches_region(title, allowed_regions, include_other_regions):
                continue
            game_info = {
                "title": title,
                "region": "Unknown",
                "href": game_url,
            }
            game_data.append(game_info)

        return game_data
    else:
        print(f"Error: Unable to retrieve data. Status code: {response.status_code}")
        return []

if __name__ == "__main__":
    (
        game_url,
        json_filename,
        update_interval_hours,
        allowed_regions,
        include_other_regions,
    ) = load_config()
    while True:  # Infinite loop to keep running the scraper
        update_game_links(
            game_url,
            json_filename,
            allowed_regions,
            include_other_regions,
        )
        time.sleep(update_interval_hours * 3600)

