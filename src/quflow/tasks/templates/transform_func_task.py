from collections.abc import Callable
from typing import Any

from quflow.tasks.base import Task, TaskContext


class TransformFuncTask(Task):
    """Reads data, applies user function, and writes result.

    This is the most common pattern for pipeline transformations where you
    need to process input data and produce output data.

    User function signature: func(data: Any) -> Any

    The template handles:
    - Reading from the input channel via ctx.read_callable()
    - Calling your function with the data
    - Writing the result to output channel via ctx.write_callable()

    Args:
        func: Callable that takes data and returns transformed data

    Example:
        # Simple transformation
        task = TransformFuncTask(func=lambda x: x * 2)

        # More complex processing
        def process_data(data):
            result = complex_calculation(data)
            return result

        task = TransformFuncTask(func=process_data)
    """

    def __init__(self, *, func: Callable[[Any], Any]):
        self.func = func

    def run(self, ctx: TaskContext):
        data = ctx.read_callable()
        result = self.func(data)
        ctx.write_callable(result)
