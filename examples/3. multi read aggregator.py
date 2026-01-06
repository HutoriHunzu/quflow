"""
Example 3: Multi-Read Aggregator

Goal:
  - Demonstrate how a node can read multiple items (chunks) from a queue channel.
  - Show an aggregator task that combines all received data.
  - Optionally live-plot aggregated data at a slower refresh rate.

Key Concepts:
  - Multi-item storage using create_queue_channel (supports multi-read).
  - Aggregator pattern: Collect and combine incoming data chunks.
  - Bridging a fast data stream with slower live plotting.

Story:
  Imagine a high-speed interactive device that streams data rapidly.
  Instead of updating a plot for every individual data point, an aggregator collects data in chunks,
  processes the aggregated data, and then updates a live plot at a more manageable rate.
  This example demonstrates how to set up channels that support multi-read operations and use them
  to aggregate and visualize data.
"""

import threading
import numpy as np
import matplotlib.pyplot as plt

from quflow import (
    GeneratorTask,
    ConditionPollingTask,
    FuncTask,
    LiveAnimationTask,
    Node,
    ParallelNode,
    Workflow,
    create_queue_channel,
    create_single_item_channel
)


# Utility Functions
def generate_wave():
    """Yield a sine wave in small chunks over time (simulating a fast data stream)."""
    for val in np.linspace(0, 10 * np.pi, 500):
        yield val, np.sin(val)


class Aggregator:
    """Accumulate data in two lists: x_data and y_data."""

    def __init__(self):
        self.x_data = []
        self.y_data = []

    def append_data(self, new_chunk=None):
        """
        Append a new chunk of data (a list of (x, y) pairs) to the aggregator.
        Returns the aggregated (x_data, y_data).
        """
        if not new_chunk:
            return
        for (x, y) in new_chunk:
            self.x_data.append(x)
            self.y_data.append(y)
        return self.x_data, self.y_data


def setup_plot():
    """Initialize the matplotlib figure and return (fig, [line, ax])."""
    fig, ax = plt.subplots()
    line, = ax.plot([], [])
    return fig, [line, ax]


def update_plot(artists, data=None):
    """Update the live plot with the aggregated data."""
    line, ax = artists
    if data:
        x_vals, y_vals = data
        line.set_data(x_vals, y_vals)
        ax.set_xlim(min(x_vals), max(x_vals))
        ax.set_ylim(min(y_vals) - 0.5, max(y_vals) + 0.5)
    return artists


# Build the Workflow
def main():
    # Create an aggregator object to collect data.
    aggregator = Aggregator()

    # Create channels:
    #   - gen_to_agg: A queue channel that supports reading chunks of data.
    #   - agg_to_plot: A single-item channel for sending the aggregated data.
    gen_to_agg = create_queue_channel(read_max_chunk=10)
    agg_to_plot = create_single_item_channel()

    # Set up an interrupt event for graceful shutdown.
    stop_event = threading.Event()
    generator_is_done = threading.Event()
    aggregator_is_done = threading.Event()

    # 1) Generator Task: Simulate fast streaming data using generate_wave().
    gen_task = GeneratorTask(
        generator=generate_wave(),
        cleanup_func=generator_is_done.set
    )

    # 2) Use ConditionPollingTask so that the aggregator repeatedly polls for new data.
    agg_polling = ConditionPollingTask(
        func=aggregator.append_data,
        stop_callable=lambda: generator_is_done.is_set() and gen_to_agg.is_empty(),
        refresh_time_seconds=0.1,
        cleanup_func=aggregator_is_done.set
    )

    # 3) Live Plot Task: Update the plot in the main thread with aggregated data.
    plot_task = LiveAnimationTask(
        setup_func=setup_plot,
        update=update_plot,
        refresh_time_sec=0.1,
        stop_callable=aggregator_is_done.is_set
    )

    # Create nodes for each task.
    node_gen = ParallelNode("generator", gen_task)
    node_agg = ParallelNode("aggregator", agg_polling)
    node_plot = ParallelNode("plot", plot_task, run_in_main_thread=True)

    # Build the workflow.
    flow = Workflow()
    flow.add_node(node_gen)
    flow.add_node(node_agg)
    flow.add_node(node_plot)

    # Connect the nodes to define the data pipeline.
    flow.connect_dataflow(node_gen, node_agg, gen_to_agg)
    flow.connect_dataflow(node_agg, node_plot, agg_to_plot)

    # Optionally visualize the workflow and then execute it.
    flow.visualize()
    flow.execute()


if __name__ == '__main__':
    main()
