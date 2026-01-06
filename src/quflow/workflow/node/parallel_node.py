from threading import Event
from .node import Node
from quflow.tasks import Task, TaskContext


class ParallelNode(Node):
    def __init__(self, name: str, task: Task, run_in_main_thread: bool = False):
        super().__init__(name=name, task=task)
        self.run_in_main_thread = run_in_main_thread
        self._interrupt: Event | None = None

    @property
    def interrupt(self) -> Event:
        if self._interrupt is None:
            self._interrupt = Event()
        return self._interrupt

    def create_context(self) -> TaskContext:
        ctx = super().create_context()
        ctx.interrupt = self.interrupt
        return ctx

    def load_interrupt(self, interrupt: Event):
        self._interrupt = interrupt

    def run(self):
        try:
            ctx = self.create_context()
            return self.task.run(ctx)
        except Exception as exc:
            self.interrupt.set()
            raise Exception(f"Exception @ Node: {self.name} -- {exc}") from exc
