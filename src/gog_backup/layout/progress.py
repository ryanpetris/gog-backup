#!/usr/bin/env python3

from typing import Optional

from rich.markup import escape
from rich.progress import (
    Progress,
    TextColumn,
    BarColumn,
    TaskProgressColumn,
    TimeRemainingColumn,
    TotalFileSizeColumn,
    TransferSpeedColumn,
    TimeElapsedColumn,
    ProgressColumn,
    Task,
)
from rich.table import Column
from rich.text import Text

from ..gog import GOG_SINGLE_LANGUAGE


class TaskDescriptionColumn(ProgressColumn):
    def __init__(self, table_column: Optional[Column] = None) -> None:
        super().__init__(table_column=table_column or Column(no_wrap=True))

    def render(self, task: Task) -> Text:
        title = task.fields.get("title")
        subtitle = task.fields.get("subtitle")
        file_type = task.fields.get("type")
        platform = task.fields.get("platform")
        language = task.fields.get("language")

        if task.description.startswith(title):
            task.description = task.description[len(title):].lstrip()

        text_parts = []

        if file_type:
            text_parts.append(f'[color blue]\[{escape(file_type)}][/]')

        if platform:
            text_parts.append(f'[color green]\[{escape(platform)}][/]')

        if language and not GOG_SINGLE_LANGUAGE:
            text_parts.append(f'[color red]\[{escape(language)}][/]')

        text_parts.append(escape(title))
        text_parts.append(f'({escape(subtitle)})')
        text_parts.append(escape(task.description))

        return Text.from_markup(" ".join(text_parts))


def get_download_progress() -> Progress:
    columns = (
        TaskDescriptionColumn(),
        BarColumn(bar_width=None),
        TaskProgressColumn(),
        TimeRemainingColumn(),
        TotalFileSizeColumn(),
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
