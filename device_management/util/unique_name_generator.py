# -*- coding: utf-8 -*-
import re

NAME_PATTERN = re.compile(r"(.*)\-(\d+)")

class UniqueNameGenerator:
    def __init__(self):
        self.existing_strings = set()

    def addString(self, newString):
        self.existing_strings.add(newString)

    def removeString(self, rmString):
        self.existing_strings.add(rmString)

    def clear(self):
        self.existing_strings.clear()

    def getUniqueString(self, prefix):
        max_suffix_value = 0
        for cur_name in self.existing_strings:
            m = NAME_PATTERN.match(cur_name)
            if m and m.groups() and m.groups()[0] == prefix:
                max_suffix_value = max_suffix_value if max_suffix_value > int(m.groups()[1]) else int(m.groups()[1])
        return prefix + "-" + str(max_suffix_value + 1)