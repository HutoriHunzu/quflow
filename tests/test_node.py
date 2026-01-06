# import pytest
# from quflow.workflow import Node
# from quflow.tasks import Task

# class MockTask(Task):
#     def execute(self):
#         return "mock-executed"

# def test_node_run():
#     node = Node(
#         name="test-node",
#         task=MockTask(),
#     )
#     result = node.run()
#     assert result == "mock-executed", "Node should return what the task returns"
