from enum import Enum

class MemberStatus(Enum):
    NORMAL = "NORMAL"
    SUSPENDED = "SUSPENDED"

class Expertise(Enum):
    BASIC = "BASIC"
    ADVANCE = "ADVANCE"
    THREE_D_PRINTER = "THREE_D_PRINTER"
    LASER_CUTTER = "LASER_CUTTER"

class ResourceStatus(Enum):
    AVAILABLE = "AVAILABLE"
    IN_USE = "IN_USE"
    MAINTENANCE = "MAINTENANCE"
    OUT_OF_STOCK = "OUT_OF_STOCK"

class SpaceType(Enum):
    LABORATORY = "LABORATORY"
    HOT_DESK = "HOT_DESK"
    MEETING_ROOM = "MEETING_ROOM"

class EquipmentType(Enum):
    THREE_D_PRINTER = "THREE_D_PRINTER"
    LASER_CUTTER = "LASER_CUTTER"
    TOOL_SET = "TOOL_SET"

class EventStatus(Enum):
    SCHEDULED = "SCHEDULED"
    OPEN = "OPEN"
    FULL = "FULL"
    CLOSED = "CLOSED"

class ReserveStatus(Enum):
    CONFIRMED = "CONFIRMED"
    CHECKED_IN = "CHECKED_IN"
    COMPLETED = "COMPLETED"
    CANCELLED = "CANCELLED"