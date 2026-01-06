import threading
from typing import Callable, Generator, Any

from quflow.status import Status
from quflow.tasks.base import Task, TaskContext
from quflow.tasks.utils import empty_function, false_function


class GeneratorTask(Task):
    """Reads from a Python generator and writes each yielded item to the output channel.

    Args:
        generator (Generator): A Python generator object.
        setup_func (Callable): Called before iteration begins (optional).
        cleanup_func (Callable): Called after the generator is exhausted (optional).
        interrupt (threading.Event): If set, can be used to halt execution.

    Flow:
        - setup_func()
        - for each item in generator:
            write_data(item)
        - cleanup_func()
    """

    def __init__(self, *,
                 generator_callable: Callable[[TaskContext], Generator[Any, None, None]],
                 setup_func: Callable[[], None] | empty_function = empty_function,
                 cleanup_func: Callable[[], None] | empty_function = empty_function,
                 ):

        self.generator_callable = generator_callable
        self.setup_func = setup_func
        self.cleanup_func = cleanup_func

    def run(self, ctx: TaskContext):

        self.setup_func()

        gen = self.generator_callable(ctx)

        # Call the function; it is expected to return an iterator/generator.
        for output_data in gen:

            ctx.write_callable(output_data)

            if ctx.interrupt.is_set():
                self.cleanup_func()
                return Status.FINISHED
