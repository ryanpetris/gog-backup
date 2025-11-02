#!/usr/bin/env python3

from rich.progress import (
    Progress,
    TextColumn,
    BarColumn,
    TaskProgressColumn,
    TimeRemainingColumn,
    FileSizeColumn,
    TransferSpeedColumn,
    TimeElapsedColumn,
)

from ..gog import GOG_SINGLE_LANGUAGE


def get_download_progress() -> Progress:
    columns = (
        TextColumn("{task.fields[title]}"),
        TextColumn("{task.fields[subtitle]}"),
        TextColumn("{task.fields[type]}"),
        TextColumn("{task.fields[platform]}"),
        TextColumn("{task.fields[language]}") if not GOG_SINGLE_LANGUAGE else None,
        TextColumn("[progress.description]{task.description}"),
        BarColumn(bar_width=None),
        TaskProgressColumn(),
        TimeRemainingColumn(),
        FileSizeColumn(),
        TransferSpeedColumn(),
    )

    columns = (x for x in columns if x is not None)

    return Progress(*columns)


def get_overall_progress() -> Progress:
    columns = (
        TextColumn("[progress.description]{task.description}"),
        BarColumn(bar_width=None),
        TaskProgressColumn(),
        TextColumn("{task.completed}/{task.total}"),
        TimeElapsedColumn(),
    )

    columns = (x for x in columns if x is not None)

    return Progress(*columns)
