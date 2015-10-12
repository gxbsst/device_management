# -*- coding: utf-8 -*-
import re
from modbus_wrapper_client import ModbusTcpWrapperClient
#from modbus_wrapper_client_tk import ModbusTcpWrapperClient

RE_PARAM_NAME = re.compile("\{(?P<NAME>.*)\}")

'''
DeviceOperationItems = {
        "OPEN_DOOR": [{"address":4107, "values":[100], "flag":'read'},
                       {"address":4108,"values":[200], "flag":'write'},
                       {"address":4108,"values":[200], "flag":'read'}],
        "CLOSE_DOOR": [{"address":4107, "values":[100], "flag":'write'}]
    }
'''
class ModbusDevice():
    def __init__(self, device_name, operations, host, port=502, device_id=0):
        self.name = device_name
        self.modbus_conn = ModbusTcpWrapperClient(host, port, device_id)
        self.operations = operations
        self.occuping_task = None

    def connect(self):
        if self.modbus_conn is not None:
            return self.modbus_conn.connect()
    
    def getDeviceName(self):
        return self.name

    def setOccupyingTask(self, order_name):
        self.occuping_task = order_name

    def getOccupyingTask(self):
        return self.occuping_task

    def canProcess(self, operation):
        return self.operations.has_key(operation)

    def __resolve(self, value, params):
        global RE_PARAM_NAME
        if isinstance(value, str):
            m = RE_PARAM_NAME.match(value)
            if m:
                param_name = m.group("NAME")
                if (param_name is None) or \
                   (params is None) or \
                   (not params.has_key(param_name)):
                    raise Exception("The value '{}' doesn't have a coresponding key in parameters '{}'".format(
                        param_name, params))
                return params.get(param_name)
            else:
                raise Exception("The value format should be '{NAME}', but the actual is '{}".format(value))
        return value

    def process(self, operation, params=None):
        steps = self.operations.get(operation)
        if (steps == None):
            return

        response = []
        status = False
        answer = None
        for step in steps:
            status = False
            message = "Success"
            address = self.__resolve(step.get("address"), params)
            values = self.__resolve(step.get("values"), params)
            read_or_write = step.get("flag")
            timeout = step.get("timeout")

            answer = [address, values, read_or_write]
            if address is None or values is None or read_or_write is None:                
                break
            if read_or_write.upper() == "WRITE":
                if not self.writeValues(address, values):
                    message = "Error"
                    break
            elif read_or_write.upper() == "READ":
                if not self.readUntilValues(address, values, timeout):
                    if self.isReadingTimeout():
                        message = "Warning: Timeout"
                    else:
                        message = "Error: Unknown"
                    break
            else:
                message = "Flag should be 'READ' or 'WRITE', but actually it is '{}'" \
                    .format(read_or_write)
                break
            status = True
            answer = [address, values, read_or_write]
            # success
            answer.append(message)
            response.append(tuple(answer))

        if not status:
            answer.append(message)
            response.append(tuple(answer)) # Append the last one
        return (status, response)# Final_Result, Step_Results

    def writeValues(self, address, values):
        if self.modbus_conn is not None:
            return self.modbus_conn.writeRegisters(address, values)
        return False

    # Attention please !!!
    def stopReading(self):
        if self.modbus_conn is not None:
            self.modbus_conn.stopListening()

    def readUntilValues(self, address, intended_values, timeout=0.0):
        """
            Waits until the values found
            :param address: start address to match
            :type address: int
            :param intended_values: intended values to match
            :type intended_values: list
            :param timeout: Timeout for the listening in seconds(0/None = unlimited)
            :type timeout: float
        """
        if self.modbus_conn is not None:
            self.modbus_conn.startListeningUntilValuesFound(address, intended_values, 1.0, timeout)
            return True
        return False

    def isReadingTimeout(self):
        return self.modbus_conn.isListeningTimeout()

    def close(self):
        if self.modbus_conn is not None:
            self.modbus_conn.closeConnection()