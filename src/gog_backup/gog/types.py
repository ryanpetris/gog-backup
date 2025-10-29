#!/usr/bin/env python3

import os

from dataclasses import dataclass
from typing import List, Mapping

from ..common import sanitize_filename


@dataclass
class GogDownload:
    game_title: str = None
    game_subtitle: str = None
    language: str = None
    platform: str = None
    file_type: str = None
    download_url: str = None
    name: str = None
    version: str = None
    date: str = None
    size: str = None
    cd_key: str = None
    storage_path: str = None

    def __init__(self, game: Mapping, language: str, platform: str, file_type: str, download: Mapping):
        self.game_title: str = game.get('title')
        self.game_subtitle = download.get('subtitle', None)
        self.language: str = language.capitalize() if language else None
        self.platform: str = platform.capitalize() if platform else None
        self.file_type: str = file_type
        self.download_url: str = download.get('manualUrl')
        self.name: str = download.get('name')
        self.version: str = download.get('version', None)
        self.date: str = download.get('date', None)
        self.size: str = download.get('size', None)
        self.cd_key: str = download.get('cdKey', None)

        self.storage_path = sanitize_filename(self.game_title)

        if self.language:
            self.storage_path = os.path.join(self.storage_path, self.language)

        if self.platform:
            self.storage_path = os.path.join(self.storage_path, self.platform)

        if self.file_type:
            self.storage_path = os.path.join(self.storage_path, self.file_type)

            if self.game_subtitle:
                self.storage_path = os.path.join(self.storage_path, sanitize_filename(self.game_subtitle))

        elif self.version:
            self.storage_path = os.path.join(self.storage_path, self.version)


@dataclass
class GogGame:
    title: str = None
    background_image: str = None
    downloads: List[GogDownload] = None

    def __init__(self, game: Mapping):
        self.title: str = game.get('title')
        self.background_image: str = game.get('backgroundImage')
        self.downloads: List[GogDownload] = []
