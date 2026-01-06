import pytest
from quflow.communications.channels import Channel, SingleReadStrategy, SingleWriteStrategy
from quflow.communications.storage import SingleItemStorage

def test_single_item_channel_read_write():
    storage = SingleItemStorage()
    channel = Channel(
        storage=storage,
        read_strategy=SingleReadStrategy(),
        write_strategy=SingleWriteStrategy()
    )

    assert channel.is_empty() is True, "Channel should start empty"

    channel.write(10)
    assert channel.is_empty() is False, "Should contain one item now"

    data = channel.read()
    assert data == 10, "We should retrieve the written data"
    assert channel.is_empty() is True, "Should be empty after reading once"
