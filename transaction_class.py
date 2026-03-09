from itertools import count
from datetime import datetime
from enum_class import ReserveStatus

class Reservation:
    __id_counter = count(1)

    def __init__(self, owner, item_list):
        self.__reservation_id = f'REQ-{next(self.__id_counter):04d}'
        self.__owner = owner
        self.__item_list = item_list
        self.__status = ReserveStatus.CONFIRMED

class Invoice:
    __id_counter = count(1)

    def __init__(self, user, invoice_type, detail, cost):
        self.__invoice_id = f'INV-{next(self.__id_counter):04d}'
        self.__user = user
        self.__invoice_type = invoice_type
        self.__detail = detail
        self.__cost = cost

class Receipt:
    __id_counter = count(1)

    def __init__(self, invoice, payment_method):
        self.__receipt_id = f'REC-{next(self.__id_counter):04d}'
        self.__invoice = invoice
        self.__payment_method = payment_method

class LineItem:
    def __init__(self, resource, amount, reserved_time):
        self.__resource = resource
        self.__amount = amount
        self.__reserved_time = reserved_time

class TimeRange:
    def __init__(self, start_time: datetime, end_time: datetime):
        self.__start_time = start_time
        self.__end_time = end_time

class Notification:
    def __init__(self, target, topic, detail):
        self.__target = target
        self.__topic = topic
        self.__detail = detail