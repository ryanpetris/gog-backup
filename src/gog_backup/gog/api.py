#!/usr/bin/env python3

import os
from typing import Any, Dict, List, Mapping, Union
from urllib.parse import unquote, urlparse
from uuid import uuid4

import requests.models
import yaml

from .env import GOG_ARCHIVE_DIR, GOG_API_COOKIES
from .types import GogDownload, GogGame
from ..common import http_send, http_send_raw, DownloadTracker, DummyDownloadTracker


class GogApi:
    @classmethod
    def get_licenses(cls) -> List[str]:
        return cls._send("https://menu.gog.com/v1/account/licences")

    @classmethod
    def get_game_details(cls, game_id: str) -> GogGame:
        results = cls._send(f"https://www.gog.com/account/gameDetails/{game_id}.json")

        if not results:
            return None

        game = GogGame(results)

        if results["downloads"]:
            for item in results["downloads"]:
                language = item[0]

                for platform, downloads in item[1].items():
                    for download in downloads:
                        download["cdKey"] = results["cdKey"]

                        game.downloads.append(GogDownload(results, language, platform, None, download))

        if results["dlcs"]:
            for dlc in results["dlcs"]:
                for item in dlc["downloads"]:
                    language = item[0]

                    for platform, downloads in item[1].items():
                        for download in downloads:
                            download["subtitle"] = dlc["title"].replace(f"{game.title} - ", "").replace(
                                f"{game.title}: ", "")
                            download["cdKey"] = dlc["cdKey"]

                            game.downloads.append(GogDownload(results, language, platform, "DLC", download))

        if results["extras"]:
            for download in results["extras"]:
                download["name"] = download["name"][0].upper() + download["name"][1:].lower()

                game.downloads.append(GogDownload(results, None, None, "Extras", download))

        return game

    @classmethod
    def download_file(cls, download: GogDownload, tracker: DownloadTracker = None):
        if not GOG_ARCHIVE_DIR:
            print("Please set GOG_ARCHIVE_DIR environment variable")
            exit(1)

        pprint = lambda x: None

        if tracker is None:
            tracker = DummyDownloadTracker()
            pprint = lambda x: print(x)

        temp_path = os.path.join(GOG_ARCHIVE_DIR, '.tmp')
        download_path = os.path.join(GOG_ARCHIVE_DIR, download.storage_path)

        os.makedirs(temp_path, exist_ok=True)

        if os.path.exists(download_path):
            for item in os.listdir(download_path):
                if not item.endswith(".meta"):
                    continue

                with open(os.path.join(download_path, item), 'r') as file:
                    data = yaml.safe_load(file)

                if data["name"] == download.name:
                    if download.cd_key and "cdKey" not in data:
                        if download.file_type:
                            if download.name == "DLC" and download.game_subtitle:
                                pprint(
                                    f"Updating CD Key for {download.file_type} {download.game_subtitle} (Game: {download.game_title}, Language: {download.language}, Platform: {download.platform})...")
                            else:
                                pprint(
                                    f"Updating CD Key for {download.file_type} {download.name} (Game: {download.game_title}, Language: {download.language}, Platform: {download.platform})...")
                        else:
                            pprint(
                                f"Updating CD Key for {download.name} (Game: {download.game_title}, Language: {download.language}, Platform: {download.platform})...")

                        data["cdKey"] = download.cd_key

                        with open(os.path.join(download_path, item), 'w') as file:
                            yaml.safe_dump(data, file)

                    return

        response = cls._send_stream(f"http://www.gog.com{download.download_url}")
        filename = unquote(urlparse(response.url).path.split("/")[-1])
        meta_filename = f"{filename}.meta"

        if os.path.exists(os.path.join(download_path, meta_filename)):
            response.close()
            return

        if download.file_type:
            if download.name == "DLC" and download.game_subtitle:
                pprint(
                    f"Downloading {download.file_type} {download.game_subtitle} (Game: {download.game_title}, Language: {download.language}, Platform: {download.platform})...")
            else:
                pprint(
                    f"Downloading {download.file_type} {download.name} (Game: {download.game_title}, Language: {download.language}, Platform: {download.platform})...")
        else:
            pprint(
                f"Downloading {download.name} (Game: {download.game_title}, Language: {download.language}, Platform: {download.platform})...")

        download_uuid = str(uuid4())

        tracker_fields = {
            'name': download.name,
            'total': int(response.headers.get('content-length', 0)),
            'title': download.game_title or '',
            'subtitle': download.game_subtitle or '',
            'language': download.language or '',
            'platform': download.platform or '',
            'type': download.file_type or '',
        }

        with tracker(**tracker_fields):
            with open(os.path.join(temp_path, download_uuid), 'wb') as file:
                for chunk in response.iter_content(chunk_size=1024 * 512):
                    tracker.advance(len(chunk))
                    file.write(chunk)

        response.close()

        os.makedirs(download_path, exist_ok=True)
        os.rename(os.path.join(temp_path, download_uuid), os.path.join(download_path, filename))

        with open(os.path.join(download_path, meta_filename), 'w') as file:
            data = {
                "name": download.name
            }

            if download.cd_key:
                data["cdKey"] = download.cd_key

            yaml.safe_dump(data, file)

    @staticmethod
    def _sanitize_fsname(val: str):
        return val.replace("/", "_")

    @classmethod
    def _get_access_token(cls) -> str:
        headers = {
            "Cookie": GOG_API_COOKIES
        }

        response = http_send("https://api.gog.com/user/accessToken.json", method="POST", headers=headers)

        return response["accessToken"]

    @classmethod
    def _send(cls, url: str, method: str = None, params: Dict[str, str] = None, body: Mapping = None,
              headers: Dict[str, str] = None) -> Union[Mapping, List[Any], Any]:
        if not headers:
            headers = {}

        access_token = cls._get_access_token()
        headers.setdefault("Authorization", f"Bearer {access_token}")

        return http_send(url, method=method, params=params, body=body, headers=headers)

    @classmethod
    def _send_stream(cls, url: str, method: str = None, params: Dict[str, str] = None, body: Mapping = None,
                     headers: Dict[str, str] = None) -> requests.models.Response:
        if not headers:
            headers = {}

        access_token = cls._get_access_token()
        headers.setdefault("Authorization", f"Bearer {access_token}")

        return http_send_raw(url, method=method, params=params, body=body, headers=headers, stream=True)
