# tests/conftest.py
import pytest
from unittest.mock import Mock

from quflow.status import Status
from quflow.tasks.base import TaskContext

from quflow.communications.channels import (
    Channel,
    SingleReadStrategy,
    SingleWriteStrategy,
)
from quflow.communications.storage import SingleItemStorage


# ----- Channels -----


@pytest.fixture
def make_single_item_channel():
    """
    Factory fixture: returns a NEW single-item Channel each call.
    Using explicit Channel(...) keeps channel tests honest (not testing a helper).
    """

    def _make() -> Channel:
        return Channel(
            storage=SingleItemStorage(),
            read_strategy=SingleReadStrategy(),
            write_strategy=SingleWriteStrategy(),
        )

    return _make


@pytest.fixture
def single_item_channel(make_single_item_channel) -> Channel:
    """One fresh channel instance for simple tests."""
    return make_single_item_channel()


@pytest.fixture
def io_channels(make_single_item_channel):
    """(in_channel, out_channel) pair."""
    return make_single_item_channel(), make_single_item_channel()


# ----- Task contexts -----


@pytest.fixture
def ctx_io(io_channels):
    """
    (ctx, in_ch, out_ch) wired so:
      - ctx.read_callable -> in_ch.read
      - ctx.write_callable -> out_ch.write
    """
    in_ch, out_ch = io_channels
    ctx = TaskContext(read_callable=in_ch.read, write_callable=out_ch.write)
    return ctx, in_ch, out_ch


@pytest.fixture
def ctx_out_only(make_single_item_channel):
    """
    (ctx, out_ch, read_mock) for OutputFuncTask tests.
    Ensures task doesn't read.
    """
    out_ch = make_single_item_channel()
    read_mock = Mock(name="read_callable")
    ctx = TaskContext(read_callable=read_mock, write_callable=out_ch.write)
    return ctx, out_ch, read_mock


@pytest.fixture
def ctx_in_only(make_single_item_channel):
    """
    (ctx, in_ch, write_mock) for InputFuncTask tests.
    Ensures task doesn't write.
    """
    in_ch = make_single_item_channel()
    write_mock = Mock(name="write_callable")
    ctx = TaskContext(read_callable=in_ch.read, write_callable=write_mock)
    return ctx, in_ch, write_mock


@pytest.fixture
def non_finished_status():
    """Handy for PollingTask propagation tests."""
    return next(s for s in Status if s != Status.FINISHED)


@pytest.fixture
def ctx_bare(make_single_item_channel):
    """
    (ctx, ch) minimal context useful for tasks that only need ctx.interrupt
    and don't care about separate in/out wiring.
    """
    ch = make_single_item_channel()
    ctx = TaskContext(read_callable=ch.read, write_callable=ch.write)
    return ctx, ch


# ----- Aliases for nicer test ergonomics -----


@pytest.fixture
def make_channel(make_single_item_channel):
    """Alias used by channel tests."""
    return make_single_item_channel


@pytest.fixture
def channel(single_item_channel):
    """Alias used by channel tests."""
    return single_item_channel
