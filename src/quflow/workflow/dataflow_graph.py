"""
governs the connecting of communication channels in DiGraph
"""
import rustworkx as rx
from rustworkx.visualization import mpl_draw
from quflow.communications import Channel
from .node import NodeTypes
from .graph_handler import GraphHandler, GraphTypes


def default_formatter(node: NodeTypes):
    return node.name



class DataFlowGraph:
    """Stores the data flow connections among Nodes.

    Each edge in this graph associates a Channel with a
    direction: Node A -> Node B. Node A writes data to that Channel,
    and Node B reads from it. The Workflow uses this to ensure that
    tasks can read from or write to a consistent interface.

    Methods:
        add_node(node): Registers a Node in the data flow graph.
        connect_dataflow(node_a, node_b, channel): Connects node_a->node_b
            with the specified Channel (node_a writes, node_b reads).
    """

    def __init__(self):
        self.graph: rx.PyDiGraph[NodeTypes, Channel] = rx.PyDiGraph()
        self.handler: GraphHandler[Channel] = GraphHandler(self.graph, GraphTypes.DATAFLOW)

    def add_node(self, node: NodeTypes):
        self.handler.add_node(node)

    def replace_node(self, old_node_name: str, new_node: NodeTypes):
        self.handler.replace_node_payload(node_name=old_node_name, new_node=new_node)

    def connect_dataflow(self, node_a: NodeTypes, node_b: NodeTypes, channel: Channel):
        # connect a channel between two nodes: Node A --> Node B
        # Node A write channel
        # Node B read channel
        node_a.write_channel = channel
        node_b.read_channel = channel

        # adding an edge
        self.handler.add_edge_by_nodes(node_a, node_b, channel)

    def connect_dataflow_by_name(self, node_a_name: str, node_b_name: str, channel: Channel):
        node_a = self.handler.node_name_to_node[node_a_name]
        node_b = self.handler.node_name_to_node[node_b_name]
        self.connect_dataflow(node_a, node_b, channel)

    def visualize(self, ax=None, pos=None, node_formatter=None):
        non_isolated_graph = self.handler.generate_non_isolated_subgraph()

        if node_formatter is None:
            node_formatter = default_formatter

        mpl_draw(
            non_isolated_graph,
            pos=pos,
            ax=ax,
            with_labels=True,
            labels=node_formatter,  # node data is already our annotated label
            node_size=2000,
            font_size=12,
            font_color="black",
        )
