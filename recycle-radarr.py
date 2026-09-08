#!/usr/bin/env python3
import requests
import json
from datetime import datetime, timedelta
import argparse
import logging

"""
Radarr Movie Cleanup Script
Version : 1.0 (08-09-2026)
Description: Delete movie after X days(except for the whitelist).
"""

# Configuratin
RADARR_URL = "http://localhost:7878"
RADARR_API_KEY = ""
WHITELIST_FILE = "movie_whitelist.txt"
DAYS_THRESHOLD = 365
DRY_RUN = False

# Loggin configuration
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

def load_whitelist(file_path):
    """Load whitelist_move from a file, one word per line"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return [line.strip() for line in f if line.strip()]
    except FileNotFoundError:
        logger.error(f"Can't find the whitelist file : {file_path}")
        return []
    except Exception as e:
        logger.error(f"Can't read the whitelist file : {e}")
        return []

def get_radarr_movies():
    url = f"{RADARR_URL}/api/v3/movie"
    headers = {
        "X-Api-Key": RADARR_API_KEY,
        "Content-Type": "application/json"
    }

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        logger.error(f"Errorr API Radarr : {e}")
        return []

def is_movie_whitelisted(movie_title, whitelist):
    title_upper = movie_title.upper()
    for keyword in whitelist:
        if keyword.upper() in title_upper:
            return True
    return False

def should_delete_movie(movie, days_threshold, whitelist):
    added_date = datetime.strptime(movie["added"], "%Y-%m-%dT%H:%M:%SZ")
    days_since_added = (datetime.now() - added_date).days

    if days_since_added <= days_threshold:
        return False

    if is_movie_whitelisted(movie["title"], whitelist):
        logger.info(f"✅ Whitelist : {movie['title']}")
        return False

    return True

def delete_movie_from_radarr(movie_id):
    url = f"{RADARR_URL}/api/v3/movie/{movie_id}?deleteFiles=true&addImportExclusion=false"
    headers = {
        "X-Api-Key": RADARR_API_KEY,
        "accept": '*/*'
    }
    try:
        if DRY_RUN:
            logger.info(f"[DRY RUN] Delete (ID: {movie_id}) : ")
            return True

        response = requests.delete(url, headers=headers)
        response.raise_for_status()
        logger.info(f"🗑 Deleted : {movie_id}")
        return True
    except requests.exceptions.RequestException as e:
        logger.error(f"❌ Failed to delete (ID: {movie_id}) : {e}")
        return False

def main():
    logger.info("=== Delete old movie in Radarr ===")

    whitelist = load_whitelist(WHITELIST_FILE)
    if not whitelist:
        logger.error("Can't load the whitelist file")
        return

    logger.info(f"Loading whitelist ({len(whitelist)} keyword)")

    movies = get_radarr_movies()
    if not movies:
        logger.error("No movie found in Radarr")
        return

    logger.info(f"Total number of movies : {len(movies)}")

    # Filter movie
    movies_to_delete = [m for m in movies if should_delete_movie(m, DAYS_THRESHOLD, whitelist)]
    logger.info(f"Movie to delete : {len(movies_to_delete)}")

    for movie in movies_to_delete:
        logger.info(f"📌 Movie to check : {movie['title']} (Added on {movie['added']})")
        delete_movie_from_radarr(movie["id"])

    logger.info("=== End of clean ===")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Clean old movies in Radarr")
    parser.add_argument("--dry-run", action="store_true", help="Mode test (don't delete anything)")
    parser.add_argument("--days", type=int, default=DAYS_THRESHOLD, help="Number of days")
    parser.add_argument("--whitelist", type=str, default=WHITELIST_FILE, help="whitelist file")
    args = parser.parse_args()

    if args.dry_run:
        DRY_RUN = True
        logger.info("⚠ DRY RUN activated (No movie will be deleted)")

    DAYS_THRESHOLD = args.days
    WHITELIST_FILE = args.whitelist
    main()
