#!/usr/bin/env python3

from rich.progress import Progress, TransferSpeedColumn, TextColumn

from .common import RichDownloadTracker, BlockingThreadPool
from .gog import get_downloads, GogApi, GOG_SINGLE_LANGUAGE


def gog_backup():
    pool = BlockingThreadPool()

    columns = (
        TextColumn("{task.fields[title]}"),
        TextColumn("{task.fields[subtitle]}"),
        TextColumn("{task.fields[type]}"),
        TextColumn("{task.fields[platform]}"),
        TextColumn("{task.fields[language]}") if not GOG_SINGLE_LANGUAGE else None,
        *Progress.get_default_columns(),
        TransferSpeedColumn(),
    )

    columns = (x for x in columns if x is not None)

    with Progress(*columns) as p:
        for download in get_downloads():
            pool.submit(GogApi.download_file, download, RichDownloadTracker(p))
