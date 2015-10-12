# -*- coding: utf-8 -*-

"""
Self defined enum type

Usage:
	import enum
	ENUM_TEST = enum.intEnum("ENUM1 ENUM2 ENUM3")
    ENUM_TEST.ENUM1
    ENUM_TEST.ENUM3
"""

def intEnum(args, start=0):
    class Enum(object):
        __slots__ = args.split()
        def __init__(self):
            self.values = {}
            for i, key in enumerate(Enum.__slots__, start):
                setattr(self, key, i)
                self.values[key] = i

        def values(self):
            return Enum.__slots__
    return Enum()

def strEnum(args, start=0):
    class Enum(object):
        __slots__ = args.split()
        def __init__(self):
            for i, key in enumerate(Enum.__slots__, start):
                setattr(self, key, key)

        def values(self):
            return Enum.__slots__
    return Enum()