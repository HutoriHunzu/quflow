from typing import Callable, Generator, Any

from quflow.status import Status
from quflow.tasks.base import Task, TaskContext


class GeneratorFuncTask(Task):
    """Iterates over generator and writes each yielded value.

    This template is for streaming data sources that produce a sequence of
    values over time. The generator function receives the TaskContext for
    interrupt checking.

    User function signature: generator(ctx: TaskContext) -> Generator

    The template handles:
    - Calling your generator function
    - Writing each yielded value to output channel via ctx.write_callable()
    - Checking for interrupt events to enable graceful shutdown

    Args:
        generator_callable: Function that takes context and returns a generator

    Example:
        # Generate sequence of numbers
        def gen_numbers(ctx):
            for i in range(100):
                if ctx.interrupt.is_set():
                    break
                yield i

        task = GeneratorFuncTask(generator_callable=gen_numbers)

        # Stream data from file
        def stream_file(ctx):
            with open('data.txt') as f:
                for line in f:
                    if ctx.interrupt.is_set():
                        break
                    yield line.strip()

        task = GeneratorFuncTask(generator_callable=stream_file)

        # Infinite data stream
        import time
        def sensor_stream(ctx):
            while not ctx.interrupt.is_set():
                data = read_sensor()
                yield data
                time.sleep(0.1)

        task = GeneratorFuncTask(generator_callable=sensor_stream)
    """

    def __init__(
        self, *, generator_callable: Callable[[TaskContext], Generator[Any, None, None]]
    ):
        self.generator_callable = generator_callable

    def run(self, ctx: TaskContext) -> Status:
        gen = self.generator_callable(ctx)

        for output_data in gen:
            ctx.write_callable(output_data)

            if ctx.interrupt.is_set():
                return Status.FINISHED

        return Status.FINISHED
