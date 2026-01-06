from quflow.communications import Channel
from quflow.tasks import Task, TaskContext
from quflow.status import Status


def empty_read():
    pass


def empty_write(data=None):
    pass


def io_adapter(read_channel: Channel | None = None,
               write_channel: Channel | None = None):

    read_callable = read_channel.read if read_channel else empty_read
    write_callable = write_channel.write if write_channel else empty_write
    return read_callable, write_callable


class Node:
    """Wraps a Task with metadata about execution requirements.

    Attributes:
        name (str): A unique name or identifier for the node.
        task (Task): The underlying Task to run.
        is_main_thread (bool): If True, must run on the main thread
            (e.g., for GUI or matplotlib).
        is_parallel (bool): If True, can be run in parallel with other
            parallelizable nodes in the same dependency layer.

    The node automatically sets read_channel/write_channel when the
    Workflow connects it to other nodes via Channels.

    Example:
        node = Node("fetch-data", FuncTask(func=fetch_data),
                    is_main_thread=False,
                    is_parallel_supported=True)
    """

    def __init__(self, name: str, task: Task):
        self.name = name
        self.task = task
        self.read_channel: Channel | None = None
        self.write_channel: Channel | None = None
        self.appearances = {}  # graph name to index
        # self.status: Status = Status.PENDING

    def register_to_graph(self, graph_name, index: int):
        self.appearances[graph_name] = index

    def get_graph_membership_index(self, graph_name) -> int:
        return self.appearances[graph_name]

    @property
    def status(self):
        return Status.PENDING

    # def set_status(self, status_value: Status):
    #     self.status = status_value

    def create_context(self):
        read_callable, write_callable = io_adapter(self.read_channel, self.write_channel)
        return TaskContext(read_callable=read_callable, write_callable=write_callable)


    def run(self):
        ctx = self.create_context()
        return self.task.run(ctx)


