#!/usr/bin/env python3

from typing import Generator

from rich.progress import Progress

from .api import GogApi
from .env import GOG_LANGUAGES, GOG_PLATFORMS
from .types import GogDownload


def get_downloads(progress: Progress) -> Generator[GogDownload, None, None]:
    licenses = GogApi.get_licenses()
    task = progress.add_task("Licenses", total=len(licenses))

    for item in licenses:
        game = GogApi.get_game_details(item)

        if not game:
            progress.advance(task)
            continue

        downloads = [x for x in game.downloads if x.language in GOG_LANGUAGES or not x.language]
        downloads = [x for x in downloads if x.platform in GOG_PLATFORMS or not x.platform]

        license_task = progress.add_task(game.title, total=len(downloads))

        for download in downloads:
            progress.advance(license_task)
            yield download

        progress.remove_task(license_task)
        progress.advance(task)
