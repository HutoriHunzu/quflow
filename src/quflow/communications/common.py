from .channels import Channel, SingleReadStrategy, MultiReadStrategy, SingleWriteStrategy
from .storage import SingleItemStorage, MultiItemStorage


def create_single_item_channel() -> Channel:
    """note that max length = None is infinite"""
    storage = SingleItemStorage()
    return Channel(
        read_strategy=SingleReadStrategy(),
        write_strategy=SingleWriteStrategy(),
        storage=storage
    )


def create_queue_channel(read_max_chunk: int | None = None, maxsize: int = 0) -> Channel:
    """note that max length = None is infinite"""
    storage = MultiItemStorage(maxsize=maxsize)
    return Channel(
        read_strategy=MultiReadStrategy(chunk_size=read_max_chunk),
        write_strategy=SingleWriteStrategy(),
        storage=storage
    )
