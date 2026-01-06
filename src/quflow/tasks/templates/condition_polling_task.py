import threading
from typing import Callable, Any

from quflow.status import Status
from quflow.tasks.base import Task, TaskContext
from quflow.tasks.utils import empty_function, false_function, true_function


class ConditionPollingTask(Task):
    """Repeatedly executes a wrapped Task until a stop condition is met.

    Args:
        task (Task): The original Task to wrap.
        stop_condition (Callable[[], bool]): Loop terminates when this returns True.
        refresh_time_seconds (float): Sleep interval between consecutive executes.

    The typical use is for tasks that need to poll data or repeat
    some routine until an external flag is set.

    Example:
        poll_task = ConditionPollingTask(
            task=FuncTask(func=do_something),
            stop_condition=lambda: global_event.is_set(),
            refresh_time_seconds=0.1
        )
    """

    def __init__(self, *,
                 func: Callable[[TaskContext, Any], Any],
                 setup_func: Callable[[], None] | empty_function = empty_function,
                 cleanup_func: Callable[[], None] | empty_function = empty_function,
                 stop_callable: Callable[[], bool] = false_function,
                 refresh_time_seconds: float = 0.1,
                 ):
        self.func = func
        self.setup_func = setup_func
        self.cleanup_func = cleanup_func
        self.stop_callable = stop_callable
        self.refresh_time_seconds = refresh_time_seconds

    def run(self, ctx: TaskContext) -> Status:
        self.setup_func()

        while not (self.stop_callable() or ctx.interrupt.is_set()):
            data = ctx.read_callable()
            result = self.func(ctx, data)
            ctx.write_callable(result)
            ctx.interrupt.wait(self.refresh_time_seconds)


        self.cleanup_func()

        return Status.FINISHED