from abc import ABC, abstractmethod
from quflow.status import Status
from quflow.tasks.base.context import TaskContext




class Task(ABC):
    """
    Defined the correct interface of a TASK.
    requires implementation of a run function which gets context.
    the return of the run function has to be a status variable.

    """

    @abstractmethod
    def run(self, ctx: TaskContext) -> Status:
        pass


