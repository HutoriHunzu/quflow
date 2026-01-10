from collections.abc import Callable

from quflow.tasks.base import Task, TaskContext


class ContextFuncTask(Task):
    """Executes user function with full TaskContext access.

    This template is for advanced users who need full control over the
    TaskContext. Use this when you need custom read/write logic, conditional
    I/O, or access to the interrupt event.

    For simpler cases, prefer TransformFuncTask, InputFuncTask, or OutputFuncTask.

    User function signature: func(ctx: TaskContext) -> None

    The template handles:
    - Calling your function with the full TaskContext
    - Your function is responsible for all read/write operations

    Args:
        func: Callable that takes TaskContext and returns None

    Example:
        # Custom control flow
        def custom_logic(ctx):
            data = ctx.read_callable()
            if data > 10:
                ctx.write_callable(data * 2)
            else:
                ctx.write_callable(0)

        task = ContextFuncTask(func=custom_logic)

        # Interruptible processing
        def process_with_interrupt(ctx):
            data = ctx.read_callable()
            for item in data:
                if ctx.interrupt.is_set():
                    break
                result = process(item)
                ctx.write_callable(result)

        task = ContextFuncTask(func=process_with_interrupt)
    """

    def __init__(self, *, func: Callable[[TaskContext], None]):
        self.func = func

    def run(self, ctx: TaskContext):
        self.func(ctx)
