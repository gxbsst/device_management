# -*- coding: utf-8 -*-

try:
    from pymodbus.client.sync import ModbusTcpClient
    from pymodbus.transaction import ModbusSocketFramer
    from pymodbus.factory import ClientDecoder
except Exception, e:
    print "pymodbus does not seem to be installed.\nInstall it by:\npip install pymodbus"
    print e
    exit()
import time
from threading import Lock
#---------------------------------------------------------------------------# 
# configure the client logging
#---------------------------------------------------------------------------# 
import logging
logging.basicConfig(filename='./modbus_wrapper.log', filemode='a', level=logging.DEBUG, format='[%(asctime)s][%(levelname)s] %(message)s')
log = logging.getLogger()

class ModbusTcpWrapperClient():
    def __init__(self, host, port=502, device_id=0):
        """
            New modbus tcp client.
            :param host
            :type host: str
            :param port
            :type port: int
            :param device_id: 
            :type device_id: int
        """
        frame = ModbusSocketFramer(ClientDecoder())
        try:
            self.client = ModbusTcpClient(host, port, framer=ModbusSocketFramer)
        except Exception, e:
            log.error("Could not get a modbus connection to the host modbus.",
                      e)
            return
        
        self.device_id = device_id
        self.__mutex = Lock()
        self.__listener_timeout = False

    def connect(self):
        if self.client is None:
            return False
        return self.client.connect()

    def readRegisters(self, address, num_registers=1):
        """
            Reads modbus registers
            :param address: First address of the registers to read
            :type address: int
            :param num_registers: Amount of registers to read
            :type num_registers: int
        """
        tmp = None
        with self.__mutex:
            if self.client is None:
                return
         
            try:
                print "reading address ({})".format(address)
                resp = self.client.read_holding_registers(address, num_registers, unit=self.device_id)
                tmp = resp.registers
            except Exception, e:
                log.warn("Could not read on address {}. Exception: {}".format(address,str(e)))
        return tmp

    def writeRegisters(self, address, values):
        """
            Writes modbus registers
            :param address: First address of the values to write
            :type address: int
            :param values: Values to write
            :type values: list
        """
        with self.__mutex:
            if self.client is None:
                return False

            try:
                print "writing address ({}) with {}".format(address, values)
                self.client.write_registers(address, values, unit=self.device_id)
                return True
            except Exception, e:
                log.warn("Could not write values %s to address {}. Exception {}"
                         .format(str(values),address, str(e)))
            return False

    def startListeningUntilValuesFound(self, address, intended_values, interval=1.0, timeout=0.0):
        """
            Waits until these intended values found by Modbus register address
            :param address: First address of the values to read
            :type address: int
            :param intended_values: Values to match
            :type intended_values: list
            :param interval: Interval time to read in seconds
            :type interval: float
            :param timeout: Timeout for the listening in seconds(0/None = unlimited)
            :type timeout: float
        """
        if ((intended_values is None) or (not isinstance(intended_values, list))):
            log.error("Intended_values is None or not a list")
            return
        
        num_of_registers = len(intended_values)

        #start reading the modbus
        self.__stop_listener = False
        self.__listener_timeout = False
        started_time = time.time()
        while self.__stop_listener is False:
            try:
                tmp =  self.readRegisters(address, num_of_registers)
                if tmp is None:
                    time.sleep(interval)
                    continue
                
                if self.__comareList(tmp, intended_values):
                    break
                print "Intended values: {}, actual values: {}".format(intended_values, tmp)
                time.sleep(interval)
            except Exception,e:
                log.warn("Could not read holding register. Exception:{}".format(e))
                time.sleep(interval)

            # exit if timeout
            if time and (timeout > 0) and (timeout > (time() - started_time)):
                self.__listener_timeout = True
                break

        self.__listener_stopped = True

    def isListeningTimeout(self):
        return self.__listener_timeout

    def stopListening(self):
        """
            Stops the listener loop
        """
        self.__stop_listener = True

    def closeConnection(self):
        """
            Closes the connection to the modbus
        """
        if self.client is None:
            return

        self.client.close()

    def __comareList(self, list1, list2):
        if len(list1) != len(list2):
            return False
        else:
            return not (False in [(list1[i] == list2[i]) for i in range(len(list1))])