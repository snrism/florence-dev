"""
Check Malformed OpenFlow control message
"""

import struct
import ofp
import loxi.of13.action as action

class malformed_message(object):
    #version = ofp.OFP_VERSION
    #type = 217

    def __init__(self, version=None, type=None, length=None, xid=None):
        self.version = version
        self.type = type
        self.xid = xid
	self.length = length

    def pack(self):
        packed = []
        packed.append(struct.pack("!B", self.version))
        packed.append(struct.pack("!B", self.type))
        packed.append(struct.pack("!H", 0)) # placeholder for length at index 2
        packed.append(struct.pack("!L", self.xid))
        if self.length is None:
	    self.length = sum([len(x) for x in packed])
        packed[2] = struct.pack("!H", self.length)
        return ''.join(packed)

    @staticmethod
    def unpack(buf):
        raise NotImplementedError()

    def __eq__(self, other):
        if type(self) != type(other): return False
        if self.version != other.version: return False
        if self.type != other.type: return False
        if self.xid != other.xid: return False
	if self.length != other.length: return False
        return True

    def __ne__(self, other):
        return not self.__eq__(other)

    def __str__(self):
        return self.show()

    def show(self):
        return "malformed_control_message"
