from base_plugin import BasePlugin

class DummyPlugin(BasePlugin):
    def __init(self, app):
        BasePlugin.__init__(self, app)

    def handleTaskStatus(self, *args, **kwargs):
        print "TestPlugin -> handleTaskStatus"
        print args
        print kwargs
        
    def install(self):
        self.registerTaskMessageHandler(self.handleTaskStatus)
        print "TestPlugin: Installed"

    def uninstall(self):
        self.unregisterTaskMessageHandler(self.handleTaskStatus)
        print "TestPlugin: Uninstalled"