#!/usr/bin/env python3

from .gog.api import GogApi
from .gog.env import GOG_LANGUAGES, GOG_PLATFORMS

def gog_backup():
    licenses = GogApi.get_licenses()

    for item in licenses:
        game = GogApi.get_game_details(item)

        if not game:
            continue

        downloads = [x for x in game.downloads if x.language in GOG_LANGUAGES or not x.language]
        downloads = [x for x in downloads if x.platform in GOG_PLATFORMS or not x.platform]

        for download in downloads:
            GogApi.download_file(download)