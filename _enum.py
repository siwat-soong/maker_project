from enum import Enum

class UserRole(Enum):
    GUEST = "GUEST"
    MEMBER = "MEMBER"

class InvoiceType(Enum):
    RESOURCE = "RESOURCE"
    EVENT = "EVENT"
    SUBSCRIBE = "SUBSCRIBE"
    FINE = "FINE"

class PaymentMethodType(Enum):
    CASH = "CASH"
    QRCODE = "QRCODE"

class ResourceStatus(Enum):
    AVAILABLE = "AVAILABLE"
    IN_USE = "IN_USE"
    MAINTENANCE = "MAINTENANCE"
    OUT_OF_STOCK = "OUT_OF_STOCK"

class SpaceType(Enum):
    LABORATORY = "LABORATORY"
    HOT_DESK = "HOT_DESK"
    MEETING_ROOM = "MEETING_ROOM"

class Expertise(Enum):
    ADVANCED = "ADVANCED"
    THREE_D_PRINTER = "THREE_D_PRINTER"
    LASER_CUTTER = "LASER_CUTTER"

class EquipmentType(Enum):
    THREE_D_PRINTER = "THREE_D_PRINTER"
    LASER_CUTTER = "LASER_CUTTER"
    TOOL_SET = "TOOL_SET"

class ReserveType(Enum):
    RESERVE = "RESERVE"
    INSTANT_PAY = "INSTANT_PAY"

class ReservedStatus(Enum):
    IN_CART = "IN_CART"
    CONFIRMED = "CONFIRMED"
    CHECKED_IN = "CHECKED_IN"
    COMPLETED = "COMPLETED"
    CANCELLED = "CANCELLED"

class EventStatus(Enum):
    SCHEDULED = "SCHEDULED"
    OPEN = "OPEN"
    FULL = "FULL"
    CLOSED = "CLOSED"