#!/usr/bin/env python3

import queue
import threading


class BlockingThreadPool:
    def __init__(self, workers=5):
        self._queue = queue.Queue(maxsize=1)
        self._threads = []
        self._stop_signal = False

        for i in range(workers):
            t = threading.Thread(target=self.worker, daemon=True)
            t.start()
            self._threads.append(t)

    def worker(self):
        while not self._stop_signal:
            try:
                task, args, kwargs = self._queue.get(timeout=1)
            except queue.Empty:
                continue

            try:
                task(*args, **kwargs)
            except Exception as e:
                print(f"Task error: {e}")
            finally:
                self._queue.task_done()

    def submit(self, task, *args, **kwargs):
        self._queue.put((task, args, kwargs))

    def wait(self):
        self._queue.join()

    def stop(self):
        self._stop_signal = True

        for t in self._threads:
            t.join()
