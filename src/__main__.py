#!/usr/bin/env python3

from .gog import GogApi
from .common import config


licenses = GogApi.get_licenses()

for license in licenses:
    game = GogApi.get_game_details(license)

    if not game:
        continue

    downloads = [x for x in game.downloads if x.language in config.GOG_LANGUAGES or not x.language]
    downloads = [x for x in downloads if x.platform in config.GOG_PLATFORMS or not x.platform]

    for download in downloads:
        GogApi.download_file(download)
