#!/usr/bin/env python3
from typing import Generator

from .api import GogApi
from .env import GOG_LANGUAGES, GOG_PLATFORMS
from .types import GogDownload


def get_downloads() -> Generator[GogDownload, None, None]:
    licenses = GogApi.get_licenses()

    for item in licenses:
        game = GogApi.get_game_details(item)

        if not game:
            continue

        downloads = [x for x in game.downloads if x.language in GOG_LANGUAGES or not x.language]
        downloads = [x for x in downloads if x.platform in GOG_PLATFORMS or not x.platform]

        for download in downloads:
            yield download
