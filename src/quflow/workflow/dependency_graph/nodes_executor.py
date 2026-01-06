import threading
from concurrent import futures
from ..node import NodeTypes, Node, ParallelNode
from threading import Event


def execute_multiple_nodes(nodes: list[ParallelNode]) -> None:
    """
    Executes multiple nodes concurrently, ensuring correct execution order.

    - **Main-thread node:** If exactly **one** node is marked `is_main_thread`, it runs in the main thread.
    - **Parallel execution:** All other nodes run in parallel using `ThreadPoolExecutor`.
    - **Error handling:** If multiple nodes are marked as `is_main_thread`, an assertion error is raised.

    Args:
        nodes (List[Node]): List of nodes to execute.

    Raises:
        AssertionError: If more than one node is marked as `is_main_thread`.
        Exception: If the main-thread node raises an exception.
    """
    # Creating interrupt event for all nodes and loading it
    interrupt = threading.Event()
    for n in nodes:
        n.load_interrupt(interrupt)

    # Separate main-thread and background nodes
    main_thread_nodes = list(filter(lambda x: x.run_in_main_thread, nodes))
    background_nodes = list(filter(lambda x: not x.run_in_main_thread, nodes))

    # Ensure there's at most one main-thread node
    assert len(main_thread_nodes) <= 1, "Only one node can be marked as main-thread."

    # Get the main-thread node (if it exists)
    main_thread_node: Node | None = main_thread_nodes[0] if main_thread_nodes else None

    # Execute background nodes in parallel
    with futures.ThreadPoolExecutor(max_workers=len(background_nodes)) as executor:
        future_tasks = [executor.submit(node.run) for node in background_nodes]

        # Run the main-thread node, if it exists
        if main_thread_node:
            main_thread_node.run()

            # If the main-thread node raised an exception, propagate it
            # if main_thread_node.exception is not None:
            #     raise main_thread_node.exception

        # Wait for all futures to complete
        futures.wait(future_tasks)

        # Check for exceptions in background tasks
        for future in future_tasks:
            future.result()  # Raises exception if any occurred during execution


def _execute_single(node: Node) -> None:
    """
    Executes a single node sequentially.

    Args:
        node (Node): The node to execute.
    """
    node.run()


def execute_nodes(nodes: list[ParallelNode] | Node) -> None:
    """
    Executes a list of nodes based on its length.

    - If the list is **empty**, raises a `ValueError`.
    - If the list contains **one** node, it executes it sequentially.
    - If the list contains **multiple** nodes, it distributes them across threads.

    Args:
        nodes (List[Node]): The list of nodes to execute.

    Raises:
        ValueError: If the list is empty.
        AssertionError: If more than one node is marked as `is_main_thread`.
    """
    if isinstance(nodes, list) and all(map(lambda x: isinstance(x, ParallelNode), nodes)):
        _execute_multiple(nodes)
    elif isinstance(nodes, Node):
        _execute_single(nodes)
    else:
        raise TypeError(f'Cannot recognize type of nodes: {nodes}')
