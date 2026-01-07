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
    InputFuncTask,
    ParallelNode,
    Workflow,
    create_queue_channel,
)

from threading import Event
from functools import partial


# Utility Functions
def generate_wave(ctx, is_done: Event):
    """Yield a sine wave in small chunks over time (simulating a fast data stream)."""
    for val in np.linspace(0, 10 * np.pi, 500):
        if ctx.interrupt.is_set():
            break
        yield val, np.sin(val)

    is_done.set()


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


def plot_final_data(x_vals, y_vals):
    """Plot the final aggregated sine wave."""
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
    # Queue channel with batch reading: Reads up to 10 items at once for efficiency.
    # Unlike single_item_channel, queue channels preserve ALL items (no drops).
    # Perfect for high-throughput producers that need all data processed.
    gen_to_agg = create_queue_channel(read_max_chunk=10)

    # Events for coordination between threads
    generator_is_done = threading.Event()

    # GeneratorFuncTask requires a callable (not a generator instance).
    # The callable receives TaskContext and returns a generator.
    # Use functools.partial to bind additional parameters (like is_done event).
    gen_task = GeneratorFuncTask(
        generator_callable=partial(generate_wave, is_done=generator_is_done)
    )

    # Create polling aggregator that reads chunks
    # The aggregator.append_data method receives a list of items (batch read)
    agg_task = InputFuncTask(func=aggregator.append_data)
    agg_polling = PollingTask(
        task=agg_task,
        stop_callable=lambda: generator_is_done.is_set() and gen_to_agg.is_empty(),
        refresh_time_seconds=0.05
    )

    # Create nodes
    node_gen = ParallelNode("generator", gen_task)
    node_agg = ParallelNode("aggregator", agg_polling)


    # Build workflow
    flow = Workflow()
    flow.add_node(node_gen)
    flow.add_node(node_agg)

    # connect_dataflow: Sets up a data channel between nodes.
    # Data flows from source node's output to destination node's input.
    flow.connect_dataflow(node_gen, node_agg, gen_to_agg)

    # Visualize and execute
    flow.visualize()
    flow.execute()

    print(f"\nAggregated {len(aggregator.x_data)} data points")
    # After it is done read the output from the aggregator channel
    plot_final_data(aggregator.x_data, aggregator.y_data)



if __name__ == '__main__':
    main()
