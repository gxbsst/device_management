# -*- coding: utf-8 -*-
import threading
import Queue
import sys
import time

class TaskThread(threading.Thread):
    def __init__(self, name, task_queue, result_queue, interval, **kwargs):
        threading.Thread.__init__(self, name=name, kwargs=kwargs)
        self.setDaemon(True)
        self.started = False
        self.task_queue = task_queue
        self.result_queue = result_queue
        self.interval = interval # Seconds (float)
        
    def run(self):
        self.started = True
        while self.started:
            try:
                # poll one task from task_queue
                task = self.task_queue.get_nowait()

                # process one task
                status = False
                device_name = ""
                operation_name = ""
                task_results = []
                if task.canProcess():
                    status, task_results = task.process()
                    #print result, device_name, operation_name
                else:
                    status = False
                    #print task.name + " can not be processed"
                
                # put the result into the result queue (Thread-Name, ...
                result = (task.name, status, task_results)
                print result
                if self.result_queue:
                    self.result_queue.put(result)
            except Queue.Empty: # the queue is empty
                time.sleep(self.interval)# Wait until notify ??
            except:
                # TODO:
                print sys.exc_info()
                
        self.started = False
                
class TaskThreadPool:
    def __init__(self, result_queue=None, num_of_threads=1):
        self.task_queue = Queue.Queue()
        self.result_queue = result_queue
        self.threads = []
        self.__num_of_threads = num_of_threads
        self.__createThreadPool(num_of_threads)
        self.count = 0

    def __createThreadPool(self, num_of_threads):
        for i in range(num_of_threads):
            thread = TaskThread("TaskThread-"+str(i), self.task_queue, self.result_queue, 0.1)
            thread.start()
            self.threads.append(thread)

    def __waitForComplete(self):
        """
            Wait for all threads complete.
        """
        for thread in self.threads:
            # wait for threads complete
            if thread.isAlive():# invoke join when the thread is alive
                thread.join()

    def isThreadsAlive(self):
        alive_threads = filter(lambda x: x.isAlive(), self.threads)
        return alive_threads is not None and len(alive_threads) > 0

    def close(self, emergency_stop=False):
        """
            Close all threads if no task in the queue
        """
        # Stop Devices' process steps firstly (mainly blocking reading process)
        if emergency_stop:
            for thread in self.threads:
                if thread.isAlive():
                    pass
        else: # Wait for all task be executed
            while not self.task_queue.empty():
                time.sleep(0.5); # every 500 ms
        
        for thread in self.threads:
            if thread.isAlive():
                thread.started = False
        self.__waitForComplete()
        
    def addTask(self, task):
        if not self.isThreadsAlive():
            self.__createThreadPool(self.__num_of_threads)
        self.task_queue.put(task)
