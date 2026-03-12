from itertools import count
from datetime import datetime
from enum_class import ReserveStatus, LineItemStatus

class Reservation:
    __id_counter = count(1)

    def __init__(self, owner, item_list):
        self.__reservation_id = f'RSV-{next(self.__id_counter):04d}'
        self.__owner = owner
        self.__item_list = item_list
        self.__status = ReserveStatus.CONFIRMED
    
    @property
    def get_id(self): return self.__reservation_id

    def search_item_list(self, res, start_time):
        for item in self.__item_list:
            if item.get_resource == res: return item
        return None

    def cancel(self, cancel_time=None):
        if self.__status != ReserveStatus.CONFIRMED: return None
        cancel_time = cancel_time or datetime.now()
        earliest_start = min(item.get_reserved_time.get_start_time for item in self.__item_list)
        hours_before = (earliest_start - cancel_time).total_seconds() / 3600
        for item in self.__item_list:
            item.get_resource.cancel_reserve(item.get_reserved_time)
        self.__status = ReserveStatus.CANCELLED
        if hours_before < 4: return 50
        return 0

class Invoice:
    __id_counter = count(1)

    def __init__(self, user, invoice_type, detail, cost):
        self.__invoice_id = f'INV-{next(self.__id_counter):04d}'
        self.__user = user
        self.__invoice_type = invoice_type
        self.__detail = detail
        self.__cost = cost
    
    @property
    def get_id(self): return self.__invoice_id

    @property
    def get_user(self): return self.__user

    @property
    def get_invoice_type(self): return self.__invoice_type

    @property
    def get_detail(self): return self.__detail

    @property
    def get_cost(self): return self.__cost

class Receipt:
    __id_counter = count(1)

    def __init__(self, user, invoice_type, detail, cost, change, payment_method):
        self.__receipt_id = f'REC-{next(self.__id_counter):04d}'
        self.__user = user
        self.__invoice_type = invoice_type
        self.__detail = detail
        self.__cost = cost
        self.__change = change
        self.__payment_method = payment_method

class LineItem:
    def __init__(self, resource, amount, reserved_time):
        self.__resource = resource
        self.__amount = amount
        self.__reserved_time = reserved_time
        self.__line_item_status = None
    
    @property
    def get_resource(self): return self.__resource

    @property
    def get_reserved_time(self): return self.__reserved_time

    @property
    def get_amount(self): return self.__amount

    @property
    def get_status(self): return self.__line_item_status

    @property
    def set_start_time(self): pass
    @set_start_time.setter
    def set_start_time(self, t): self.__reserved_time.set_start_time = t

    @property
    def set_end_time(self): pass
    @set_end_time.setter
    def set_end_time(self, t): self.__reserved_time.set_end_time = t
    
    def update_status(self, status: LineItemStatus): self.__line_item_status = status

    def set_actual_start_time(self, start_time):
        self.__reserved_time.set_start_time = start_time

class TimeRange:
    def __init__(self, start_time: datetime, end_time: datetime):
        self.__start_time = start_time
        self.__end_time = end_time

    @property
    def get_start_time(self): return self.__start_time
    @get_start_time.setter
    def set_start_time(self, start_time): self.__start_time = start_time

    @property
    def get_end_time(self): return self.__end_time
    @get_end_time.setter
    def set_end_time(self, end_time): self.__end_time = end_time

    def get_duration(self):
        diff = self.__end_time - self.__start_time
        duration_mins = diff.total_seconds() / 60
        return duration_mins
    
    def check_overlap(self, start_time, end_time):
        return self.__start_time < end_time and start_time < self.__end_time

class Notification:
    def __init__(self, target, topic, detail):
        self.__target = target
        self.__topic = topic
        self.__detail = detail

    @property
    def get_target(self): return self.__target
    @property
    def get_topic(self): return self.__topic
    @property
    def get_detail(self): return self.__detail