#!/usr/bin/env python3

from rich.progress import Progress, TransferSpeedColumn, TextColumn

from .common import RichDownloadTracker, BlockingThreadPool
from .gog import get_downloads, GogApi


def gog_backup():
    pool = BlockingThreadPool()

    columns = (
        TextColumn("{task.fields[title]}"),
        TextColumn("{task.fields[subtitle]}"),
        TextColumn("{task.fields[type]}"),
        TextColumn("{task.fields[platform]}"),
        TextColumn("{task.fields[language]}"),
        *Progress.get_default_columns(),
        TransferSpeedColumn(),
    )

    with Progress(*columns) as p:
        for download in get_downloads():
            pool.submit(GogApi.download_file, download, RichDownloadTracker(p))
