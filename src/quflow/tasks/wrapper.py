from typing import Any, Callable
from .base import Task


class TaskWrapper(Task):
    """Base class for all task wrappers using composition"""

    def __init__(self, wrapped_task: Task):
        super().__init__()
        self.wrapped_task = wrapped_task

    def __getattr__(self, name: str) -> Any:
        """Delegate attributes to wrapped task"""
        return getattr(self.wrapped_task, name)


    def connect_to_io(self,
                            read_callable: Callable | None = None,
                            write_callable: Callable | None = None):

        self.wrapped_task.connect_to_io(read_callable=read_callable,
                                        write_callable=write_callable)

    def read_data(self):
        return self.wrapped_task.read_data()

    def write_data(self, data):
        return self.wrapped_task.write_data(data)


    # Lifecycle delegation
    def setup(self) -> None:
        self.wrapped_task.setup()

    def execute(self) -> Any:
        return self.wrapped_task.execute()

    def cleanup(self) -> None:
        self.wrapped_task.cleanup()

    def handle_exception(self, exc: Exception) -> None:
        self.wrapped_task.handle_exception(exc)


# class TimerWrapper(TaskWrapper):
#     """Wrapper that adds periodic execution"""
#
#     def __init__(self, wrapped_task: Task, interval_sec: float):
#         super().__init__(wrapped_task)
#         self.interval_sec = interval_sec
#
#     def execute(self) -> None:
#         while True:
#             result = super().execute()
#             time.sleep(self.interval_sec)
#             return result  # Optional: return last result
#
#
# class InterruptibleWrapper(TaskWrapper):
#     """Wrapper that adds interruption support"""
#
#     def __init__(self, wrapped_task: Task, interrupt_flag: threading.Event):
#         super().__init__(wrapped_task)
#         self.interrupt_flag = interrupt_flag
#
#     def execute(self) -> Any:
#         while not self.interrupt_flag.is_set():
#             return super().execute()
#         raise InterruptedError("Task execution interrupted")