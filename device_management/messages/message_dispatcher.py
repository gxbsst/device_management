# -*- coding: utf-8 -*-
import threading, Queue, time

try:
    import message
except Exception, e:
    print "message does not seem to be installed.\nInstall it by:\nsudo pip install message"
    print e
    exit()
    
class MessageDispatcher:
    class MessageDispatcherThread(threading.Thread):
        def __init__(self, name, timeout=1.0, kwargs=None):
            threading.Thread.__init__(self, name=name, kwargs=kwargs)
            self.setDaemon(True)
            self.messsageQueue = Queue.Queue()
            self.started = False
            self.timeout = timeout

        def addMessageToPublish(self, topic, content):
            self.messsageQueue.put_nowait((topic,content))

        def run(self):
            self.started = True
            while self.started:
                try:
                    topic, content = self.messsageQueue.get_nowait()
                    message.pub(topic, content)
                except Queue.Empty, e:
                    time.sleep(self.timeout)

            self.started = False

    def __init__(self):
        self.message_dispatcher_thread = self.MessageDispatcherThread(
            "Message-Dispatcher-Thread")
        #self.message_dispatcher_thread.start()

    def subscribe(self, topic, callback, front = False):
        message.sub(topic, callback, front)

    def unsubscribe(self, topic, callback):
        message.unsub(topic, callback)

    def publishAsync(self, topic, content):
        self.publishSync(topic, content)
        #self.message_dispatcher_thread.addMessageToPublish(topic, content)

    def publishSync(self, topic, content):
        message.pub(topic, content)

    def close(self):
        pass
        #self.message_dispatcher_thread.start = False
        #if self.message_dispatcher_thread.isAlive():
        #    self.message_dispatcher_thread.join()