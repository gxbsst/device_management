# -*- coding: utf-8 -*-
from abc import ABCMeta, abstractmethod
import Queue

from tasks import TaskDispatcher
from messages import MessageDispatcher
from messages import BROADCAST_MSG_TOPICS

class BaseApp:
    __metaclass__=ABCMeta
    
    def __init__(self, devices):
        self.devices = devices
        self.task_result_queue = Queue.Queue()
        self.task_dispatcher = TaskDispatcher(self.devices, self.task_result_queue)
        self.message_dispatcher = MessageDispatcher()

    def createAndAddTask(self, orders):
        new_task = self.task_dispatcher.createTask(orders)
        if new_task.canProcess():
            return self.task_dispatcher.addTask(new_task)
        raise Exception("The new task can not be executing, because the operations can NOT be found")

    def pumpTaskStatusMessage(self):
        try:
            task_result = self.task_result_queue.get_nowait()
            return task_result
        except Queue.Empty:
            pass
        return None

    def dispatchMessage(self, topic, message):
        if message is None:
            return
        self.message_dispatcher.publishAsync(topic, message)
    
    def installBroadcastMessageHandler(self, callback, front = False):
        self.subscribe(BROADCAST_MSG_TOPICS.TASK_STATUS, 
                       callback, front)
    
    def uninstallBroadcastMessageHandler(self, callback):
        self.unsubscribe(BROADCAST_MSG_TOPICS.TASK_STATUS, 
                         callback)

    def subscribe(self, topic, callback, front = False):
        self.message_dispatcher.subscribe(topic, callback, front)

    def unsubscribe(self, topic, callback):
        self.message_dispatcher.unsubscribe(topic, callback)

    def close(self):
        self.task_dispatcher.close()
        self.message_dispatcher.close()