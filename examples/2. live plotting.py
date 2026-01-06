"""
Example 2: Live Plotting with Parallel Tasks

Goal:
  Demonstrate how to:
    - Use ConditionPollingTask to repeatedly fetch data in parallel.
    - Use LiveAnimationTask to update a plot in real time on the main thread.

Key Concepts:
  - Parallel execution with ConditionPollingTask.
  - Live plotting using LiveAnimationTask.
  - Safe data communication using channels.

Story:
  Imagine an experimental setup where data is acquired continuously (with noise) and needs to be processed
  in real time. In this example, data fetching and shifting run in parallel, while a live plot updates on the
  main thread to provide immediate visual feedback. The workflow uses channels to safely pass data between nodes.
"""

import threading
import numpy as np
import matplotlib.pyplot as plt

from quflow import (
    FuncTask,
    LiveAnimationTask,
    ConditionPollingTask,
    Node, ParallelNode,
    Workflow,
    create_single_item_channel
)

# Utility Functions
def fetch_data():
    """Generate noisy quadratic data on each call."""
    x = np.linspace(0, 100, 100)
    y = (x ** 2) * np.random.randn(100)
    return x, y

def shift_data(data=None):
    """Apply a minor transformation: subtract a constant from y."""
    if data is None:
        return
    x, y = data
    return x, y - 500

def setup_plot():
    """Initialize a matplotlib figure and return (fig, [line, ax])."""
    fig, ax = plt.subplots()
    line, = ax.plot([], [])
    return fig, [line, ax]

def update_plot(artists, data=None):
    """Update the live plot with the latest data."""
    line, ax = artists
    if data is not None:
        x, y = data
        line.set_data(x, y)
        ax.set_xlim(x.min(), x.max())
        ax.set_ylim(y.min() - 50, y.max() + 50)
    return artists

# Build the Workflow
def main():
    # Create channels for transferring data between nodes.
    fetch_to_shift = create_single_item_channel()
    shift_to_plot  = create_single_item_channel()

    # Wrap tasks in ConditionPollingTask to run them repeatedly in parallel.
    fetch_polling = ConditionPollingTask(
        func=fetch_data,
        refresh_time_seconds=0.05
    )
    shift_polling = ConditionPollingTask(
        func=shift_data,
        refresh_time_seconds=0.05
    )

    # Create a live plot task that must run on the main thread.
    plot_task = LiveAnimationTask(
        setup_func=setup_plot,
        update=update_plot,
        refresh_time_sec=0.05,
    )

    # Create Nodes for each task.
    node_fetch = ParallelNode("fetch", fetch_polling)
    node_shift = ParallelNode("shift", shift_polling)
    node_plot  = ParallelNode("plot", plot_task, run_in_main_thread=True)

    # Build the workflow.
    flow = Workflow()
    flow.add_node(node_fetch)
    flow.add_node(node_shift)
    flow.add_node(node_plot)

    # Connect the nodes to define data flow.
    flow.connect_dataflow(node_fetch, node_shift, fetch_to_shift)
    flow.connect_dataflow(node_shift, node_plot, shift_to_plot)

    # Optionally visualize the workflow and execute it.
    flow.visualize()
    flow.execute()

if __name__ == '__main__':
    main()
