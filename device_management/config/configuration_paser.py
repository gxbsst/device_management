# -*- coding: utf-8 -*-
import os, re
from xml.etree import ElementTree as ET

class ConfigPaser:
    def __init__(self):
        self.device_description_path = None

    def parseXmlFile(self, file_path):
        self.device_description_path = None
        root = ET.parse(file_path)
        return self.parseRoot(root)

    def parseXmlText(self, text):
        self.device_description_path = None
        root = ET.fromstring(text)
        return self.parseRoot(root)

    def parseRoot(self, root):
        node_device_desc = root.find("device-description")
        device_desc_path = node_device_desc.attrib.get('path')
        if device_desc_path:
            self.device_description_path = device_desc_path
