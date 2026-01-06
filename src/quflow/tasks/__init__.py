"""
this module allows for different wrappers over the functions to handle both IO and functionalities
the main example for his is a repeated calling for the function in while loop in a thread safe manner using
shared memories
"""

from .base import Task, TaskContext
from .templates import FuncTask, GeneratorTask, ConditionPollingTask

__all__ = ['Task', 'TaskContext', 'FuncTask', 'GeneratorTask', 'ConditionPollingTask']


