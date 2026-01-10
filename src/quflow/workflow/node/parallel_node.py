from threading import Event

from quflow.status import Status
from quflow.tasks import Task, TaskContext

from .node import Node


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
            self.status = Status.RUNNING
            ctx = self.create_context()
            self.task.run(ctx)
            if ctx.status is Status.RUNNING:
                self.status = Status.FINISHED
            else:
                self.status = ctx.status
        except Exception as exc:
            self.interrupt.set()
            self.status = Status.CRASHED
            raise Exception(f"Exception @ Node: {self.name} -- {exc}") from exc
