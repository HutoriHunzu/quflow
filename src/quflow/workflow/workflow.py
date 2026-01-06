"""
contains a unified class to support high level methods for connecting tasks
should expose Node if wanted but maybe keep it inside

"""
from .node import NodeTypes
from .dependency_graph import DependencyGraph
from .dataflow_graph import DataFlowGraph
from .graph_handler import produce_unified_pos
from quflow.communications import Channel, create_single_item_channel
from quflow.status import Status, return_most_harsh_status

import matplotlib.pyplot as plt


class Workflow:
    """Orchestrates a pipeline of Nodes and handles their execution order.

    The Workflow maintains two graphs: a DependencyGraph for
    ordering the Nodes, and a DataFlowGraph for routing data
    through Channels. Use `add_node()`, `connect_dependency()`,
    `connect_dataflow()`, then call `execute()` to run all tasks
    in correct order (potentially in parallel).

    Example:
        flow = Workflow()
        n1 = Node("A", FuncTask(func_a))
        n2 = Node("B", FuncTask(func_b))
        flow.add_node(n1)
        flow.add_node(n2)
        flow.connect(n1, n2, create_single_item_channel())
        flow.execute()
    """

    def __init__(self):
        self.dependency_graph = DependencyGraph()
        self.data_flow_graph = DataFlowGraph()
        self.status: Status = Status.PENDING
        self._result_channel: Channel | None = None
        self._result_node: NodeTypes | None = None

    @property
    def result(self):
        if self._result_channel:
            return self._result_channel.read()

    def get_node_by_name(self, name):
        return self.dependency_graph.get_node_by_name(name)

    def configure_result_channel(self, node: NodeTypes):
        self._result_channel = create_single_item_channel()
        self._result_node = node
        self._result_node.write_channel = self._result_channel

    def add_node(self, node: NodeTypes):
        self.dependency_graph.add_node(node)
        self.data_flow_graph.add_node(node)
        return node

    def copy_dependencies(self, ref_node_name: str, new_node_name: str):
        self.dependency_graph.copy_deg_in(ref_node_name, new_node_name)

    def replace_node(self, old_node_name: str, new_node: NodeTypes):
        self.dependency_graph.replace_node(old_node_name=old_node_name, new_node=new_node)
        self.data_flow_graph.replace_node(old_node_name=old_node_name, new_node=new_node)

    def add_nodes(self, nodes: list[NodeTypes]):
        for node in nodes:
            self.add_node(node)
        return nodes

    def add_dependency_sequential_nodes(self, nodes):
        self.add_nodes(nodes)
        for i in range(len(nodes) - 1):
            self.connect_dependency(nodes[i], nodes[i + 1])
        return nodes

    def connect_dependency(self, node_a: NodeTypes, node_b: NodeTypes):
        self.dependency_graph.connect_dependency(node_a, node_b)

    def connect_dataflow(self, node_a, node_b, channel: Channel):
        self.data_flow_graph.connect_dataflow(node_a, node_b, channel)

    def connect_dataflow_by_name(self, node_a: str, node_b: str, channel: Channel):
        self.data_flow_graph.connect_dataflow_by_name(node_a, node_b, channel)


    def connect(self, node_a, node_b, channel: Channel | None = None):
        self.connect_dependency(node_a, node_b)
        if channel:
            self.connect_dataflow(node_a, node_b, channel)

    @property
    def empty(self):
        return len(self.dependency_graph.nodes()) == 0

    def validate(self):
        # checks there are nodes to run
        nodes = self.dependency_graph.nodes()
        if len(nodes) == 0:
            raise ValueError('Cannot execute Workflow without any nodes')

    def execute(self):
        self.validate()

        # setting status when we begin
        self.status = Status.RUNNING

        self.dependency_graph.execute()

        # setting the most harsh status over all the nodes
        participating_nodes = self.dependency_graph.nodes()
        self.status = return_most_harsh_status(map(lambda x: x.status, participating_nodes))

    def visualize(self):
        # computing unified position
        pos = produce_unified_pos(self.dependency_graph, self.data_flow_graph)

        # visualization of the two graphs:
        fig, axs = plt.subplots(ncols=2, figsize=(16, 10))

        node_formatter = self.dependency_graph.visualize(ax=axs[0], pos=pos)
        axs[0].set_title('Dependency graph')
        axs[0].margins(0.15)

        self.data_flow_graph.visualize(ax=axs[1], pos=pos, node_formatter=node_formatter)
        axs[1].set_title('Dataflow graph')
        axs[1].margins(0.15)

        fig.tight_layout()
        plt.show()
