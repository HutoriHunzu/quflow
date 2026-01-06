from threading import Event
from .node import Node
from quflow.tasks import Task
from quflow.status import Status



class ParallelNode(Node):

    def __init__(self, name: str, task: Task,
                 run_in_main_thread: bool = False):

        super().__init__(name=name, task=task)
        self.run_in_main_thread = run_in_main_thread
        self.interrupt: Event | None = None

    def create_context(self):
        ctx = super().create_context()
        ctx.interrupt = self.interrupt
        return ctx

    def load_interrupt(self, interrupt: Event):
        self.interrupt = interrupt

    def run(self):
        try:
            ctx = self.create_context()
            return self.task.run(ctx)
        except Exception as exc:
            self.interrupt.set()
            raise Exception(f"Exception @ Node: {self.name} -- {exc}") from exc
