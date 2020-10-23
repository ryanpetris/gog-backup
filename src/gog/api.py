#!/usr/bin/env python3

from __future__ import annotations

import json
import os
import requests.models

from ..common import config, http_send, http_send_raw
from typing import Any, Dict, List, Mapping, Union
from urllib.parse import unquote, urlparse


class GogGame:
    @property
    def title(self) -> str:
        return self._title

    @property
    def background_image(self) -> str:
        return self._background_image

    @property
    def downloads(self) -> List[GogDownload]:
        return self._downloads

    def __init__(self, game: Mapping):
        self._title: str = game["title"]
        self._background_image: str = game["backgroundImage"]
        self._downloads: List[GogDownload] = []


class GogDownload:
    @property
    def game_title(self) -> str:
        return self._game_title

    @property
    def game_subtitle(self) -> str:
        return self._game_subtitle

    @property
    def language(self) -> str:
        return self._language

    @property
    def platform(self) -> str:
        return self._platform

    @property
    def file_type(self) -> str:
        return self._file_type

    @property
    def download_url(self) -> str:
        return self._download_url

    @property
    def name(self) -> str:
        return self._name

    @property
    def version(self) -> str:
        return self._version

    @property
    def date(self) -> str:
        return self._date

    @property
    def size(self) -> str:
        return self._size

    @property
    def cd_key(self) -> str:
        return self._cd_key

    def __init__(self, game: Mapping, language: str, platform: str, file_type: str, download: Mapping):
        self._game_title: str = game["title"]
        self._game_subtitle = download.get("subtitle", None)
        self._language: str = language[0].upper() + language[1:].lower() if language else None
        self._platform: str = platform[0].upper() + platform[1:].lower() if platform else None
        self._file_type: str = file_type
        self._download_url: str = download["manualUrl"]
        self._name: str = download["name"]
        self._version: str = download.get("version", None)
        self._date: str = download.get("date", None)
        self._size: str = download.get("size", None)
        self._cd_key: str = download.get("cdKey", None)


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
                            download["subtitle"] = dlc["title"].replace(f"{game.title} - ", "").replace(f"{game.title}: ", "")
                            download["cdKey"] = dlc["cdKey"]

                            game.downloads.append(GogDownload(results, language, platform, "DLC", download))

        if results["extras"]:
            for download in results["extras"]:
                download["name"] = download["name"][0].upper() + download["name"][1:].lower()

                game.downloads.append(GogDownload(results, None, None, "Extras", download))

        return game

    @classmethod
    def download_file(cls, download: GogDownload):
        if not config.GOG_ARCHIVE_DIR:
            print("Please set GOG_ARCHIVE_DIR environment variable")
            exit(1)

        game_name = cls._sanitize_fsname(download.game_title)

        download_path = os.path.join(config.GOG_ARCHIVE_DIR, game_name)
        cls._mkdir_if_not_exists(download_path)

        if download.language:
            download_path = os.path.join(download_path, download.language)
            cls._mkdir_if_not_exists(download_path)

        if download.platform:
            download_path = os.path.join(download_path, download.platform)
            cls._mkdir_if_not_exists(download_path)

        if download.file_type:
            download_path = os.path.join(download_path, download.file_type)
            cls._mkdir_if_not_exists(download_path)

            if download.game_subtitle:
                download_path = os.path.join(download_path, cls._sanitize_fsname(download.game_subtitle))
                cls._mkdir_if_not_exists(download_path)

        for item in os.listdir(download_path):
            if not item.endswith(".meta"):
                continue

            with open(os.path.join(download_path, item), 'r') as file:
                data = json.load(file)

            if data["name"] == download.name:
                if download.cd_key and "cdKey" not in data:
                    if download.file_type:
                        if download.name == "DLC" and download.game_subtitle:
                            print(f"Updating CD Key for {download.file_type} {download.game_subtitle} (Game: {download.game_title}, Language: {download.language}, Platform: {download.platform})...")
                        else:
                            print(f"Updating CD Key for {download.file_type} {download.name} (Game: {download.game_title}, Language: {download.language}, Platform: {download.platform})...")
                    else:
                        print(f"Updating CD Key for {download.name} (Game: {download.game_title}, Language: {download.language}, Platform: {download.platform})...")

                    data["cdKey"] = download.cd_key

                    with open(os.path.join(download_path, item), 'w') as file:
                        json.dump(data, file)

                return

        response = cls._send_stream(f"http://www.gog.com{download.download_url}")
        filename = unquote(urlparse(response.url).path.split("/")[-1])
        meta_filename = f"{filename}.meta"

        if os.path.exists(os.path.join(download_path, meta_filename)):
            response.close()
            return

        if download.file_type:
            if download.name == "DLC" and download.game_subtitle:
                print(f"Downloading {download.file_type} {download.game_subtitle} (Game: {download.game_title}, Language: {download.language}, Platform: {download.platform})...")
            else:
                print(f"Downloading {download.file_type} {download.name} (Game: {download.game_title}, Language: {download.language}, Platform: {download.platform})...")
        else:
            print(f"Downloading {download.name} (Game: {download.game_title}, Language: {download.language}, Platform: {download.platform})...")

        with open(os.path.join(download_path, filename), 'wb') as file:
            for chunk in response.iter_content(chunk_size=1024 * 1024 * 10):
                file.write(chunk)

        response.close()

        with open(os.path.join(download_path, meta_filename), 'w') as file:
            data = {
                "name": download.name
            }

            if download.cd_key:
                data["cdKey"] = download.cd_key

            json.dump(data, file)

    @staticmethod
    def _mkdir_if_not_exists(path: str):
        if not os.path.exists(path):
            os.mkdir(path)

    @staticmethod
    def _sanitize_fsname(val: str):
        return val.replace("/", "_")

    @classmethod
    def _get_accesstoken(cls) -> str:
        headers = {
            "Cookie": config.GOG_API_COOKIES
        }

        response = http_send("https://api.gog.com/user/accessToken.json", method="POST", headers=headers)

        return response["accessToken"]

    @classmethod
    def _send(cls, url: str, method: str = None, params: Dict[str, str] = None, body: Mapping = None, headers: Dict[str, str] = None) -> Union[Mapping, List[Any], Any]:
        if not headers:
            headers = {}

        access_token = cls._get_accesstoken()
        headers.setdefault("Authorization", f"Bearer {access_token}")

        return http_send(url, method=method, params=params, body=body, headers=headers)

    @classmethod
    def _send_stream(cls, url: str, method: str = None, params: Dict[str, str] = None, body: Mapping = None, headers: Dict[str, str] = None) -> requests.models.Response:
        if not headers:
            headers = {}

        access_token = cls._get_accesstoken()
        headers.setdefault("Authorization", f"Bearer {access_token}")

        return http_send_raw(url, method=method, params=params, body=body, headers=headers, stream=True)
