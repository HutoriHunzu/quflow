from collections.abc import Callable
from typing import Any

from quflow.tasks.base import Task, TaskContext


class OutputFuncTask(Task):
    """Calls user function and writes result. No reading.

    This template is for source/producer tasks that generate data without
    requiring input. Common use cases include data generation, sensor reading,
    file loading, or any data source operations.

    User function signature: func() -> Any

    The template handles:
    - Calling your function (no parameters)
    - Writing the result to output channel via ctx.write_callable()
    - No reading from input (this is a source node)

    Args:
        func: Callable with no parameters that returns data

    Example:
        # Random data generator
        import numpy as np
        task = OutputFuncTask(func=lambda: np.random.randn(100))

        # Sensor reading
        def read_sensor():
            return sensor.get_current_value()

        task = OutputFuncTask(func=read_sensor)

        # File loading
        def load_data():
            with open('data.txt') as f:
                return f.read()

        task = OutputFuncTask(func=load_data)
    """

    def __init__(self, *, func: Callable[[], Any]):
        self.func = func

    def run(self, ctx: TaskContext):
        result = self.func()
        ctx.write_callable(result)
