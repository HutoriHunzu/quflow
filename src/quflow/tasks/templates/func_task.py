import threading
from typing import Callable, Optional
from typing import Any

from quflow.status import Status

from quflow.tasks.base import Task, TaskContext
from quflow.tasks.utils import empty_function, true_function


class FuncTask(Task):
    """Executes a simple Python function with optional input/output from channels.

    The function signature can be either:
    - func() with no parameters, or
    - func(data) taking a single argument from the read channel.

    The result of the function is automatically written to the write channel.

    Args:
        func (Callable): The function to wrap.
        setup_func (Callable): Optional setup routine, runs before execute().
        cleanup_func (Callable): Optional cleanup routine, runs after execute().
        interrupt (threading.Event): Optional event used to interrupt the task.

    Example:
        def multiply_by_two(num):
            return num * 2

        task = FuncTask(func=multiply_by_two)
    """

    def __init__(self, *,
                 func: Callable[[TaskContext], None],
                 setup_func: Callable[[], None] | empty_function = empty_function,
                 cleanup_func: Callable[[], None] | empty_function = empty_function,
                 ):

        self.func = func
        self.setup_func = setup_func
        self.cleanup_func = cleanup_func

    def run(self, ctx):
        self.setup_func()
        self.func(ctx)
        self.cleanup_func()

        return Status.FINISHED