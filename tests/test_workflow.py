import pytest
from quflow.workflow import Workflow, Node
from quflow.tasks import FuncTask
from quflow.communications import create_single_item_channel


def test_simple_workflow():
    # Prepare tasks
    def produce_number():
        return 42

    def consume_number(num):
        assert num == 42
        return num + 1  # just to have an output

    # Create nodes
    prod_node = Node("producer", FuncTask(func=produce_number))
    cons_node = Node("consumer", FuncTask(func=consume_number))

    # Create channel
    channel = create_single_item_channel()

    # Build workflow
    flow = Workflow()
    flow.add_node(prod_node)
    flow.add_node(cons_node)
    flow.connect(prod_node, cons_node, channel)

    # Execute
    flow.execute()

    # If test reaches here with no AssertionError, the channel data was correct
