# -*- coding: utf-8 -*-
import os, re
from xml.etree import ElementTree as ET

#from xmlclass import *
class DeviceDescriptionParser:
    def __init__(self):
        pass

    def parseXmlFile(self, file_path):
        root = ET.parse(file_path)
        return self.parseRoot(root)

    def parseXmlText(self, text):
        root = ET.fromstring(text)
        return self.parseRoot(root)

    '''
    device_name, operations, host, port=502, device_id=0
    '''
    def parseRoot(self, root):
        #node_devices = root.find('devices')
        answer = []
        node_device_iter = root.getiterator("device")
        for node_device in node_device_iter:
            #self.printNode(node_device)
            device_name = node_device.attrib.get('name')
            host = node_device.attrib.get('host')
            port = node_device.attrib.get('port')
            device_id = node_device.attrib.get('id')
            # Operations
            operations = {}
            node_operation_iter = node_device.getiterator("operation")
            for node_operation in node_operation_iter:
                operation_name = node_operation.attrib.get('name')
                register_operations = []
                node_register_oper_iter = node_operation.getiterator("register")
                for node_register in node_register_oper_iter:
                    register_address = node_register.attrib.get('address')
                    register_values = node_register.attrib.get('values')
                    register_values_tmp = eval(register_values) if not re.match("\{.*\}", register_values) else register_values
                    register_values = [register_values_tmp] if isinstance(register_values_tmp, int) or isinstance(register_values_tmp, long) else register_values_tmp
                    register_flag = node_register.attrib.get('flag')
                    register_timeout = node_register.attrib.get('timeout')
                    register_operations.append({
                            'address': eval(register_address) if not re.match("\{.*\}", register_address) else register_address,
                            'values' : register_values,
                            'flag' : register_flag,
                            'timeout' : eval(register_timeout) if register_timeout is not None else None
                        })
                operations[operation_name] = register_operations

            answer.append({
                    'device_name': device_name,
                    'operations': operations,
                    'host': host,
                    'port': eval(port),
                    'device_id': eval(device_id) if device_id is not None else 1
                })
        return answer

    def printNode(self, node):
        '''NODE INFO'''
        print "=============================================="
        print "node.attrib:%s" % node.attrib
        if node.attrib.has_key("age") > 0 :
            print "node.attrib['age']:%s" % node.attrib['age']
        print "node.tag:%s" % node.tag
        print "node.text:%s" % node.text

if __name__ == "__main__":
    path = r"C:\Users\Administrator\Desktop\device.description.xml"
    print str(DeviceDescriptionParser().parseXmlFile(path))