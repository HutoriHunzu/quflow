import threading
from collections.abc import Callable

import rustworkx as rx
from rustworkx.visualization import mpl_draw

from ..graph_handler import GraphHandler, GraphTypes
from ..node import Node, NodeTypes, ParallelNode
from .nodes_executor import execute_multiple_nodes
from .sequencer import sequencer_of_nodes_and_parallel


class DependencyGraph:
    """Represents directed dependencies among Nodes.

    Internally, uses a directed acyclic graph (DAG) to
    track which Nodes must run before others. Provides
    methods to generate an execution order and run nodes
    in parallel if allowed.

    Methods:
        add_node(node): Adds a new Node into the dependency graph.
        connect_dependency(node_a, node_b): Declares that node_a must
            finish before node_b starts.
        execute(): Runs all nodes in topological order, grouping any
            parallelizable nodes together.
    """

    def __init__(self):
        self.graph: rx.PyDiGraph[NodeTypes, None] = rx.PyDiGraph()
        self.handler: GraphHandler[None] = GraphHandler(
            self.graph, GraphTypes.DEPENDENCY
        )
        self.node_index_to_execution_order: dict[int, int] = {}

    def add_node(self, node: NodeTypes):
        self.handler.add_node(node)

    def replace_node(self, old_node_name: str, new_node: NodeTypes):
        self.handler.replace_node_payload(node_name=old_node_name, new_node=new_node)

    def copy_deg_in(self, ref_node_name: str, new_node_name: str):
        self.handler.copy_deg_in(ref_node_name, new_node_name)

    def connect_dependency(self, node_a: NodeTypes, node_b: NodeTypes):
        # adding an edge
        self.handler.add_edge_by_nodes(node_a, node_b, None)

    def get_node_by_name(self, name: str) -> NodeTypes:
        idx = self.handler.node_name_to_index(name)
        return self.handler[idx]

    def nodes(self):
        return self.handler.get_all_nodes()

    def execute_parallel_nodes(self, nodes: list[ParallelNode]):
        if not nodes:
            return

        # Create Event and connect it
        interrupt = threading.Event()
        for node in nodes:
            node.load_interrupt(interrupt)

        execute_multiple_nodes(nodes)

    @staticmethod
    def execute_non_parallel_nodes(nodes: list[Node]):
        for node in nodes:
            node.run()

    def update_node_index_to_execution_order(self):
        def _helper():
            for non_parallel_nodes, parallel_nodes in sequencer_of_nodes_and_parallel(
                self.graph
            ):
                non_parallel_indexes = list(
                    map(self.handler.node_to_index, non_parallel_nodes)
                )
                parallel_indexes = list(map(self.handler.node_to_index, parallel_nodes))

                if non_parallel_indexes:
                    yield from map(lambda x: [x], non_parallel_indexes)

                if parallel_indexes:
                    yield parallel_indexes

        self.node_index_to_execution_order = {}
        for execution_order, nodes_indexes in enumerate(_helper()):
            self.node_index_to_execution_order.update(
                {idx: execution_order for idx in nodes_indexes}
            )

    def execute(self):
        for non_parallel_nodes, parallel_nodes in sequencer_of_nodes_and_parallel(
            self.graph
        ):
            self.execute_non_parallel_nodes(non_parallel_nodes)
            self.execute_parallel_nodes(parallel_nodes)

    def prepare_node_formatter(self) -> Callable[[Node], str]:
        self.update_node_index_to_execution_order()
        return self.node_display_formatter

    def node_display_formatter(self, node) -> str:
        execution_order = self.node_index_to_execution_order[
            self.handler.node_to_index(node)
        ]
        centered_order_with_format = f"{execution_order}".center(len(node.name))
        return f"{node.name}\n{centered_order_with_format}"

    def visualize(self, ax=None, pos=None):
        node_formatter = self.prepare_node_formatter()

        mpl_draw(
            self.graph,
            pos=pos,
            with_labels=True,
            labels=node_formatter,  # node data is already our annotated label
            node_size=2000,
            font_size=12,
            font_color="black",
            ax=ax,
        )

        return node_formatter
