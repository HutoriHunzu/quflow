from collections.abc import Callable, Iterable
from enum import StrEnum, auto


class Status(StrEnum):
    PENDING = auto()
    RUNNING = auto()
    SKIP = auto()
    FINISHED = auto()
    REJECT = auto()
    CRASHED = auto()
    STOPPED = auto()


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
