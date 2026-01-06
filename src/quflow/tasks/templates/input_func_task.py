from typing import Callable, Any

from quflow.status import Status
from quflow.tasks.base import Task, TaskContext


class InputFuncTask(Task):
    """Reads data and passes to user function. No automatic writing.

    This template is for sink/consumer tasks that process input data without
    producing output. Common use cases include logging, plotting, saving to
    databases, or any side-effect operations.

    User function signature: func(data: Any) -> None

    The template handles:
    - Reading from the input channel via ctx.read_callable()
    - Calling your function with the data
    - No writing to output (this is a sink node)

    Args:
        func: Callable that takes data and returns None

    Example:
        # Logging task
        task = InputFuncTask(func=lambda x: print(f"Got: {x}"))

        # Plotting task
        def plot_data(data):
            plt.plot(data)
            plt.show()

        task = InputFuncTask(func=plot_data)

        # Save to database
        def save_to_db(data):
            db.insert(data)

        task = InputFuncTask(func=save_to_db)
    """

    def __init__(self, *, func: Callable[[Any], None]):
        self.func = func

    def run(self, ctx: TaskContext) -> Status:
        data = ctx.read_callable()
        self.func(data)
        return Status.FINISHED
