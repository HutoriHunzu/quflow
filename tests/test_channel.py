import pytest


def test_single_item_channel_read_write(channel):
    assert channel.is_empty() is True

    channel.write(10)
    assert channel.is_empty() is False

    assert channel.read() == 10
    assert channel.is_empty() is True


@pytest.mark.parametrize(
    "setup",
    [
        pytest.param(lambda ch: None, id="read-when-empty"),
        pytest.param(lambda ch: (ch.write("x"), ch.read()), id="read-after-consume"),
    ],
)
def test_channel_read_empty_returns_none(make_channel, setup):
    ch = make_channel()
    setup(ch)

    assert ch.is_empty() is True
    assert ch.read() is None


def test_channel_write_when_full_overwrites(channel):
    channel.write(1)
    assert channel.is_empty() is False

    channel.write(2)  # allowed by current design

    # With "single slot" semantics, last write usually wins
    assert channel.read() == 2
    assert channel.is_empty() is True


def test_channel_multiple_cycles(channel):
    channel.write(10)
    assert channel.read() == 10
    assert channel.is_empty() is True

    channel.write(20)
    assert channel.read() == 20
    assert channel.is_empty() is True


def test_channel_passes_objects_through(channel):
    payload = {"a": 1, "b": [1, 2, 3]}

    channel.write(payload)
    out = channel.read()

    assert out is payload
