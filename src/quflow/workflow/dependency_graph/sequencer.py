from typing import Generator, Any
import rustworkx as rx

from ..node import Node, ParallelNode, NodeTypes


def topological_sequencer(
    graph: rx.PyDiGraph[Node, Any],
) -> Generator[list[Node], None, None]:
    """
    sort the graph by using topological ordering.
    yields a list of nodes
    each list of nodes can be either executed in parallel or the sequential where the order
    doesn't matter.
    the type of execution depends on the capabilities of the node which is "self.is_parallel_supported"
    """

    assert rx.is_directed_acyclic_graph(graph), "Graph contains a cycle!"

    # Perform topological sorting with batch layers
    sorter = rx.TopologicalSorter(graph, check_cycle=False)

    while sorter.is_active():
        nodes = sorter.get_ready()
        yield [graph[n] for n in nodes]
        sorter.done(nodes)


def split_to_non_parallel_and_parallel(
    nodes: list[NodeTypes],
) -> tuple[list[Node], list[ParallelNode]]:
    # split them into parallel and non-parallel

    parallel_nodes = [n for n in nodes if isinstance(n, ParallelNode)]
    non_parallel_nodes = [n for n in nodes if not isinstance(n, ParallelNode)]
    # non_parallel_nodes = list(filter(lambda x: not isinstance(x, ParallelNode), nodes))

    # first yield one by one the non-parallel part (no matter the order)
    # then yield the parallel part
    return non_parallel_nodes, parallel_nodes


def sequencer_of_nodes_and_parallel(
    graph: rx.PyDiGraph[Node, Any],
) -> Generator[tuple[list[Node], list[ParallelNode]], None, None]:
    for nodes in topological_sequencer(graph):
        yield split_to_non_parallel_and_parallel(nodes)
