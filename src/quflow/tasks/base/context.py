import threading
from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

from quflow.status import Status


def empty_read():
    pass


def empty_write(data=None):
    pass


@dataclass
class TaskContext:
    read_callable: Callable[[], Any] = empty_read
    write_callable: Callable[[Any], None] = empty_write
    interrupt: threading.Event = threading.Event()
    status: Status = Status.RUNNING
