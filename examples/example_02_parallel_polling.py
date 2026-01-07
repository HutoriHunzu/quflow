"""
Example 2: Parallel Polling Tasks

Goal:
  Demonstrate how to:
    - Use PollingTask to repeatedly execute tasks
    - Run tasks in parallel with ParallelNode
    - Use stop conditions to terminate polling

Key Concepts:
  - Compositional PollingTask design
  - Parallel execution
  - Single-item channels (latest value semantics)
  - Stop conditions

Story:
  Imagine a data acquisition pipeline where data is fetched repeatedly, processed,
  and logged. This example shows how to wrap tasks in PollingTask for repeated
  execution, run them in parallel, and stop after a fixed number of iterations.
"""

import numpy as np

from quflow import (
    OutputFuncTask,
    TransformFuncTask,
    InputFuncTask,
    PollingTask,
    ParallelNode,
    Workflow,
    create_single_item_channel
)

# Utility Functions
def fetch_data():
    """Generate noisy quadratic data on each call."""
    x = np.linspace(0, 100, 100)
    y = (x ** 2) + np.random.randn(100) * 10  # Add noise
    return x, y

def shift_data(data):
    """Apply a minor transformation: subtract a constant from y."""
    if data is None:
        return 
    x, y = data
    return x, y - 500

def print_data(data):
    """Print summary of processed data."""
    if data is None:
        return
    x, y = data
    print(f"Received data: x range [{x.min():.2f}, {x.max():.2f}], "
          f"y range [{y.min():.2f}, {y.max():.2f}]")

# Build the Workflow
def main():
    # Create channels for transferring data between nodes.
    fetch_to_shift = create_single_item_channel()
    shift_to_print = create_single_item_channel()

    # Counter for stop condition
    # Using a dictionary so the counter can be mutated inside the nested function
    iteration_count = {"count": 0}
    max_iterations = 10

    def increment_and_check():
        """Increment counter and check if we've reached max iterations.

        This is called by fetch_polling on each iteration, so it controls
        the polling loop for all tasks (since they all check the same counter).
        """
        iteration_count["count"] += 1
        return iteration_count["count"] >= max_iterations

    # Create task templates (simple function wrappers)
    fetch_task = OutputFuncTask(func=fetch_data)
    shift_task = TransformFuncTask(func=shift_data)
    print_task = InputFuncTask(func=print_data)

    # Compositional design: Wrap simple tasks in PollingTask for repeated execution.
    # PollingTask is a Decorator that wraps ANY Task instance and runs it repeatedly.
    fetch_polling = PollingTask(
        task=fetch_task,  # The task to run repeatedly
        stop_callable=increment_and_check,  # Called each iteration to check if done
        refresh_time_seconds=0.1  # Wait time between iterations
    )
    shift_polling = PollingTask(
        task=shift_task,
        stop_callable=lambda: iteration_count["count"] >= max_iterations,
        refresh_time_seconds=0.1
    )
    print_polling = PollingTask(
        task=print_task,
        stop_callable=lambda: iteration_count["count"] >= max_iterations,
        refresh_time_seconds=0.1
    )

    # ParallelNode: Runs task in a separate thread for concurrent execution.
    # This allows all three polling tasks to run simultaneously, each reading
    # and processing data as it becomes available in their input channels.
    node_fetch = ParallelNode("fetch", fetch_polling)
    node_shift = ParallelNode("shift", shift_polling)
    node_print = ParallelNode("print", print_polling)

    # Build workflow
    flow = Workflow()
    flow.add_node(node_fetch)
    flow.add_node(node_shift)
    flow.add_node(node_print)

    flow.connect_dataflow(node_fetch, node_shift, fetch_to_shift)
    flow.connect_dataflow(node_shift, node_print, shift_to_print)

    # Optionally visualize the workflow and execute it.
    flow.visualize()
    flow.execute()

    print(f"\nCompleted {iteration_count['count']} iterations")

if __name__ == '__main__':
    main()
