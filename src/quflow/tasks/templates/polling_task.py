from typing import Callable

from quflow.status import Status
from quflow.tasks.base import Task, TaskContext
from quflow.tasks.utils import false_function


class PollingTask(Task):
    """Repeatedly runs a wrapped task until stop condition is met.

    This is a task decorator that adds polling behavior to any task. Instead
    of running once, the wrapped task will execute repeatedly until either
    the stop condition returns True or an interrupt is triggered.

    This compositional design allows you to poll ANY task type - transform
    tasks, input tasks, output tasks, or even custom tasks.

    Args:
        task: The task to run repeatedly
        stop_callable: Function that returns True when polling should stop
        refresh_time_seconds: Sleep interval between iterations

    Example:
        # Poll a transform task
        transform = TransformFuncTask(func=lambda x: x * 2)
        polling = PollingTask(
            task=transform,
            stop_callable=lambda: should_stop,
            refresh_time_seconds=0.1
        )

        # Poll an output task (sensor reading)
        sensor = OutputFuncTask(func=read_sensor)
        polling_sensor = PollingTask(
            task=sensor,
            stop_callable=lambda: reading_complete,
            refresh_time_seconds=0.5
        )

        # Poll an input task (logging)
        logger = InputFuncTask(func=lambda x: print(f"Data: {x}"))
        polling_logger = PollingTask(
            task=logger,
            stop_callable=lambda: done_logging
        )

        # Use with workflow
        workflow.add_node(Node("polling_sensor", polling_sensor))
    """

    def __init__(
        self,
        *,
        task: Task,
        stop_callable: Callable[[], bool] = false_function,
        refresh_time_seconds: float = 0.1,
    ):
        self.task = task
        self.stop_callable = stop_callable
        self.refresh_time_seconds = refresh_time_seconds

    def run(self, ctx: TaskContext) -> Status:
        while not (self.stop_callable() or ctx.interrupt.is_set()):
            # Run the wrapped task completely
            status = self.task.run(ctx)

            # If wrapped task failed, propagate the status
            if status != Status.FINISHED:
                return status

            # Wait before next iteration (interruptible)
            ctx.interrupt.wait(self.refresh_time_seconds)

        return Status.FINISHED
