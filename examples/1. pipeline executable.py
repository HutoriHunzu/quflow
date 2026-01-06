"""
Example 1: Basic Sequential Workflow

Goal:
  Demonstrate a simple linear pipeline of 3 tasks:
    (1) fetch_data -> (2) post_process -> (3) plot_data

Key Concepts:
  - Working with Tasks and Nodes
  - Using a single_item_channel for data passing (only the most updated item is kept)
  - Strictly sequential execution (tasks run one after the other)

Story:
  Imagine you have a sensor that gathers data, which then needs to be post-processed before visualization.
  In this workflow, the "fetch" node acquires the data, the "post" node processes it, and the "plot" node displays it.
"""

#####################################
######### Utility Functions #########
#####################################

# Here we define the core functions that simulate our process:
# 1. fetch_data: Simulates acquiring data (for example, from a sensor).
# 2. post_process: Applies a simple transformation to the data.
# 3. plot_data: Visualizes the processed data using matplotlib.

import numpy as np
import matplotlib.pyplot as plt


def fetch_data(ctx, data = None):
    """Simulate data acquisition (e.g., from a sensor)."""
    x = np.linspace(0, 100, 100)
    y = x ** 2  # Quadratic data
    return x, y


def post_process(ctx, data):
    """Apply a simple transformation on the fetched data."""
    x, y = data
    y_shifted = y - 500  # Subtract offset
    return x, y_shifted


def plot_data(ctx, data):
    """Plot the processed data using matplotlib."""
    x, y = data
    plt.plot(x, y)
    plt.title("Basic Sequential Workflow")
    plt.show()


#####################################
############# Workflow #############
#####################################

# Next, we assemble our pipeline by creating the following building blocks:
#   1. Workflow: The container that manages execution.
#   2. Tasks (via FuncTask): Wrap our functions for standardized execution.
#   3. Nodes: Each node holds a task and can include metadata (like a name).
#   4. Channels: These handle data transfer between nodes using a single-item mechanism.
#
# The story unfolds as:
#   - The "fetch" node collects data and sends it to the "post" node.
#   - The "post" node processes the data and forwards it to the "plot" node.
#   - The "plot" node finally visualizes the result.

from quflow import (
    FuncTask,
    Node,
    Workflow,
    create_single_item_channel
)


def main():
    # Create channels for data flow between nodes.
    fetch_to_post = create_single_item_channel()
    post_to_plot = create_single_item_channel()

    # Wrap our utility functions in FuncTasks.
    fetch_task = FuncTask(func=fetch_data)
    post_task = FuncTask(func=post_process)
    plot_task = FuncTask(func=plot_data)

    # Create Nodes corresponding to each task.
    node_fetch = Node("fetch", fetch_task)
    node_post = Node("post", post_task)
    node_plot = Node("plot", plot_task)

    # Build the workflow by adding the nodes.
    flow = Workflow()
    flow.add_node(node_fetch)
    flow.add_node(node_post)
    flow.add_node(node_plot)

    # Connect the nodes with channels to define data flow.
    flow.connect(node_fetch, node_post, fetch_to_post)
    flow.connect(node_post, node_plot, post_to_plot)

    # Visualize the workflow (optional) and execute the pipeline.
    flow.visualize()
    flow.execute()


if __name__ == '__main__':
    main()
