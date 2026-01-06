import pytest

from quflow.status import Status

# Adjust these imports if they live elsewhere in your package
from quflow.tasks import ContextFuncTask, PollingTask, Task, TaskContext, TransformFuncTask, OutputFuncTask, InputFuncTask


def test_output_func_task_writes_result_and_does_not_read(ctx_out_only):
    ctx, out_ch, read_mock = ctx_out_only

    def say_hello():
        return "hello"

    task = OutputFuncTask(func=say_hello)
    status = task.run(ctx)

    assert status == Status.FINISHED
    assert out_ch.read() == "hello"
    read_mock.assert_not_called()


def test_transform_func_task_reads_input_and_writes_output(ctx_io):
    ctx, in_ch, out_ch = ctx_io

    def double(x):
        return x * 2

    task = TransformFuncTask(func=double)

    in_ch.write(5)
    status = task.run(ctx)

    assert status == Status.FINISHED
    assert out_ch.read() == 10


def test_input_func_task_calls_func_and_does_not_write(ctx_in_only):
    ctx, in_ch, write_mock = ctx_in_only
    seen = {}

    def consume(x):
        seen["x"] = x

    task = InputFuncTask(func=consume)

    in_ch.write(7)
    status = task.run(ctx)

    assert status == Status.FINISHED
    assert seen["x"] == 7
    write_mock.assert_not_called()


def test_context_func_task_can_do_custom_io(ctx_io):
    ctx, in_ch, out_ch = ctx_io

    def logic(ctx: TaskContext):
        x = ctx.read_callable()
        ctx.write_callable(x + 1)

    task = ContextFuncTask(func=logic)

    in_ch.write(41)
    status = task.run(ctx)

    assert status == Status.FINISHED
    assert out_ch.read() == 42


def test_polling_task_runs_until_stop_condition(ctx_bare):
    ctx, _ch = ctx_bare

    class CountingTask(Task):
        def __init__(self):
            self.calls = 0

        def run(self, ctx: TaskContext) -> Status:
            self.calls += 1
            return Status.FINISHED

    wrapped = CountingTask()

    polling = PollingTask(
        task=wrapped,
        stop_callable=lambda: wrapped.calls >= 3,
        refresh_time_seconds=0.0,
    )

    status = polling.run(ctx)

    assert status == Status.FINISHED
    assert wrapped.calls == 3


def test_polling_task_propagates_non_finished_status(ctx_bare, non_finished_status):
    ctx, _ch = ctx_bare

    class BadTask(Task):
        def __init__(self):
            self.calls = 0

        def run(self, ctx: TaskContext) -> Status:
            self.calls += 1
            return non_finished_status

    wrapped = BadTask()
    polling = PollingTask(task=wrapped, refresh_time_seconds=0.0)

    status = polling.run(ctx)

    assert status == non_finished_status
    assert wrapped.calls == 1


def test_polling_task_stops_if_interrupted_before_start(ctx_bare):
    ctx, _ch = ctx_bare

    class CountingTask(Task):
        def __init__(self):
            self.calls = 0

        def run(self, ctx: TaskContext) -> Status:
            self.calls += 1
            return Status.FINISHED

    wrapped = CountingTask()
    polling = PollingTask(task=wrapped, refresh_time_seconds=0.0)

    ctx.interrupt.set()
    status = polling.run(ctx)

    assert status == Status.FINISHED
    assert wrapped.calls == 0
