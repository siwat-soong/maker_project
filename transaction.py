from enum_class import ReserveStatus
from datetime import datetime
import uuid

class Reservation:
    ID_COUNTER = 1
    
    def __init__(self, owner, item_list):
        # self.__rsv_id = f"REV-{str(uuid.uuid4().int)[:10]}"
        self.__rsv_id = "123"
        self.__owner = self.__validate_input_owner(owner)
        self.__item_list = item_list
        self.__status = ReserveStatus.CONFIRMED
    
    @property
    def get_id(self):
        return self.__rsv_id
    
    @property
    def get_status(self):
        return self.__status
    
    def update_status(self, status):
        self.__status = status
    
    # Input Validation
    def __validate_input_owner(self, owner):
        from user_class import User
        if isinstance(owner, User): return owner
        else: raise TypeError("Wrong Type")
    
    def update_status(self, status):
        if isinstance(status, ReserveStatus): self.__status = status
        else: raise TypeError("Wrong Type")
    
    def force_cancel_reservation(self):
        pass

    def cancel_reservation(self, cancel_date_time):
        pass

    def list_all_match_line_item(self, resource_id):
        res = list()
        for lit in self.__item_list:
            if lit.get_resource.get_id == resource_id:
                res.append(lit)
        
        return res

    def calculate_total_cost(self):
        pass

    def calculate_fine(self):
        return 100
    
    def return_items(self, return_date):
        pass

    def check_late_return(self):
        pass

    def search_line_item_by_resource(self, resource):
        for item in self.__item_list:
            if item.get_resource.get_id == resource.get_id:
                return item
        return None

    def calculate_check_out_cost(self, space_lit, check_out_time, damage_item_id_list):
        
        fee = 0

        dur = space_lit.calculate_duration(check_out_time)
        fee += space_lit.calculate_overtime(check_out_time)

        for item in self.__item_list:
            rs = item.get_resource
            
            from resource_class import Equipment
            if isinstance(rs, Equipment):
                if rs.get_location.get_id == space_lit.get_resource.get_id:
                    fee += rs.calculate_fee(self.__owner, item.get_amount, dur)
                    from enum_class import ResourceStatus
                    if damage_item_id_list is not None and rs.get_id in damage_item_id_list:
                        fee += self.calculate_fine()
                        rs.update_status(ResourceStatus.MAINTENANCE)
                    else: rs.update_status(ResourceStatus.AVAILABLE)

        space = space_lit.get_resource
        fee += space.calculate_fee(self.__owner, space_lit.get_amount, dur)
        
        import math
        return math.ceil(float(fee))

class Invoice:
    def __init__(self, purchased_user, payment_method, event, rsv, cost):
        from event_class import Event
        from user_class import User
        from payment_class import PaymentMethod
        self.__inv_id = f"INV-{str(uuid.uuid4().int)[:10]}"
        self.__purchased_user = self.__validate_input_specific_type(purchased_user, User)
        self.__payment_method = self.__validate_input_specific_type(payment_method, PaymentMethod, True)
        self.__event = self.__validate_input_specific_type(event, Event, True)
        self.__rsv = self.__validate_input_specific_type(rsv, Reservation, True)
        self.__cost = self.__validate_input_positive_number(cost)
        self.__is_purchased = False
    
    # Input Validation
    def __validate_input_specific_type(self, obj, obj_type, none_accepted=False):
        if none_accepted and obj is None: return None
        elif obj is not None and isinstance(obj, obj_type): return obj
        else: raise TypeError("Wrong Type")
    
    def __validate_input_positive_number(self, number):
        try:
            if float(number) >= 0: return number
            else: raise Exception()
        except: raise ValueError("Cost below 0")

    def is_purchased(self):
        return self.__is_purchased

    def mark_as_paid(self):
        self.__is_purchased = True

class LineItem:
    def __init__(self, resource, amount, start_date_time, end_date_time):
        from resource_class import Resource
        self.__resource = self.__validate_input_specific_type(resource, Resource)
        self.__amount = self.__validate_input_positive_number(amount)
        self.__rsv_time = TimeRange(start_date_time, end_date_time)

    @property
    def get_resource(self):
        return self.__resource
    
    @property
    def get_amount(self):
        return self.__amount
    
    # Input Validation
    def __validate_input_specific_type(self, obj, obj_type):
        if isinstance(obj, obj_type): return obj
        else: raise TypeError("Wrong Type")
    
    def __validate_input_positive_number(self, number):
        try:
            if float(number) > 0: return number
            else: raise Exception()
        except: raise ValueError("Amount must greater than 0")
    
    def cancel(self, cancel_date_time):
        pass

    def calculate_sub_total(self):
        pass

    def calculate_duration(self, check_out_time):
        return self.__rsv_time.get_duration(check_out_time)
    
    def calculate_overtime(self, check_out_time):
        actual_duration = self.calculate_duration(check_out_time)
        duration = self.__rsv_time.get_duration()
        if (actual_duration.total_seconds() / 60) > (duration.total_seconds() / 60) + 15:
            return 100
        else: return 0


class Notification:
    def __init__(self, target, topic, detail):
        from user_class import User
        self.__target = self.__validate_input_specific_type(target, User)
        self.__topic = topic
        self.__detail = detail
    
    # Input Validation
    def __validate_input_specific_type(self, obj, obj_type):
        if isinstance(obj, obj_type): return obj
        else: raise TypeError("Wrong Type")

class TimeRange:
    def __init__(self, start_time: datetime, end_time: datetime):
        if start_time > end_time: raise Exception()
        self.__start_time = start_time
        self.__end_time = end_time
    
    def get_duration(self, end_time: datetime=None):
        if end_time is None: return self.__end_time - self.__start_time
        else: return end_time - self.__start_time
    
    def check_overlap(self, start_time: datetime, end_time: datetime):
        if (self.__start_time <= start_time <= self.__end_time): return True
        elif (self.__start_time <= end_time <= self.__end_time): return True
        elif (start_time < self.__start_time and end_time > self.__end_time): return True
        else: return False