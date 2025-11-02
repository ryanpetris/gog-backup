#!/usr/bin/env python3

from rich.console import Console, Group
from rich.live import Live
from rich.panel import Panel

from .common import RichDownloadTracker, BlockingThreadPool
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
        for download in get_downloads(overall_progress):
            pool.submit(GogApi.download_file, download, RichDownloadTracker(download_progress))
