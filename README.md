# README

## Overview

quflow is a Python framework designed to build and orchestrate data‐processing pipelines. 
Think of it as a way to create a “workflow story” where data flows from one stage to the next, 
much like a production line. In quflow Workflow, you break down your process into smaller, manageable steps and 
connect them to form a complete pipeline.

The core concepts are:

1. **Tasks**:  
   The fundamental units of work. Each task has a clear lifecycle—setup, execute, and cleanup. Tasks represent individual actions (like fetching data, processing it, or generating a plot).

2. **Nodes**:  
   Containers that wrap tasks with additional metadata (such as names) and control their execution context. Nodes determine whether a task runs in the main thread (e.g., for UI updates) or in parallel (e.g., background data processing).

3. **Channels**:  
   Mechanisms for passing data between nodes safely. For instance, a single-item channel ensures that only the most recent data item is passed from one node to the next.

4. **Workflow**:  
   The orchestrator that connects nodes, managing both the execution order and the flow of data between them. The workflow lets you define dependencies and creates a complete pipeline from individual components.

Whether you’re building a simple sequential process or a complex, interactive real-time system, quflow Workflow provides the building blocks to create robust and maintainable data pipelines.

## Installation

To install Qucraft Workflow, simply run:

```bash
pip install quflow
```

## Examples
The best way to learn is by exploring our incremental examples in the examples/ directory. Each example builds on the previous one to introduce new features and concepts:

- Basic Sequential Workflow:
A simple pipeline that connects three tasks—fetching data, post-processing, and plotting—executed in a strict linear sequence.
- Live Plotting:
This example demonstrates a real-time scenario where data is fetched and processed in parallel using ConditionPollingTask, while a LiveAnimationTask updates a plot in the main thread. It’s perfect for interactive experiments where you need immediate visual feedback.
- Multi-Read Aggregator:
In this example, a fast data-generating task streams individual data items into a queue channel. An aggregator task then reads these items in chunks (using a multi-read strategy), combines them, and passes the aggregated result to a live plotting task. This setup is ideal for handling high-frequency data while maintaining a smooth, lower-frequency live plot update.


## Getting Started
To quickly build your own pipeline with quflow Workflow:

1. Define Your Tasks: Write simple functions for each stage of your process (e.g., data fetching, processing, plotting).
2. Wrap Tasks in Nodes: Use FuncTask or other task wrappers, then create Nodes to encapsulate these tasks along with metadata.
3. Connect Nodes via Channels: Establish data pathways between nodes using channels, ensuring safe communication.
4. Assemble the Workflow: Add your nodes to a Workflow, set up the dependencies, and define the execution order.
5. Visualize & Execute: Optionally, visualize your workflow’s structure before running the entire pipeline.
