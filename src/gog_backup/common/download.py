#!/usr/bin/env python3

from abc import ABC, abstractmethod
from typing import Any

from rich.progress import Progress, TaskID


class DownloadTracker(ABC):
    @property
    def is_initialized(self) -> bool:
        return self._is_initialized

    @property
    def is_complete(self) -> bool:
        return self._is_complete

    @property
    def is_error(self) -> bool:
        return self._is_error

    @property
    def total_bytes(self) -> int:
        return self._total_bytes

    def __init__(self):
        self._is_initialized: bool = False
        self._is_complete: bool = False
        self._is_error: bool = False
        self._total_bytes: int = 0

    def __call__(self, name: str, total: int, **fields: Any):
        self._init(name, total, **fields)
        return self

    def __enter__(self):
        self._is_initialized = True
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is not None:
            self._is_error = True
        else:
            self._is_complete = True

        self._complete()

    def advance(self, amount: int, **fields: Any):
        self._total_bytes += amount
        self._advance(amount, **fields)

    @abstractmethod
    def _init(self, name: str, total: int, **fields: Any):
        raise NotImplementedError

    @abstractmethod
    def _advance(self, amount: int, **fields: Any):
        raise NotImplementedError

    @abstractmethod
    def _complete(self):
        raise NotImplementedError


class RichDownloadTracker(DownloadTracker):
    def __init__(self, progress: Progress):
        super().__init__()

        self._progress: Progress = progress
        self._task_id: TaskID | None = None

    def _init(self, name: str, total: int, **fields: Any):
        if self._task_id is not None:
            raise Exception("DownloadTracker already initialized")

        self._task_id = self._progress.add_task(name, total=total, **fields)

    def _advance(self, amount: int, **fields: Any):
        if self._task_id is None:
            raise Exception("DownloadTracker not initialized")

        self._progress.update(self._task_id, advance=amount, **fields)

    def _complete(self):
        if self._task_id is None:
            return

        self._progress.remove_task(self._task_id)
        self._task_id = None


class DummyDownloadTracker(DownloadTracker):
    def _init(self, name: str, total: int, **fields: Any):
        pass

    def _advance(self, amount: int, **fields: Any):
        pass

    def _complete(self):
        pass
