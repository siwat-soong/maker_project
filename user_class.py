from datetime import datetime
from enum_class import UserRole, Expertise
from event_class import *
from enum_class import *

# User & sub class
class User:
    def __init__(self, user_id, name, tel):
        self.__user_id = user_id
        self.__name = self.__validate_input_name(name)
        self.__tel = self.__validate_input_tel(tel)
        self.__role = UserRole.GUEST
        self.__certificate_list = []
        self.__notification_list = []
        self.__reservation_list = []
        self.__receipt_list = []
        self.__line_item_list = []
        self.__unpaid_balance = 0
        self.__is_blacklist = False

    # Print Method
    def __repr__(self):
        return f"👤 User:\nID = {self.__user_id}\nNAME = {self.__name}\nTEL = {self.__tel}\n"
    
    # Input Validation
    def __validate_input_name(self, name):
        if all(char.isalpha() or char.isspace() for char in name) and name != "": return name
        else: raise ValueError("Name must be character or space")

    def __validate_input_tel(self, tel):
        if not tel.isdigit(): raise ValueError("Telephone Number must be number")
        if len(tel) != 10: raise ValueError("Telephone Number must have 10 digits")
        if tel[0] != "0": raise ValueError("Telephone Number must start with 0")
        else: return tel
    
    # Getter and Setter
    @property
    def get_id(self):
        return self.__user_id
    
    @property
    def get_name(self):
        return self.__name
    
    @property
    def get_tel(self):
        return self.__tel
    @property
    def get_max_reserve_days(self):
        if self.__role == UserRole.ANNUALMEMBER:
            return 14
        else : return 1
    def __repr__(self):
        if self.__role == UserRole.ANNUALMEMBER:
            return f"⭐ Member:\nID = {self.get_id}\nNAME = {self.get_name}\nTEL = {self.get_tel}\nSTATUS = {self.__role}\nEXPIRED DATE = {self.__expired_date}\n"
        else : return f"User not is Member"
    def update_status(self, status):
            if isinstance(status, UserRole.ANNUALMEMBER):
                self.__member_status = status
                current_date = datetime.now()
                self.__registry_date = current_date
                self.__expired_date = current_date.replace(year=current_date.year + 1)
                self.__monthly_quota = 120 # minutes
    
    def notify(self, notification):
        from transaction import Notification
        if isinstance(notification, Notification):
            self.__notification_list.append(notification)

    def join_event(self, event_id):
        pass

    def add_receipt(self, receipt):
        from transaction import Receipt
        if isinstance(receipt, Receipt):
            self.__notification_list.append(receipt)

    def add_item_list(self, line_item):
        pass

    def add_certificate(self, certificate):
        if isinstance(certificate, Certificate): self.__certificate_list.append(certificate)
        else: raise TypeError("Please add certificate only")

    def cancel_event(self, event_id):
        pass

    def list_reserve_history(self):
        pass
    
    def cancel_reservation(self, reservation_id, cancel_date_time):
        pass

    def add_to_cart(self):
        pass

    def check_blacklist(self):
        return self.__is_blacklist
    
    def check_certified(self, required_certified):
        for certificate in self.__certificate_list:
            if certificate.get_certified_topic == required_certified:
                if certificate.get_expired_date is not None and datetime.now() < certificate.get_expired_date: return True
                elif certificate is None: return True
                else: return False
        return False


    def check_in(self, reservation_id, space_id):
        pass

    def check_out(self, reservation_id, space_id):
        pass

    def pay_receipt(self, invoice_id, amount):
        pass

    def reserve(self):
        pass

    def return_resource(self, reservation_id, resource_id=None):
        pass

class Instructor(User):
    def __init__(self, user_id, name, tel, expertise, instructor_fee):
        super().__init__(user_id, name, tel)
        self.__expertise = self.__validate_input_expertise(expertise)
        self.__instructor_fee = self.__validate_input_fee(instructor_fee)

    def __repr__(self):
        return f"👨‍🏫 Instructor:\nID = {self.get_id}\nNAME = {self.get_name}\nTEL = {self.get_tel}\nEXPERTISE = {self.__expertise.value}\nINSTRUCTOR_FEE = {self.__instructor_fee}\n"

    # Input Validation
    def __validate_input_expertise(self, expertise):
        if isinstance(expertise, Expertise): return expertise
        else: raise ValueError("Expertise must be in the list")
    
    def __validate_input_fee(self, fee):
        try:
            if float(fee) >= 0: return fee
            else: raise Exception()
        except:
            raise ValueError("Fee must be positive number")

    def evaluate(self, user_id, event_id, score):
        pass

    def list_event_attender(self,  event_id):
        pass

# Admin class
class Admin:
    def __init__(self, admin_id, name, department):
        self.__admin_id = admin_id
        self.__name = self.__validate_input_name(name)
        self.__department = department

    # Input Validation
    def __validate_input_name(self, name):
        if all(char.isalpha() or char.isspace() for char in name) and name != "": return name
        else: raise ValueError("Name must be character or space")

    def force_cancel_membership(self,  user_id, reason):
        pass

    def generate_report(self):
        pass