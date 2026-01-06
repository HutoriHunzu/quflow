import pytest
from quflow.tasks import FuncTask


def test_func_task_no_input():
    # A function that doesn't need input
    def say_hello():
        return "hello"

    task = FuncTask(func=say_hello)
    result = task.run()  # Directly call the lifecycle

    assert result == "hello", "FuncTask should return the function's output"


def test_func_task_with_input():
    # A function that transforms input data
    def double(x):
        return x * 2

    task = FuncTask(func=double)
    # Simulate data from a channel
    task.connect_to_io(read_callable=lambda: 5,
                       write_callable=lambda data: None)  # no-op
    result = task.run()
    # The function itself returns the original input, but the actual
    # new data is "written" to the channel. So let's check "execute" return.
    # By default, we see in the code: 'return data' is the last line in execute()
    # which is the input from read_data (slightly confusing).
    # If we want the function's real output, we can track it in write_data:
    # but let's just confirm no crash
    assert result == 10, "FuncTask's run() returns the read input by default"
