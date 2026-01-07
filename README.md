# quflow

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
[![pytest](https://img.shields.io/badge/tested%20with-pytest-blue.svg)](https://github.com/pytest-dev/pytest)

## Overview

quflow is a Python framework designed to build and orchestrate data‐processing pipelines.
Think of it as a way to create a "workflow story" where data flows from one stage to the next,
much like a production line. With quflow, you break down your process into smaller, manageable steps and
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

Whether you're building a simple sequential process or a complex, interactive real-time system, quflow provides the building blocks to create robust and maintainable data pipelines.

## Installation

To install quflow, simply run:

```bash
pip install quflow
```

## Examples
The best way to learn is by exploring our progressive examples in the `examples/` directory. Each example builds on the previous one to introduce new features and concepts:

### Example 01: Basic Sequential Pipeline (`example_01_basic_pipeline.py`)
A simple linear pipeline that connects three tasks—fetching data, post-processing, and plotting—executed in strict sequential order. Introduces the core task templates:
- **OutputFuncTask** - For source/producer functions that generate data
- **TransformFuncTask** - For processor functions that transform input to output
- **InputFuncTask** - For sink/consumer functions that process data without producing output
- **Single-item channels** - Latest value semantics for data passing

### Example 02: Parallel Polling (`example_02_parallel_polling.py`)
Demonstrates repeated task execution using **PollingTask**, a compositional wrapper that can wrap any Task instance for continuous execution. Shows how to:
- Use PollingTask to repeatedly execute tasks with stop conditions
- Run multiple tasks in parallel using **ParallelNode**
- Coordinate execution with shared stop conditions
- Handle concurrent data flow between parallel tasks

### Example 03: Generator Aggregation (`example_03_generator_aggregation.py`)
Shows streaming data patterns with **GeneratorFuncTask** and queue channels. Demonstrates:
- Generator tasks for streaming data production
- **Queue channels with batch reading** (`read_max_chunk`) for efficient processing
- Aggregation patterns for collecting streaming data
- Difference between `connect_dataflow()` (data channels) and `connect_dependency()` (execution ordering)

### Example 04: Custom Live Plot Task (`example_04_custom_live_plot.py`)
Demonstrates how to create **custom Task classes** by inheriting from the Task base class. Shows:
- Implementing the `run(ctx)` method for custom behavior
- Using `ctx.read_callable()` to read from channels in custom tasks
- Integrating matplotlib FuncAnimation for real-time visualization
- Running custom tasks in the main thread with `ParallelNode(run_in_main_thread=True)`


## Getting Started
To quickly build your own pipeline with quflow:

1. **Define Your Functions**: Write simple functions for each stage of your process (e.g., data fetching, processing, plotting).

2. **Wrap Functions in Task Templates**: Choose the appropriate task template based on your function signature:
   - `OutputFuncTask(func=your_function)` - For functions that produce data: `func() -> Any`
   - `TransformFuncTask(func=your_function)` - For functions that transform data: `func(data) -> Any`
   - `InputFuncTask(func=your_function)` - For functions that consume data: `func(data) -> None`
   - `PollingTask(task=your_task, ...)` - To wrap any task for repeated execution
   - `GeneratorFuncTask(generator_callable=your_gen)` - For streaming data sources

3. **Create Nodes**: Wrap your tasks in Nodes to control execution:
   - `Node(name, task)` - For sequential execution in main flow
   - `ParallelNode(name, task)` - For concurrent execution in separate threads

4. **Connect Nodes via Channels**: Establish data pathways using channels:
   - `create_single_item_channel()` - Latest value only (overwrites old values)
   - `create_queue_channel(read_max_chunk=N)` - Preserves all items, supports batch reading

5. **Assemble the Workflow**: Build your pipeline:
   - Add nodes with `workflow.add_node(node)`
   - Connect data flow with `workflow.connect_dataflow(source, dest, channel)`
   - Set execution order with `workflow.connect_dependency(node1, node2)` if needed

6. **Visualize & Execute**:
   - `workflow.visualize()` - View your pipeline structure
   - `workflow.execute()` - Run the complete pipeline

### Quick Example

Here's a minimal example that demonstrates the basic workflow:

```python
from quflow import (
    OutputFuncTask, TransformFuncTask, InputFuncTask,
    Node, Workflow, create_single_item_channel
)

# 1. Define your functions
def fetch_data():
    return [1, 2, 3, 4, 5]

def process_data(data):
    return [x * 2 for x in data]

def display_data(data):
    print(f"Result: {data}")

# 2. Wrap functions in task templates
fetch_task = OutputFuncTask(func=fetch_data)
process_task = TransformFuncTask(func=process_data)
display_task = InputFuncTask(func=display_data)

# 3. Create nodes
node_fetch = Node("fetch", fetch_task)
node_process = Node("process", process_task)
node_display = Node("display", display_task)

# 4. Create channels
fetch_to_process = create_single_item_channel()
process_to_display = create_single_item_channel()

# 5. Assemble workflow
workflow = Workflow()
workflow.add_node(node_fetch)
workflow.add_node(node_process)
workflow.add_node(node_display)

workflow.connect_dataflow(node_fetch, node_process, fetch_to_process)
workflow.connect_dataflow(node_process, node_display, process_to_display)

# 6. Execute
workflow.visualize()  # Optional: shows pipeline structure
workflow.execute()     # Output: Result: [2, 4, 6, 8, 10]
```

For more advanced patterns including parallel execution, polling, generators, and custom tasks, see the [examples](examples/) directory.
