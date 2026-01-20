#!/usr/bin/env python3

from rich.console import Console, Group
from rich.live import Live
from rich.panel import Panel

from .common import RichDownloadTracker, BlockingThreadPool, DownloadTracker
from .gog import get_downloads, GogApi
from .layout import get_download_progress, get_overall_progress


def gog_backup():
    pool = BlockingThreadPool()

    console = Console()
    download_progress = get_download_progress()
    overall_progress = get_overall_progress()

    live = Live(
        Panel(
            Group(
                Panel(overall_progress, title="Progress"),
                Panel(download_progress, title="Downloads"),
            ),
            title="[bold red]GOG Backup[/bold red]",
        ),
        console=console,
        transient=True,
    )

    with live:
        trackers: list[DownloadTracker] = []

        for download in get_downloads(overall_progress):
            tracker = RichDownloadTracker(download_progress)
            trackers.append(tracker)

            pool.submit(GogApi.download_file, download, tracker)

        pool.wait()

        complete_files = 0
        complete_bytes = 0
        error_files = 0
        error_bytes = 0

        for tracker in trackers:
            if tracker.is_complete:
                complete_files += 1
                complete_bytes += tracker.total_bytes
            elif tracker.is_error:
                error_files += 1
                error_bytes += tracker.total_bytes

        print("Download Summary:")
        print(f"Files Downloaded:  {complete_files}")
        print(f"Bytes Downloaded:  {complete_bytes / 1024 / 1024:.2f} MB")
        print(f"Files with Errors: {error_files}")
        print(f"Bytes with Errors: {error_bytes / 1024 / 1024:.2f} MB")
