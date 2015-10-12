# -*- coding: utf-8 -*-
from xml.etree import ElementTree as ET

class TcpRequestParser:
    def __init__(self):
        pass

    def genOneOrders(self, action, outlet, location):

        if action == 'in':
            return [
                ("PilingCar-Device-01", "read_status_free", {}),
                ("PilingCar-Device-01", "write_in_stock", {'location': [location], 'outlet': [outlet]}),
                ("PilingCar-Device-01", "read_in_stock_work_status", {}),
                ("PilingCar-Device-01", "write_in_stock_done_status", {})
            ]
        else:
            return [
                ("PilingCar-Device-01", "read_status_free", {}),
                ("PilingCar-Device-01", "write_out_stock", {'location': [location], 'outlet': [outlet]}),
                ("PilingCar-Device-01", "read_out_stock_work_status", {}),
                ("PilingCar-Device-01", "write_out_stock_done_status", {})
            ]

        # nc_device_name = DEVICE_NAME_MAPPING[nc_device_id]
        #
        # return [
        #     # NC
        #     (nc_device_name, "write_program_num", {'pronum-value':[program_num]}),
        #     (nc_device_name, "before_unclamp", {}),
        #     # ROBOT
        #     ("Robot-Device-01", "d8_robot_status_idle", {}),
        #     ("Robot-Device-01", "d5_loading_prepare", {'location-no':[ROBOT_D5_LOADING_MAPPING[nc_device_id]]}),
        #     ("Robot-Device-01", "d7_loading_robot_placed_complete", {'location-no':[ROBOT_D7_LOADING_PLACED_COMPLETE_MAPPING[nc_device_id]]}),
        #     # NC
        #     (nc_device_name, "before_clamp", {}),
        #     # ROBOT
        #     ("Robot-Device-01", "d8_robot_status_executing", {}),
        #     ("Robot-Device-01", "d6_loading_nc_lock", {'location-no':[ROBOT_D6_NC_LOCK_MAPPING[nc_device_id]]}),
        #     ("Robot-Device-01", "d7_loading_robot_leaved_complete", {'location-no':[ROBOT_D7_LOADING_LEAVED_COMPLETE_MAPPING[nc_device_id]]}),
        #     # NC ###
        #     (nc_device_name, "execute_program", {}),
        #     # ROBOT
        #     ("Robot-Device-01", "d8_robot_status_idle", {}),
        #     ("Robot-Device-01", "d5_unloading_prepare", {'location-no':[ROBOT_D5_UNLOADING_MAPPING[nc_device_id]]}),
        #     ("Robot-Device-01", "d7_unloading_robot_grab_complete", {'location-no':[ROBOT_D7_UNLOADING_GRAB_COMPLETE_MAPPING[nc_device_id]]}),
        #     # NC
        #     (nc_device_name, "after_unclamp", {}),
        #     # ROBOT
        #     ("Robot-Device-01", "d8_robot_status_executing", {}),
        #     ("Robot-Device-01", "d6_unloading_nc_unlock", {'location-no':[ROBOT_D6_NC_UNLOCK_MAPPING[nc_device_id]]}),
        #     ("Robot-Device-01", "d7_unloading_robot_leaved_complete", {'location-no':[ROBOT_D7_UNLOADING_LEAVE_COMPLETE_MAPPING[nc_device_id]]}),
        #     # NC
        #     (nc_device_name, "after_clamp", {}),
        #     # ROBOT
        #     ("Robot-Device-01", "d8_robot_status_idle", {})
        # ]

    def parseXmlText(self, text):
        answer = []
        root = ET.fromstring(text)
        order_type = root.attrib.get('type')
        if order_type == 'transport_order':
            node_transport_order_iter = root.getiterator("order")
            for node_transport_order in node_transport_order_iter:
                action = node_transport_order.attrib.get('action')
                outlet_id = eval(node_transport_order.attrib.get('outlet_id'))
                location = eval(node_transport_order.attrib.get('location'))
                answer.append((action, outlet_id, location))
            return answer
    
    def parse(self, request):
        orders = []
        info = self.parseXmlText(request)
        for action, outlet_id, location in info:
            for order in self.genOneOrders(action, outlet_id, location):
                orders.append(order)
        return orders

