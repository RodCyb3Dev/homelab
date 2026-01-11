import requests
from loguru import logger
from base64 import b64encode
import json
import concurrent.futures
from .poster_generation import fetch_collection_posters, safe_download, create_mosaic, get_font


class JellyfinClient:

    imdb_to_jellyfin_type_map = {
        "movie": ["Movie"],
        "short": ["Movie"],
        "tvEpisode": ["TvProgram", "Episode"],
        "tvSeries": ["Program", "Series"],
        "tvShort": ["TvProgram", "Episode", "Program"],
        "tvMiniSeries": ["Program", "Series"],
        "tvMovie": ["Movie", "TvProgram", "Episode"],
        "video": ["Movie", "TvProgram", "Episode", "Series"],
        "show": ["Program", "Series"],
    }

    def __init__(self, server_url: str, api_key: str, user_id: str):
        self.server_url = server_url
        self.api_key = api_key
        self.user_id = user_id

        # Check if server is reachable
        try:
            requests.get(self.server_url)
        except requests.exceptions.ConnectionError:
            raise Exception("Server is not reachable")

        # Check if api key is valid
        res = requests.get(f"{self.server_url}/Users/{self.user_id}", headers={"X-Emby-Token": self.api_key})
        if res.status_code != 200:
            raise Exception("Invalid API key")

        # Check if user id is valid
        res = requests.get(f"{self.server_url}/Users/{self.user_id}", headers={"X-Emby-Token": self.api_key})
        if res.status_code != 200:
            raise Exception("Invalid user id")


    def get_all_collections(self):
        params = {
            "enableTotalRecordCount": "false",
            "enableImages": "false",
            "Recursive": "true",
            "includeItemTypes": "BoxSet",
            "fields": ["Name", "Id", "Tags"]
        }
        logger.info("Getting collections list...")
        res = requests.get(f'{self.server_url}/Users/{self.user_id}/Items',headers={"X-Emby-Token": self.api_key}, params=params)
        return res.json()["Items"]


    def find_collection_with_name_or_create(self, list_name: str, list_id: str, description: str, plugin_name: str) -> str:
        '''Returns the collection id of the collection with the given name. If it doesn't exist, it creates a new collection and returns the id of the new collection.'''
        collection_id = None
        collections = self.get_all_collections()

        # Check if list name in tags
        for collection in collections:
            if json.dumps(list_id) in collection["Tags"]:
                collection_id = collection["Id"]
                break

        # if no match - Check if list name == collection name
        if collection_id is None:
            for collection in collections:
                if list_name == collection["Name"]:
                    collection_id = collection["Id"]
                    break

        if collection_id is not None:
            logger.info("found existing collection: " + list_name + " (" + collection_id + ")")

        if collection_id is None:
            # Collection doesn't exist -> Make a new one
            logger.info("No matching collection found for: " + list_name + ". Creating new collection...")
            res2 = requests.post(f'{self.server_url}/Collections',headers={"X-Emby-Token": self.api_key}, params={"name": list_name})
            collection_id = res2.json()["Id"]

        # Update collection description and add tags to we can find it later
        if collection_id is not None:
            collection = requests.get(f'{self.server_url}/Users/{self.user_id}/Items/{collection_id}', headers={"X-Emby-Token": self.api_key}).json()
            if collection.get("Overview", "") == "" and description is not None:
                collection["Overview"] = description
            collection["Tags"] = list(set(collection.get("Tags", []) + ["Jellyfin-Auto-Collections", plugin_name, json.dumps(list_id)]))
            r = requests.post(f'{self.server_url}/Items/{collection_id}',headers={"X-Emby-Token": self.api_key}, json=collection)

        return collection_id

    def has_poster(self, collection_id):
        '''Check if a collection already has a poster'''
        poster_url = f"{self.server_url}/Items/{collection_id}/Images/Primary"
        r = requests.get(poster_url, headers={"X-Emby-Token": self.api_key})
        if r.status_code == 404:
            return False
        return True


    def make_poster(self, collection_id, collection_name, mosaic_limit=20, google_font_url="https://fonts.googleapis.com/css2?family=Dosis:wght@800&display=swap"):

        # Check if collection poster exists
        poster_urls = fetch_collection_posters(self.server_url, self.api_key, self.user_id, collection_id)[:mosaic_limit]
        headers={"X-Emby-Token": self.api_key}

        # Use a ThreadPoolExecutor to download images in parallel
        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(safe_download, url, headers) for url in poster_urls]
            results = [future.result() for future in concurrent.futures.as_completed(futures)]

        # Filter out any failed downloads (None values)
        poster_images = [img for img in results if img is not None]

        font_path = get_font(google_font_url)

        if poster_images:
            safe_name = collection_name.replace(" ", "_").replace("/", "_")
            output_path = f"/tmp/{safe_name}_cover.jpg"
            create_mosaic(poster_images, collection_name, output_path, font_path)
        else:
            logger.warning(f"No posters available for collection '{collection_name}'. Skipping mosaic generation.")
            return

        # Upload

        from PIL import Image
        img = Image.open(output_path)  # or whatever format
        img = img.convert("RGB")  # Ensures it's safe for JPEG
        img.save(output_path, format="JPEG")

        with open(output_path, 'rb') as f:
            img_data = f.read()
        encoded_data = b64encode(img_data)

        headers["Content-Type"] = "image/jpeg"
        r = requests.post(f"{self.server_url}/Items/{collection_id}/Images/Primary", headers=headers, data=encoded_data)


    def add_item_to_collection(self, collection_id: str, item, year_filter: bool = True, jellyfin_query_parameters={}):
        '''Adds an item to a collection based on item name and release year'''

        # Map media type to Jellyfin types
        media_type_mapping = self.imdb_to_jellyfin_type_map.get(item["media_type"], [item["media_type"]])
        if isinstance(media_type_mapping, list):
            # Use first type if it's a list, but search all types
            primary_type = media_type_mapping[0] if media_type_mapping else item["media_type"]
        else:
            primary_type = media_type_mapping

        # First, try searching by IMDB ID if available (most accurate)
        match = None
        if "imdb_id" in item and item["imdb_id"]:
            params = {
                "enableTotalRecordCount": "false",
                "enableImages": "false",
                "Recursive": "true",
                "fields": ["ProviderIds", "ProductionYear", "Name", "Type"]
            }
            # Optionally filter by media type for better accuracy
            if primary_type and primary_type in ["Movie", "Series", "Program"]:
                params["IncludeItemTypes"] = primary_type
            params = {**params, **jellyfin_query_parameters}
            
            # Search all libraries recursively
            res = requests.get(f'{self.server_url}/Users/{self.user_id}/Items',headers={"X-Emby-Token": self.api_key}, params=params)
            
            for result in res.json().get("Items", []):
                if result.get("ProviderIds", {}).get("Imdb", "").lower() == item["imdb_id"].lower():
                    # Verify the type matches expected media type (if mapping exists)
                    result_type = result.get("Type", "")
                    if media_type_mapping and isinstance(media_type_mapping, list):
                        if result_type not in media_type_mapping:
                            logger.debug(f"IMDB match found but type mismatch: expected {media_type_mapping}, got {result_type}. Continuing search...")
                            continue
                    match = result
                    logger.debug(f"Found exact IMDB match: {item['title']} ({item.get('imdb_id')}) - Type: {result_type}")
                    break

        # If no IMDB match, try title search
        if match is None:
            params = {
                "enableTotalRecordCount": "false",
                "enableImages": "false",
                "Recursive": "true",
                "IncludeItemTypes": primary_type,
                "searchTerm": item["title"],
                "fields": ["ProviderIds", "ProductionYear", "Name"]
            }
            params = {**params, **jellyfin_query_parameters}

            res = requests.get(f'{self.server_url}/Users/{self.user_id}/Items',headers={"X-Emby-Token": self.api_key}, params=params)
            results = res.json().get("Items", [])

            if len(results) > 0:
                # If year filter is enabled, try to match by year first
                if year_filter and "release_year" in item and item["release_year"]:
                    for result in results:
                        if str(result.get("ProductionYear", "")) == str(item["release_year"]):
                            match = result
                            logger.debug(f"Found year match: {item['title']} ({item.get('release_year')})")
                            break
                
                # If still no match, check for title similarity (case-insensitive)
                if match is None:
                    title_lower = item["title"].lower().strip()
                    for result in results:
                        result_title = result.get("Name", "").lower().strip()
                        if title_lower == result_title:
                            match = result
                            logger.debug(f"Found title match: {item['title']}")
                            break
                
                # Last resort: take first result if only one
                if match is None and len(results) == 1:
                    match = results[0]
                    logger.debug(f"Using single result match: {item['title']}")

        if match is None:
            logger.warning(f"Item {item['title']} ({item.get('release_year','N/A')}) {item.get('imdb_id','')} not found in jellyfin")
            return False
        else:
            try:
                item_id = match["Id"]
                # Check if item is already in collection
                collection_items = requests.get(f'{self.server_url}/Collections/{collection_id}/Items', headers={"X-Emby-Token": self.api_key})
                existing_ids = [existing_item["Id"] for existing_item in collection_items.json().get("Items", [])]
                
                if item_id in existing_ids:
                    logger.debug(f"Item {item['title']} already in collection, skipping")
                    return True
                
                # Add item to collection
                add_response = requests.post(f'{self.server_url}/Collections/{collection_id}/Items?ids={item_id}', headers={"X-Emby-Token": self.api_key})
                if add_response.status_code in [200, 204]:
                    logger.info(f"Added {item['title']} ({match.get('Name', 'N/A')}) to collection")
                    logger.debug(f"\tList item: {item}")
                    logger.debug(f"\tMatched JF item: {match.get('Name')} (ID: {match.get('Id')})")
                    return True
                else:
                    logger.warning(f"Failed to add {item['title']} to collection. Status: {add_response.status_code}")
                    return False
            except json.decoder.JSONDecodeError:
                logger.error(f"Error adding {item['title']} to collection - JSONDecodeError")
                return False
            except Exception as e:
                logger.error(f"Error adding {item['title']} to collection: {e}")
                return False
        return False



    def clear_collection(self, collection_id: str):
        '''Clears a collection by removing all items from it'''
        res = requests.get(f'{self.server_url}/Users/{self.user_id}/Items',headers={"X-Emby-Token": self.api_key}, params={"Recursive": "true", "parentId": collection_id})
        all_ids = [item["Id"] for item in res.json()["Items"]]

        # chunk ids into groups of 10
        all_ids = [all_ids[i:i + 10] for i in range(0, len(all_ids), 10)]
        for ids in all_ids:
             requests.delete(f'{self.server_url}/Collections/{collection_id}/Items',headers={"X-Emby-Token": self.api_key}, params={"ids": ",".join(ids)})

        logger.info(f"Cleared collection {collection_id}")
