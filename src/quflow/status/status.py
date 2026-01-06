from enum import StrEnum, auto
from typing import Callable, Iterable


class Status(StrEnum):
    STOPPED = auto()
    CRASHED = auto()
    FINISHED = auto()
    RUNNING = auto()
    SKIP = auto()
    PENDING = auto()


def return_most_harsh_status(statuses: Iterable[Status]):
    return max(statuses)


class StatusReporter:
    def __init__(self):
        self._status_reporter: Callable[[Status], None] | None = None
        self.status: Status = Status.PENDING

    def register_status_reporter(self, reporter: Callable[[Status], None]) -> None:
        self._status_reporter = reporter

    def report_status(self, status: Status) -> None:
        if self._status_reporter:
            self._status_reporter(status)
            self.status = status
