from enum import Enum

class MemberStatus(Enum):
    NORMAL = "NORMAL"
    SUSPENDED = "SUSPENDED"

class Expertise(Enum):
    BASIC = "BASIC"
    ADVANCE = "ADVANCE"
    THREE_D_PRINTER = "THREE_D_PRINTER"
    LASER_CUTTER = "LASER_CUTTER"