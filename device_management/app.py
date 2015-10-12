# -*- coding: utf-8 -*-
import os
import sys, platform, traceback
import time
import Queue
import getopt

from exception_handler import ExceptionHandler 
from drivers import ModbusDevice
from config import ConfigPaser
from config import DeviceDescriptionParser
from base_app import BaseApp
from messages.message_topics import *

#---------------------------------------------------------------------------# 
# configure the client logging
#---------------------------------------------------------------------------# 
import logging
logging.basicConfig(filename='./mj-device-management.log', filemode='a', level=logging.DEBUG, format='[%(asctime)s][%(levelname)s] %(message)s')
log = logging.getLogger()

APP_TITLE = "MJ Device Management"
APP_VERSION = '1.0'

config_file = None
if __name__ == '__main__':
    def usage():
        print "\nUsage of app.py :"
        print "\n   %s [Projectpath] [Buildpath]\n"%sys.argv[0]
    
    try:
        opts, args = getopt.getopt(sys.argv[1:], "hc:e:", ["help", "config_file=", "extend="])
    except getopt.GetoptError:
        # print help information and exit:
        usage()
        sys.exit(1)

    extensions=[]
        
    for o, a in opts:
        if o in ("-h", "--help"):
            usage()
            sys.exit()
        if o in ("-c", "--config_file"):
            config_file = a
        if o in ("-e", "--extend"):
            extensions.append(a) # TODO

def addExceptionHook(path, app_title='[No title]', app_version='[No version]'):
    m_exception_hooker = ExceptionHandler(path, app_title, app_version)
    m_exception_hooker.AddExceptHook()


def parseDeviceConfiguration(device_conf):
    answer = []
    device_descs = DeviceDescriptionParser().parseXmlFile(device_conf)
    for device_param in device_descs:
        try:
            answer.append(ModbusDevice(**device_param))
        except Exception, e:
            log.error("create ModbusDevice Error by parameters: {}\nError Info: {}".format(device_param, str(e)))
            sys.exit(1)
    return answer

class App(BaseApp):
    
    def __init__(self, devices, PluginClasses):
        print APP_TITLE + " running..."
        BaseApp.__init__(self, devices)

        self.started = False

        # Command Message Handlers
        self.cmdMessageHandlers = {
            CMD_MSG_TOPICS.NEW_TASK:[
                self.createAndAddTask
            ],
            CMD_MSG_TOPICS.SHUTDOWN:[
                self.generateShutdownMessage
            ]
        }
        self.installCmdMessageHandler()

        self.shutdown_msg = None

        # Plugins
        self.plugins = []
        # Instantiation
        if PluginClasses:
            for PluginClass in PluginClasses:
                self.plugins.append(PluginClass(self))
        self.installPlugins()        

    def installCmdMessageHandler(self):
        for cmd_topic, cmd_handlers in self.cmdMessageHandlers.items():
            if cmd_handlers is not None:
                for h in cmd_handlers:
                    self.subscribe(cmd_topic, h)
    
    def __openDevices(self):
        if self.devices is not None:
            for device in self.devices:
                status = device.connect()
                print "Device {}({}) connected {}...".format(
                    device.getDeviceName(),
                    (device.modbus_conn.client.host, device.modbus_conn.client.port),
                    "Successfully" if status else "Failed")

    def __shutdownDevices(self):
        if self.devices is not None:
            for device in self.devices:
                device.close()
    
    def generateShutdownMessage(self, *args, **kwargs):
        self.shutdown_msg = args

    def pumpShutdownMessage(self):
        return self.shutdown_msg

    def pumpMessage(self):
        message = self.pumpShutdownMessage()
        if message:
            self.shutdown_msg = None
            return CMD_MSG_TOPICS.SHUTDOWN, message

        message = self.pumpTaskStatusMessage()
        if message:
            return BROADCAST_MSG_TOPICS.TASK_STATUS, message

        return BROADCAST_MSG_TOPICS.UNKNOWN, None

    def translateMessage(self, topic, message):
        return topic, message

    def dispatchMessage(self, topic, message):
        BaseApp.dispatchMessage(self, topic, message)
        # TODO

    def close(self):
        BaseApp.close(self)

    def installPlugins(self):
        if self.plugins:
            for plugin in self.plugins:
                plugin.install()

    def uninstallPlugins(self):
        if self.plugins:
            for plugin in self.plugins:
                plugin.uninstall()

    def mainLoop(self):
        self.started = True
        try:
            self.__openDevices()
            while self.started:
                topic, message = self.pumpMessage()
                if topic == CMD_MSG_TOPICS.SHUTDOWN:
                    break

                topic, resolved_message = self.translateMessage(topic, message)
                self.dispatchMessage(topic, resolved_message)
                time.sleep(0.1) # 100 ms
        except KeyboardInterrupt, e:
            pass
        finally:
            print APP_TITLE + " ready to shutdown..."
            self.started = False
            self.close()
            self.uninstallPlugins()
            self.__shutdownDevices()

if __name__=="__main__":
    # Install a exception handle for bug reports
    addExceptionHook(os.getcwd(),APP_TITLE, APP_VERSION)

    # Global Configuration
    if not config_file: # Try find a default one
        config_file = os.path.join(os.getcwd(), "config.xml")
    config_parser = ConfigPaser()
    config_parser.parseXmlFile(config_file)

    # Device Configuration
    device_config = config_parser.device_description_path
    device_config = device_config.replace("/", os.sep)
    device_config = device_config.replace("\\", os.sep)

    devices = parseDeviceConfiguration(os.path.join(os.getcwd(), device_config))

    
    # Plugins
    from plugins import DummyPlugin
    from plugins import TcpCommucation
    PluginClasses = [TcpCommucation]

    App(devices, PluginClasses).mainLoop()