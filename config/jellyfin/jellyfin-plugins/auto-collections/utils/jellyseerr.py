import requests
import urllib.parse
from loguru import logger

class JellyseerrClient:
    def __init__(self, server_url: str, api_key:str=None, email: str=None, password: str=None, user_type: str="local"):
        # Fix common url issues
        if server_url.endswith("/"):
            server_url = server_url[:-1]  # Remove trailing slash 
        if not server_url.endswith("/api/v1"):
            server_url += "/api/v1"
        self.server_url = server_url

        if user_type not in ["local", "plex", "jellyfin"]:
            raise Exception("Invalid user type. Must be one of: local, plex, jellyfin")

        # Check if server is reachable
        try:
            r = requests.get(self.server_url + "/status")
            if r.status_code != 200:
                raise Exception("Jellyseerr Server is not reachable")
        except requests.exceptions.ConnectionError:
            raise Exception("Jellyseerr Server is not reachable")

        self.session = requests.Session()
        self.api_key = api_key
        if api_key is not None:
            self.session.headers.update({
                "X-Api-Key": api_key
            })
        if email is not None and password is not None:
            r = self.session.post(f"{self.server_url}/auth/{user_type}", json={
                "email": email,
                "password": password
            })
            if r.status_code != 200:
                raise Exception("Invalid jellyseerr email or password")

        # Check if user is authenticated
        r = self.session.get(f"{self.server_url}/auth/me")
        if r.status_code != 200:
            raise Exception("jellyseerr user is not authenticated")


    def make_request(self, item):
        '''Request item from jellyseerr'''

        # Search for item
        try:
            r = self.session.get(f"{self.server_url}/search", params={
                "query": urllib.parse.quote_plus(item["title"])
            })
            r.raise_for_status()
            search_results = r.json().get("results", [])
        except Exception as e:
            logger.warning(f"Failed to search Jellyseerr for {item.get('title', 'unknown')}: {e}")
            return
        
        # Find matching item
        mediaId = None
        matched_result = None
        
        for result in search_results:
            # Try IMDB match first
            if "mediaInfo" in result and "ImdbId" in result["mediaInfo"]:
                imdb_id = result["mediaInfo"]["ImdbId"]
                if imdb_id == item.get("imdb_id"):
                    mediaId = result["id"]
                    matched_result = result
                    logger.debug(f"Found exact IMDB match for {item['title']}")
                    break
            elif "releaseDate" in result and item.get("release_year"):
                # Try year match
                release_year = result["releaseDate"].split("-")[0]
                if release_year == str(item["release_year"]):
                    mediaId = result["id"]
                    matched_result = result
                    logger.debug(f"Found year match for {item['title']}")
                    break

        # Request item if match found and not already in Jellyfin
        if mediaId is not None and matched_result is not None:
            if "mediaInfo" not in matched_result or matched_result["mediaInfo"].get("jellyfinMediaId") is None:
                # If it's not already in Jellyfin, request it
                try:
                    r = self.session.post(f"{self.server_url}/request", json={
                        "mediaType": matched_result["mediaType"],
                        "mediaId": mediaId,
                    })
                    r.raise_for_status()
                    logger.info(f"Requested {item['title']} from Jellyseerr")
                except Exception as e:
                    logger.warning(f"Failed to request {item['title']} from Jellyseerr: {e}")
            else:
                logger.debug(f"Item {item['title']} already exists in Jellyfin, skipping request")
        else:
            logger.debug(f"No match found in Jellyseerr for {item.get('title', 'unknown')}")



if __name__ == "__main__":
    # Example usage - remove hardcoded path
    # This is a test/example block, not used in production
    import sys
    import os
    
    # Try to find config in common locations
    config_paths = [
        os.path.join(os.path.dirname(__file__), "../../config.yaml"),
        os.path.join(os.path.dirname(__file__), "../config.yaml"),
        "/app/config/config.yaml",
        "config.yaml"
    ]
    
    config = None
    for path in config_paths:
        if os.path.exists(path):
            from pyaml_env import parse_config
            config = parse_config(path, default_value=None)
            break
    
    if config is None:
        print("Error: Could not find config.yaml file")
        sys.exit(1)

    client = JellyseerrClient(
        server_url=config["jellyseerr"]["server_url"],
        api_key=config["jellyseerr"].get("api_key"),
        email=config["jellyseerr"].get("email"),
        password=config["jellyseerr"].get("password"),
        user_type=config["jellyseerr"].get("user_type", "local")
    )
    client.make_request({
        "title": "The Matrix",
        "imdb_id": "tt0133093",
        "release_year": 1999
    })
