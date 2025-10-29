#!/usr/bin/env python3

from abc import ABC, abstractmethod
from typing import Any

from rich.progress import Progress, TaskID


class DownloadTracker(ABC):
    def __call__(self, name: str, total: int, **fields: Any):
        self.init(name, total, **fields)
        return self

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.complete()

    @abstractmethod
    def init(self, name: str, total: int, **fields: Any):
        raise NotImplementedError

    @abstractmethod
    def advance(self, amount: int, **fields: Any):
        raise NotImplementedError

    @abstractmethod
    def complete(self):
        raise NotImplementedError


class RichDownloadTracker(DownloadTracker):
    def __init__(self, progress: Progress):
        self._progress: Progress = progress
        self._task_id: TaskID | None = None

    def init(self, name: str, total: int, **fields: Any):
        if self._task_id is not None:
            raise Exception("DownloadTracker already initialized")

        self._task_id = self._progress.add_task(name, total=total, **fields)

    def advance(self, amount: int, **fields: Any):
        if self._task_id is None:
            raise Exception("DownloadTracker not initialized")

        self._progress.update(self._task_id, advance=amount, **fields)

    def complete(self):
        if self._task_id is None:
            return

        self._progress.remove_task(self._task_id)
        self._task_id = None


class DummyDownloadTracker(DownloadTracker):
    def init(self, name: str, total: int, **fields: Any):
        pass

    def advance(self, amount: int, **fields: Any):
        pass

    def complete(self):
        pass
