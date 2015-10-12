# -*- coding: utf-8 -*-
from xml.etree import ElementTree as ET

DEVICE_NAME_MAPPING = {
        1: "NC-Device-01",
        2: "NC-Device-02",
        3: "NC-Device-03",
        4: "NC-Device-04",
        5: "NC-Device-05",
        6: "NC-Device-06"
    }

ROBOT_D5_LOADING_MAPPING = {
        1:11,
        2:12,
        3:13,
        4:14,
        5:15,
        6:16
    }

ROBOT_D5_UNLOADING_MAPPING = {
        1:1,
        2:2,
        3:3,
        4:4,
        5:5,
        6:6
    }

ROBOT_D6_NC_LOCK_MAPPING = {
        1:15,
        2:25,
        3:35,
        4:45,
        5:55,
        6:65
    }

ROBOT_D6_NC_UNLOCK_MAPPING = {
        1:11,
        2:21,
        3:31,
        4:41,
        5:51,
        6:61
    }

ROBOT_D7_UNLOADING_GRAB_COMPLETE_MAPPING = {
        1:10,
        2:20,
        3:30,
        4:40,
        5:50,
        6:60        
    }

ROBOT_D7_UNLOADING_LEAVE_COMPLETE_MAPPING = {
        1:11,
        2:21,
        3:31,
        4:41,
        5:51,
        6:61        
    }

ROBOT_D7_LOADING_PLACED_COMPLETE_MAPPING = {
        1:15,
        2:25,
        3:35,
        4:45,
        5:55,
        6:65        
    }

ROBOT_D7_LOADING_LEAVED_COMPLETE_MAPPING = {
        1:16,
        2:26,
        3:36,
        4:46,
        5:56,
        6:66        
    }
    
class TcpRequestParser:
    def __init__(self):
        pass

    def genOneOrders(self, nc_device_id, program_num):
        global DEVICE_NAME_MAPPING
        global ROBOT_D5_LOADING_MAPPING
        global ROBOT_D5_UNLOADING_MAPPING
        global ROBOT_D6_NC_LOCK_MAPPING
        global ROBOT_D6_NC_UNLOCK_MAPPING
        global ROBOT_D7_UNLOADING_GRAB_COMPLETE_MAPPING
        global ROBOT_D7_UNLOADING_LEAVE_COMPLETE_MAPPING
        global ROBOT_D7_LOADING_PLACED_COMPLETE_MAPPING
        global ROBOT_D7_LOADING_LEAVED_COMPLETE_MAPPING

        nc_device_name = DEVICE_NAME_MAPPING[nc_device_id]

        return [
            # NC
            (nc_device_name, "write_program_num", {'pronum-value':[program_num]}),
            (nc_device_name, "before_unclamp", {}),
            # ROBOT
            ("Robot-Device-01", "d8_robot_status_idle", {}),
            ("Robot-Device-01", "d5_loading_prepare", {'location-no':[ROBOT_D5_LOADING_MAPPING[nc_device_id]]}),
            ("Robot-Device-01", "d7_loading_robot_placed_complete", {'location-no':[ROBOT_D7_LOADING_PLACED_COMPLETE_MAPPING[nc_device_id]]}),
            # NC
            (nc_device_name, "before_clamp", {}),
            # ROBOT
            ("Robot-Device-01", "d8_robot_status_executing", {}),
            ("Robot-Device-01", "d6_loading_nc_lock", {'location-no':[ROBOT_D6_NC_LOCK_MAPPING[nc_device_id]]}),
            ("Robot-Device-01", "d7_loading_robot_leaved_complete", {'location-no':[ROBOT_D7_LOADING_LEAVED_COMPLETE_MAPPING[nc_device_id]]}),
            # NC ###
            (nc_device_name, "execute_program", {}),
            # ROBOT
            ("Robot-Device-01", "d8_robot_status_idle", {}),
            ("Robot-Device-01", "d5_unloading_prepare", {'location-no':[ROBOT_D5_UNLOADING_MAPPING[nc_device_id]]}),
            ("Robot-Device-01", "d7_unloading_robot_grab_complete", {'location-no':[ROBOT_D7_UNLOADING_GRAB_COMPLETE_MAPPING[nc_device_id]]}),
            # NC
            (nc_device_name, "after_unclamp", {}),
            # ROBOT
            ("Robot-Device-01", "d8_robot_status_executing", {}),
            ("Robot-Device-01", "d6_unloading_nc_unlock", {'location-no':[ROBOT_D6_NC_UNLOCK_MAPPING[nc_device_id]]}),
            ("Robot-Device-01", "d7_unloading_robot_leaved_complete", {'location-no':[ROBOT_D7_UNLOADING_LEAVE_COMPLETE_MAPPING[nc_device_id]]}),
            # NC
            (nc_device_name, "after_clamp", {}),
            # ROBOT
            ("Robot-Device-01", "d8_robot_status_idle", {})
        ]

    def parseXmlText(self, text):
        answer = []
        root = ET.fromstring(text)
        node_workorder_iter = root.getiterator("workorder")
        for node_workorder in node_workorder_iter:
            device_no = eval(node_workorder.attrib.get('device'))
            program_no = eval(node_workorder.attrib.get('program_no'))
            answer.append((device_no, program_no))
        return answer
    
    def parse(self, request):
        orders = []
        info = self.parseXmlText(request)
        for device_no, program_no in info:
            for order in self.genOneOrders(device_no, program_no):
                orders.append(order)
        return orders

