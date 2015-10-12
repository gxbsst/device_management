# -*- coding: utf-8 -*-
import copy
import Queue
import time

OrderItems = [
    #("Device-01", "__DEVICE_LOCK__"),
    ("Device-01", "OPEN_DOOR"),
    ("Device-01", "CLOSE_DOOR"),
    #("Device-01", "__DEVICE_UNLOCK__")
]

class Task:
    OPERATION_LOCK = "__DEVICE_LOCK__"
    OPERATION_UNLOCK = "__DEVICE_UNLOCK__"

    def __init__(self, order_name, devices, orders):
        if devices is None or not isinstance(devices, list):
            raise Exception("devices is none or not a list")
        if orders is None or not isinstance(orders, list):
            raise Exception("orders is none or not a list")
        device_names = [d.getDeviceName() for d in devices]
        if len(device_names) != len(set(device_names)):
            raise Exception("Some device names are the same: {}".format(device_names))

        self.name = order_name
        orders_temp = copy.deepcopy(orders) # TEMP 

        self.devices = {}
        order_device_names = [v[0] for v in orders_temp]
        for device in devices:
            device_name = device.getDeviceName()
            if device_name in order_device_names:
                self.devices[device_name] = device
        if len(set(order_device_names)) != len(self.devices.keys()):
            raise Exception("Some devices in the task can NOT be found from the device list\nTask devices:{}\nDevice List:{}".format(
                str(set(order_device_names)),
                str([d.getDeviceName() for d in devices])))

        # self.orders_to_process
        self.__reorganizeOrders(orders_temp, order_device_names)
        self.orders_processed = Queue.Queue(len(orders_temp))
        
        self.processing = False

    # self.orders_to_process
    def __reorganizeOrders(self, orders, order_device_names):
        # Add LOCK & UNLOCK operations for each device
        self.orders = []
        for i, order in enumerate(orders):
            order_devices_before = order_device_names[:i]
            order_devices_after = order_device_names[i+1:]
            device_name = order_device_names[i]
            # LOCK OPERATION
            if not device_name in order_devices_before:
                self.orders.append((device_name, Task.OPERATION_LOCK, None))
            # OPERATIONS
            self.orders.append(order)
            # UNLOCK OPERATION
            if not device_name in order_devices_after:
                self.orders.append((device_name, Task.OPERATION_UNLOCK, None))

    def canProcess(self):
        for device_name, operation_name, params in self.orders:
            if operation_name in [Task.OPERATION_LOCK, Task.OPERATION_UNLOCK]:
                continue
            device = self.devices.get(device_name)
            if (device is None) or \
                (not device.canProcess(operation_name)):
                return False
        return True
    
    def __lockDevice(self, device):
        #TODO: Wait until device available
        while (device.getOccupyingTask() != None and \
                device.getOccupyingTask() != self.name): # TODO: No need '==' ?
            time.sleep(1.0)
        # LOCK 
        device.setOccupyingTask(self.name)

    def __unlockDevice(self, device):
        #Check first
        if (device.getOccupyingTask() != None and \
                device.getOccupyingTask() == self.name):
            # LOCK 
            device.setOccupyingTask(None)

    def process(self):
        self.processing = True
        step_results = []
        for device_name, operation_name, params in self.orders:
            device = self.devices.get(device_name)

            # LOCK OPERATION
            if operation_name == Task.OPERATION_LOCK:
                self.__lockDevice(device)
                continue
            
            # UNLOCK OPERATION
            if operation_name == Task.OPERATION_UNLOCK:
                self.__unlockDevice(device)
                continue

            # GENERAL OPERATION
            status, step_result = device.process(operation_name, params)

            step_results.append((device_name, operation_name, step_result))
            #task_result = (device_name, operation_name, step_results)

            if status: # SUCCESS
                self.orders_processed.put((device_name, operation_name))
            else: # ERROR, EXIT
                break
        self.processing = False
        return (status, step_results)