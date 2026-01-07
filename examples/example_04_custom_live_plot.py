"""
Example 4: Custom Live Plotting Task

Goal:
  - Demonstrate creating a custom Task class
  - Show how to use matplotlib FuncAnimation for live plotting
  - Illustrate reading from channels within custom tasks

Key Concepts:
  - Inheriting from Task base class
  - Implementing the run(ctx) method
  - FuncAnimation for continuous plot updates
  - Running custom tasks in main thread

Story:
  Sometimes the built-in task templates aren't enough. This example shows how
  to create your own custom Task class. We create a live plotting task that
  continuously reads data from a channel and updates a matplotlib plot in real-time.
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

from quflow import (
    Task,
    TaskContext,
    OutputFuncTask,
    PollingTask,
    ParallelNode,
    Workflow,
    create_single_item_channel,
    Status
)


class LivePlotTask(Task):
    """Custom task that updates a matplotlib plot in real-time.

    This demonstrates how to create a custom Task by:
    1. Inheriting from the Task base class
    2. Implementing the run(ctx) method
    3. Using ctx.read_callable() to get data from channels
    4. Using ctx.interrupt to check for stop signals
    """

    def __init__(self, title="Live Plot"):
        self.title = title
        self.fig = None
        self.ax = None
        self.line = None
        self.animation = None

    def run(self, ctx: TaskContext) -> Status:
        """Main execution method - called by the workflow."""

        # Setup: Create the matplotlib figure and line
        self.fig, self.ax = plt.subplots()
        self.line, = self.ax.plot([], [], 'b-', linewidth=2)
        self.ax.set_xlim(0, 100)
        self.ax.set_ylim(-1000, 10000)
        self.ax.set_title(self.title)
        self.ax.set_xlabel('X')
        self.ax.set_ylabel('Y')
        self.ax.grid(True)

        def update_plot(frame):
            """Called by FuncAnimation to update the plot."""
            # Check if we should stop
            if ctx.interrupt.is_set():
                self.animation.event_source.stop()
                plt.close(self.fig)
                return self.line,

            # Read data from the channel using ctx.read_callable()
            # This is how custom tasks access data from input channels
            data = ctx.read_callable()

            # Update the plot if we got data
            if data is not None:
                x, y = data
                self.line.set_data(x, y)
                # Auto-scale if needed
                self.ax.relim()
                self.ax.autoscale_view()

            return self.line,

        # Create the animation (updates every 100ms)
        self.animation = FuncAnimation(
            self.fig,
            update_plot,
            interval=100,  # milliseconds
            blit=True
        )

        # Show the plot (blocking until closed)
        plt.show()

        # Note that we add set interrupt
        ctx.interrupt.set()

        return Status.FINISHED


# Utility function to generate data
def generate_data():
    """Generate noisy quadratic data."""
    x = np.linspace(0, 100, 100)
    y = x ** 2 + np.random.randn(100) * 100
    return x, y


def main():
    # Create channel for data flow
    # Single-item channel: Only latest data matters for live plotting
    data_to_plot = create_single_item_channel()

    # Create data generator task (polls repeatedly)
    # OutputFuncTask wraps our simple function
    data_task = OutputFuncTask(func=generate_data)

    # Wrap in PollingTask for repeated execution
    data_polling = PollingTask(
        task=data_task,
        refresh_time_seconds=0.2  # Generate data every 200ms
    )

    # Create custom live plot task
    # This is our custom Task class that we implemented above
    plot_task = LivePlotTask(title="Real-time Data Stream")

    # Create nodes
    # ParallelNode for generator (runs in background thread)
    node_data = ParallelNode("data_generator", data_polling)

    # ParallelNode with run_in_main_thread=True for plotting
    # Matplotlib requires the main thread for GUI operations
    node_plot = ParallelNode("live_plot", plot_task, run_in_main_thread=True)

    # Build workflow
    flow = Workflow()
    flow.add_node(node_data)
    flow.add_node(node_plot)

    # Connect data flow from generator to plotter
    flow.connect_dataflow(node_data, node_plot, data_to_plot)

    # Visualize and execute
    flow.visualize()
    flow.execute()


if __name__ == '__main__':
    main()
