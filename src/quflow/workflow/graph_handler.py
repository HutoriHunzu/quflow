"""
governs the basic functionality needed from graph
"""

import rustworkx as rx
from .node import NodeTypes
from typing import TypeVar, Generic
from enum import StrEnum, auto

T = TypeVar("T")


class GraphTypes(StrEnum):
    DATAFLOW = auto()
    DEPENDENCY = auto()


class GraphHandler(Generic[T]):
    def __init__(self, graph, graph_type):
        self.type: GraphTypes = graph_type
        self.graph: rx.PyDiGraph[NodeTypes, T] = graph
        self.node_name_to_node: dict = {}

    def __getitem__(self, item: int):
        return self.graph[item]

    def add_node(self, node: NodeTypes):
        node_index = self.graph.add_node(node)
        node.register_to_graph(self.type, node_index)
        self.node_name_to_node[node.name] = node

    def remove_node(self, node_name):
        node_index = self.node_name_to_node[node_name]
        self.graph.remove_node(node_index)

    def replace_node_payload(self, node_name, new_node: NodeTypes):
        node_index = self.node_to_index(self.node_name_to_node[node_name])
        new_node.register_to_graph(self.type, node_index)
        self.graph[node_index] = new_node
        self.node_name_to_node.pop(node_name)
        self.node_name_to_node[new_node.name] = new_node

    def node_name_to_index(self, name):
        try:
            node = self.node_name_to_node[name]
        except KeyError:
            raise KeyError(f"Cannot find {name} in {self.node_name_to_node.keys()}")

        return self.node_to_index(node)

    def copy_deg_in(self, reference_node_name: str, new_node_name: str):
        ref_node_index = self.node_name_to_index(reference_node_name)
        new_node_index = self.node_name_to_index(new_node_name)
        ref_edges = self.graph.in_edges(ref_node_index)
        # change the edges to have the index of the new node
        new_edges = map(lambda x: (x[0], new_node_index, x[2]), ref_edges)
        self.graph.add_edges_from(new_edges)

    def get_all_nodes(self) -> list[NodeTypes]:
        return self.graph.nodes()

    def node_to_index(self, node):
        try:
            return node.get_graph_membership_index(self.type)
        except KeyError:
            raise KeyError(
                f"Cannot find {node.name} in graph membership, probability forgot to add node to Workflow"
            )

    def add_edge_by_nodes(self, node_a, node_b, payload):
        node_a_index = self.node_to_index(node_a)
        node_b_index = self.node_to_index(node_b)
        self.graph.add_edge(node_a_index, node_b_index, payload)

    def add_edge_by_nodes_names(self, node_a: str, node_b: str, payload):
        node_a_index = self.node_name_to_index(node_a)
        node_b_index = self.node_name_to_index(node_b)
        self.graph.add_edge(node_a_index, node_b_index, payload)

    def generate_non_isolated_subgraph(self):
        non_isolated_nodes = [
            n
            for n in self.graph.node_indices()
            if self.graph.in_degree(n) > 0 or self.graph.out_degree(n) > 0
        ]
        return self.graph.subgraph(non_isolated_nodes)


def produce_unified_pos(dependency_graph, dataflow_graph):
    # Compute a common layout.
    union_graph = dependency_graph.graph.copy()
    for edge in dataflow_graph.graph.edge_list():
        try:
            union_graph.add_edge(*edge)
        except Exception:
            pass  # Ignore duplicate edges if any

    # Compute node positions with a force-directed layout.
    # (The spring_layout algorithm uses forces between nodes; if a graph is empty,
    # the nodes would be scattered randomly.)
    return rx.spring_layout(union_graph, seed=42)
