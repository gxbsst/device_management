# -*- coding: utf-8 -*-
from Queue import Queue
import copy

from util import UniqueNameGenerator
from task import Task
from task_thread_pool import TaskThreadPool

class TaskDispatcher:
    prefix = "Task"
    num_of_threads = 5

    def __init__(self, devices, task_results_queue):
        if devices is None or not isinstance(devices, list):
            raise Exception("devices is none or not a list")

        self.started = True
        self.devices = devices
        self.tasks = []
        self.task_name_generator = UniqueNameGenerator()
        self.task_thread_pool = TaskThreadPool(task_results_queue, 
                                               TaskDispatcher.num_of_threads)

    def createTask(self, orders):
        if orders is None or not isinstance(orders, list):
            raise Exception("orders is none or not a list")
        task_name = self.task_name_generator.getUniqueString(TaskDispatcher.prefix)
        return Task(task_name, self.devices, orders)

    def addTask(self, task):
        if not self.started or task is None:
            return
        self.tasks.append(task)
        self.task_name_generator.addString(task.name)
        self.task_thread_pool.addTask(task)
        return task

    def createAndAddTask(self, orders):
        task = self.createTask(orders)
        self.addTask(task)
        return copy.copy(task)

    def removeTask(self, task_name):
        for task in self.tasks:
            if task.name == task_name:
                # Check the task status
                if task.processing:
                    raise Exception("Task is processing, please stop it firstly")
                self.tasks.remove(task)
                return True
        return False

    def clearTasks(self):
        #TODO
        pass

    def dispatch(self):
        pass
    
    def start(self):
        self.started = True
    
    def close(self, emergency_stop=False):
        self.started = False

        # Stopping devices' blocking reading operations
        if emergency_stop:
            for device in self.devices:
                device.stopReading()

        # Close all task threads
        self.task_thread_pool.close(emergency_stop)