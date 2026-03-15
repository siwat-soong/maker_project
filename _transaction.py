from itertools import count
from _enum import InvoiceType, ReservedStatus, ResourceStatus
from datetime import datetime

class Reservation:
    __id_counter = count(1)

    def __init__(self, owner, item_list):
        self.__reservation_id = f'RSV-{next(self.__id_counter):04d}'
        self.__owner = owner
        self.__item_list = item_list
    
    @property
    def get_id(self): return self.__reservation_id

    @property
    def get_items(self): return self.__item_list
    
    def detail(self): return {
        "ID": self.__reservation_id,
        "OWNER": self.__owner.get_id,
        "ITEMS": [x.detail() for x in self.__item_list]
    }

    def cancel(self, res, start_time):
        item_to_cancel = []
        if res is None: return [x for x in self.__item_list if x.get__status == ReservedStatus.CONFIRMED]
        else:
            res_to_check = [res.get_id]
            if hasattr(res, "get_eq"): res_to_check.extend([eq.get_id for eq in res.get_eq])
            for item in self.__item_list:
                if item.check_matching(res_to_check, start_time) and item.get_status == ReservedStatus.CONFIRMED: item_to_cancel.append(item)
        return item_to_cancel
    
    def check_in(self, res, start_time):
        item_to_ci = []
        if res.get_status == ResourceStatus.IN_USE: raise Exception("อุปกรณ์ถูกใช้งานอยู่ กรุณาเช็คเอ้าท์ก่อน")
        res_to_check = [res.get_id]
        if hasattr(res, "get_eq"): res_to_check.extend([eq.get_id for eq in res.get_eq])
        for item in self.__item_list:
            if item.check_matching(res_to_check, start_time) and item.get_status == ReservedStatus.CONFIRMED: item_to_ci.append(item)
        return item_to_ci
    
    def check_out(self, res):
        item_to_co = []
        res_to_check = [res.get_id]
        if hasattr(res, "get_eq"): res_to_check.extend([eq.get_id for eq in res.get_eq])
        for item in self.__item_list:
            if item.check_matching(res_to_check, None) and item.get_status == ReservedStatus.CHECKED_IN: item_to_co.append(item)
        return item_to_co

class ReserveSlot:
    def __init__(self, resource, amount: float, reserved_time):
        self.__resource = resource
        self.__amount = amount
        self.__reserved_time = reserved_time
        self.__status = ReservedStatus.IN_CART

    @property
    def get_resource(self): return self.__resource

    @property
    def get_amount(self): return self.__amount

    @property
    def get_time(self): return self.__reserved_time
    @get_time.setter
    def set_time(self, time): self.__reserved_time = time

    @property
    def get_status(self): return self.__status
    
    def add_amount(self, amount):
        self.__amount += amount
    
    def detail(self): return {
        "RESOURCE": self.__resource.get_id,
        "AMOUNT": self.__amount,
        "START": self.__reserved_time.get_start_time.strftime("%d-%m-%Y %H:%M") if self.__reserved_time is not None else None,
        "END": self.__reserved_time.get_end_time.strftime("%d-%m-%Y %H:%M") if self.__reserved_time is not None else None,
        "STATUS": self.__status
    }

    def check_duplicate(self, slot):
        if slot.get_resource == self.__resource:
            if slot.get_time is not None and not self.__reserved_time.check_overlap(slot.get_time.get_start_time, slot.get_time.get_end_time): return False
            return True
        return False
    
    def check_matching(self, res_id, start_time):
        if self.__resource.get_id in res_id:
            if start_time and self.__reserved_time.get_start_time != start_time: return False
            return True
    
    def reserve(self):
        self.__status = ReservedStatus.CONFIRMED
        self.__resource.add_schedule(self.__reserved_time)
    
    def check_in(self):
        self.__status = ReservedStatus.CHECKED_IN
        self.__resource.update_status(ResourceStatus.IN_USE)
    
    def check_out(self, user, check_out_time):
        dur = check_out_time - self.__reserved_time.get_start_time
        diff = self.__reserved_time.get_end_time - check_out_time
        if diff.total_seconds() / 60 < 0: cost = int(diff.total_seconds() / 60) * -10
        else: cost = 0 
        cost += self.__resource.calculate_fee(user, self.__amount, dur.total_seconds() / 60)

        self.__status = ReservedStatus.COMPLETED
        self.__resource.update_status(ResourceStatus.AVAILABLE)
        return cost
    
    def cancel(self) -> float:
        self.__resource.remove_schedule(self.__reserved_time)
        self.__status = ReservedStatus.CANCELLED
        now = datetime.now()
        if now > self.__reserved_time.get_start_time: return 200
        diff = self.__reserved_time.get_start_time - now
        if diff.total_seconds() / 3600 > 4: return 100
        return 0
    
    def update_status(self, status): self.__status = status

class Invoice:
    __id_counter = count(1)
    def __init__(self, user, type: InvoiceType, detail, cost: float):
        self.__inv_id = f'INV-{next(self.__id_counter):04d}'
        self.__user = user
        self.__type = type
        self.__detail = detail
        self.__cost = cost
    
    @property
    def get_id(self): return self.__inv_id

    @property
    def get_type(self): return self.__type

    @property
    def get_cost(self): return self.__cost

    @property
    def get_detail(self): return self.__detail
    
    def detail(self): return {
        "ID": self.__inv_id,
        "USER": self.__user.get_id,
        "TYPE": self.__type,
        "DETAILS": self.__detail,
        "COST": self.__cost
    }

class Receipt:
    __id_counter = count(1)
    def __init__(self, user, inv_id: str, type: InvoiceType, detail, total: float, purchased: float, change: float):
        self.__user_id = user.get_id
        self.__receipt_id = f"REC-{next(self.__id_counter):04d}"
        self.__purchased_time = datetime.now().strftime("%d-%m-%Y %H:%M")
        self.__inv_id = inv_id
        self.__item_type = type
        self.__detail = detail
        self.__total = total
        self.__purchased = purchased
        self.__change = change
    
    def detail(self): return {
        "CUSTOMER": self.__user_id,
        "REC ID": self.__receipt_id,
        "TIME": self.__purchased_time,
        "INV ID": self.__inv_id,
        "TOPIC": self.__item_type,
        "DETAILS": self.__detail,
        "TOTAL": "$" + str(self.__total),
        "PURCHASED": "$" + str(self.__purchased),
        "CHANGE": "$" + str(self.__change)
    }

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
    def __init__(self, target, topic: str, detail: str):
        self.__target = target
        self.__topic = topic
        self.__detail = detail
    
    def detail(self): return {
        "TOPIC": self.__topic,
        "DETAIL": self.__detail
    }