"""
Example 3: Generator with Queue Channel and Aggregation

Goal:
  - Demonstrate GeneratorFuncTask for streaming data
  - Show queue channels with multi-read capability
  - Implement aggregation pattern for batch processing
  - Display final aggregated results

Key Concepts:
  - GeneratorFuncTask (streaming data source)
  - Queue channels with read_max_chunk for batch reading
  - PollingTask for continuous aggregation
  - Stop conditions based on generator completion

Story:
  Imagine a high-speed data stream (like a sensor) that produces values rapidly.
  Instead of processing each value individually, we batch-read chunks from a queue,
  aggregate them, and display the final result. This demonstrates how to handle
  fast producers with slower consumers using queue channels.
"""

import threading
import numpy as np
import matplotlib.pyplot as plt

from quflow import (
    GeneratorFuncTask,
    PollingTask,
    TransformFuncTask,
    InputFuncTask,
    Node,
    ParallelNode,
    Workflow,
    create_queue_channel,
    create_single_item_channel
)


# Utility Functions
def generate_wave(ctx):
    """Yield a sine wave in small chunks over time (simulating a fast data stream)."""
    for val in np.linspace(0, 10 * np.pi, 500):
        if ctx.interrupt.is_set():
            break
        yield val, np.sin(val)


class Aggregator:
    """Accumulate data in two lists: x_data and y_data."""

    def __init__(self):
        self.x_data = []
        self.y_data = []

    def append_data(self, new_chunk):
        """Append a new chunk of data (a list of (x, y) pairs)."""
        if not new_chunk:
            return None
        for (x, y) in new_chunk:
            self.x_data.append(x)
            self.y_data.append(y)
        return self.x_data, self.y_data


def plot_final_data(data):
    """Plot the final aggregated sine wave."""
    if not data:
        print("No data to plot")
        return
    x_vals, y_vals = data
    plt.figure(figsize=(10, 6))
    plt.plot(x_vals, y_vals, 'b-', linewidth=2)
    plt.title("Aggregated Sine Wave Data")
    plt.xlabel("x")
    plt.ylabel("sin(x)")
    plt.grid(True)
    plt.show()


# Build the Workflow
def main():
    aggregator = Aggregator()

    # Create channels
    gen_to_agg = create_queue_channel(read_max_chunk=10)  # Queue for batch reading
    agg_to_plot = create_single_item_channel()            # Latest aggregated result

    # Events for coordination
    generator_is_done = threading.Event()

    # Create generator task
    gen_task = GeneratorFuncTask(generator_callable=generate_wave)

    # Create polling aggregator that reads chunks
    agg_task = TransformFuncTask(func=aggregator.append_data)
    agg_polling = PollingTask(
        task=agg_task,
        stop_callable=lambda: generator_is_done.is_set() and gen_to_agg.is_empty(),
        refresh_time_seconds=0.05
    )

    # Create final plot task (runs once at the end)
    plot_task = InputFuncTask(func=plot_final_data)

    # Create nodes
    node_gen = ParallelNode("generator", gen_task)
    node_agg = ParallelNode("aggregator", agg_polling)
    node_plot = Node("plot", plot_task)  # Sequential node, runs after aggregator

    # Build workflow
    flow = Workflow()
    flow.add_node(node_gen)
    flow.add_node(node_agg)
    flow.add_node(node_plot)

    flow.connect_dataflow(node_gen, node_agg, gen_to_agg)
    flow.connect_dataflow(node_agg, node_plot, agg_to_plot)

    # Monitor generator completion
    def check_generator_done():
        import time
        time.sleep(0.1)  # Give generator a moment to start
        while True:
            if flow.status != flow.status.RUNNING:
                break
            # Check if generator node is done
            if node_gen.status.value >= 2:  # FINISHED, STOPPED, etc.
                generator_is_done.set()
                break
            time.sleep(0.05)

    # Start monitoring thread
    monitor_thread = threading.Thread(target=check_generator_done, daemon=True)
    monitor_thread.start()

    # Visualize and execute
    flow.visualize()
    flow.execute()

    print(f"\nAggregated {len(aggregator.x_data)} data points")


if __name__ == '__main__':
    main()
