import pytest
import threading
from quflow.tasks import FuncTask, ConditionPollingTask

def test_condition_polling_task_stops():
    # We'll use an event to trigger stop_condition
    stop_event = threading.Event()

    call_count = {"count": 0}
    def increment_count(_=None):
        call_count["count"] += 1

    # Once call_count hits 3, we set the event to stop
    def stop_condition():
        return call_count["count"] >= 3

    polling_task = ConditionPollingTask(
        func=increment_count,
        stop_callable=stop_condition,
        refresh_time_seconds=0.0,  # run as fast as possible
    )

    polling_task.run()
    assert call_count["count"] == 3, "Should have run exactly 3 times then stopped."
