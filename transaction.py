from enum_class import ReserveStatus
from datetime import datetime
import uuid

class Reservation:
    ID_COUNTER = 1
    
    def __init__(self, owner, due_date):
        self.__reservation_id = f"REV-{str(uuid.uuid4().int)[:10]}"
        self.__owner = self.__validate_input_owner(owner)
        self.__due_date = due_date
        self.__status = ReserveStatus.CONFIRMED
        self.__line_item_list = []
    
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
        pass
    
    def add_line_item(self, item: LineItem):
        self.__line_item_list.append(item)

    def return_items(self, item_id: str) -> float:
        total_fee = 0.0
        current_time = datetime.now()
        
        overdue_days = 0
        if current_time > self.__due_date:
            delta = current_time - self.__due_date
            overdue_days = delta.days if delta.days > 0 else 1

        for item in self.__line_item_list:
            if item.get_resource().get_id() == item_id:
                res = item_id.get_resource()
                fee = res.calculate_fee(overdue_days)
                total_fee += fee
                res.update_status("AVAILABLE")
            
        self.__status = "COMPLETED"
        return total_fee
    
    def check_item(self, item_id):
        for item in self.__line_item_list:
            if item.get_resource().get_id() == item_id:
                return item
    
    def pop_item(self, item):
        self.__line_item_list.remove(item)

    def update_status(self, new_status: str):
        self.__status = new_status
        print(f"Reservation {self.__reservation_id} status updated to: {new_status}")

class Receipt:
    def __init__(self, purchased_user, payment_method, event, rsv, cost):
        from event_class import Event
        from user_class import User
        from payment_class import PaymentMethod
        self.__receipt_id = f"R-{str(uuid.uuid4().int)[:10]}"
        self.__purchased_user = self.__validate_input_specific_type(purchased_user, User)
        self.__payment_method = self.__validate_input_specific_type(payment_method, PaymentMethod)
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

    def get_id(self):
        return self.__receipt_id
    
    def get_payment_method(self):
        return self.__payment_method
        
    def get_cost(self):
        return self.__cost
        
    def get_reservation(self):
        return self.__rsv

class LineItem:
    def __init__(self, resource, amount, start_date_time, end_date_time):
        from resource_class import Resource
        self.__resource = self.__validate_input_specific_type(resource, Resource)
        self.__amount = self.__validate_input_positive_number(amount)
        self.__start_date_time = self.__validate_input_specific_type(start_date_time, datetime)
        self.__end_date_time = self.__validate_input_specific_type(end_date_time, datetime)

    @property
    def get_resource(self):
        return self.__resource
    
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