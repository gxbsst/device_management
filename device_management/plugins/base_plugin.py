# -*- coding: utf-8 -*-
from abc import ABCMeta, abstractmethod
from base_app import BaseApp

class BasePlugin():
    __metaclass__=ABCMeta

    def __init__(self, app):
        self.app = app

    def registerTaskMessageHandler(self, handlerCallback, front = False):
        self.app.installBroadcastMessageHandler(handlerCallback)

    def unregisterTaskMessageHandler(self, handlerCallback):
        self.app.uninstallBroadcastMessageHandler(handlerCallback)

    @abstractmethod
    def install(self):
        pass
    
    @abstractmethod
    def uninstall(self):
        pass