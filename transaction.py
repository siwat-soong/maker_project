from enum_class import ReserveStatus
from datetime import datetime
from resource_class import *
from enum_class import *
from event_class import *
from user_class import *
import uuid

class Reservation:
    def __init__(self, owner, due_date, fixed_id=None):
        self.__reservation_id = fixed_id if fixed_id else f"REV-{str(uuid.uuid4().int)[:10]}"
        self.__owner = self.__validate_input_owner(owner)
        self.__due_date = due_date
        self.__status = ReserveStatus.CONFIRMED
        self.__line_item_list = []
    
    def __validate_input_owner(self, owner):
        from user_class import User
        if isinstance(owner, User): return owner
        else: raise TypeError("Wrong Type")
    
    def update_status(self, status):
        if isinstance(status, ReserveStatus):
            self.__status = status
        else:
            # รับ string ได้ด้วย (เพื่อ backward compat)
            try:
                self.__status = ReserveStatus(status)
            except:
                self.__status = status
        print(f"Reservation {self.__reservation_id} status updated to: {status}")

    @property
    def get_reservation_id(self):
        return self.__reservation_id

    def force_cancel_reservation(self):
        pass

    def cancel_reservation(self, cancel_date_time):
        pass

    def list_all_match_line_item(self, resource_id):
        res = []
        try:
            for lit in self.__line_item_list:
                if lit.get_resource.get_id == resource_id:
                    res.append(lit)
        except Exception as e:
            print(f"DEBUG: Error in list_all_match_line_item: {e}")
        return res

    def calculate_total_cost(self):
        pass

    def calculate_fine(self):
        pass
    
    def add_line_item(self, item: "LineItem"):
        self.__line_item_list.append(item)

    def return_items(self, item_id: str) -> float:
        total_fee = 0.0
        current_time = datetime.now()
        
        overdue_days = 0
        if current_time > self.__due_date:
            delta = current_time - self.__due_date
            overdue_days = delta.days if delta.days > 0 else 1

        for item in self.__line_item_list:
            if item.get_resource.get_id == item_id:
                res = item.get_resource
                fee = res.calculate_fee(None, None, overdue_days)
                total_fee += fee if fee else 0.0
                res.update_status(ResourceStatus.AVAILABLE)
            
        self.__status = ReserveStatus.COMPLETED
        return total_fee
    
    def check_item(self, item_id):
        for item in self.__line_item_list:
            if item.get_resource.get_id == item_id:
                return item
        return None
    
    def pop_item(self, item):
        self.__line_item_list.remove(item)

    def check_late_return(self):
        pass


class Invoice:
    def __init__(self, user, line_item_list=None, event=None, reservation=None, payment_method=None, cost=0):
        self.__user = user
        self.__invoice_id = f"INV-{str(uuid.uuid4().int)[:10]}"
        self.__line_item_list = line_item_list
        self.__event = event
        self.__reservation = reservation
        self.__payment_method = payment_method
        self.__price = cost
        self.__paid = False

    def calculate_total_price(self):
        if self.__line_item_list is not None:
            for line_item in self.__line_item_list:
                self.__price += line_item.calculate_fee(self.__user, line_item.get_amount, None)
        if self.__event is not None:
            self.__price += self.__event.join_fee
        if self.__user.get_role == UserRole.GUEST:
            self.__price += User.MEMBER_FEE

    @property
    def user(self):
        return self.__user

    @property
    def get_id(self):
        return self.__invoice_id

    def is_purchased(self):
        return self.__paid

    def mark_as_paid(self):
        self.__paid = True

    def get_payment_method(self):
        return self.__payment_method

    def get_cost(self):
        return self.__price

    def get_reservation(self):
        return self.__reservation

    @property
    def detail(self):
        pass


class Receipt:
    def __init__(self, purchased_user, payment_method, invoice):
        from user_class import User
        from payment_class import PaymentMethod
        self.__receipt_id = f"R-{str(uuid.uuid4().int)[:10]}"
        self.__purchased_user = self.__validate_input_specific_type(purchased_user, User)
        self.__payment_method = self.__validate_input_specific_type(payment_method, PaymentMethod)
        self.__invoice = self.__validate_input_specific_type(invoice, Invoice)

    @property
    def receipt_id(self):
        return self.__receipt_id

    @property
    def purchased_user(self):
        return self.__purchased_user

    @property
    def payment_method(self):
        return self.__payment_method

    @property
    def invoice(self):
        return self.__invoice

    def __validate_input_specific_type(self, obj, obj_type, none_accepted=False):
        if none_accepted and obj is None: return None
        elif obj is not None and isinstance(obj, obj_type): return obj
        else: raise TypeError("Wrong Type")

    def get_id(self):
        return self.__receipt_id


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

    @property
    def get_amount(self):
        return self.__amount

    @property
    def get_start_date_time(self):
        return self.__start_date_time

    @property
    def get_end_date_time(self):
        return self.__end_date_time

    def __validate_input_specific_type(self, obj, obj_type):
        if isinstance(obj, obj_type): return obj
        else: raise TypeError("Wrong Type")
    
    def __validate_input_positive_number(self, number):
        try:
            if float(number) > 0: return number
            else: raise Exception()
        except: raise ValueError("Amount must greater than 0")

    def check_overlap_date_time(self, start_time, end_time):
        return not (end_time <= self.__start_date_time or start_time >= self.__end_date_time)

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
    
    def __validate_input_specific_type(self, obj, obj_type):
        if isinstance(obj, obj_type): return obj
        else: raise TypeError("Wrong Type")