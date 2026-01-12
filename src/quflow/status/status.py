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


_SEVERITY: dict[Status, int] = {
    Status.PENDING: 0,
    Status.RUNNING: 1,
    Status.SKIP: 2,
    Status.FINISHED: 3,
    Status.REJECT: 4,
    Status.STOPPED: 5,
    Status.CRASHED: 6,
}


def return_most_harsh_status(statuses: Iterable[Status]) -> Status:
    return max(statuses, key=lambda x: _SEVERITY.get(x, 1))


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
