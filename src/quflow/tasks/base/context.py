from typing import Optional, Any, Callable
from dataclasses import dataclass
import threading


def empty_read():
    pass


def empty_write(data=None):
    pass


@dataclass
class TaskContext:

    read_callable: Callable[[], Any] = empty_read
    write_callable: Callable[[Any], None] = empty_write
    interrupt: threading.Event = threading.Event()




