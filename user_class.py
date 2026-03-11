from enum_class import UserRole
from datetime import datetime, timedelta

class User:
    def __init__(self, user_id, name, tel):
        # Basic Info
        self.__user_id = user_id
        self.__name = self.__validate_input_name(name)
        self.__tel = self.__validate_input_tel(tel)
        self.__role = UserRole.GUEST
        self.__expired_date = datetime.now()
        self.__max_reserve_days = 1
        self.__is_blacklist = False
        self.__discount = 0

        # Storage
        self.__certificate_list = []
        self.__reservation_list = []
        self.__line_item_list = []
        self.__invoice_list = []
        self.__receipt_list = []
        self.__notification_list = []

    def __validate_input_name(self, name):
        if all(char.isalpha() or char.isspace() for char in name) and name != "": return name
        else: raise ValueError("Name must be character or space")

    def __validate_input_tel(self, tel):
        if not tel.isdigit(): raise ValueError("Telephone Number must be number")
        if len(tel) != 10: raise ValueError("Telephone Number must have 10 digits")
        if tel[0] != "0": raise ValueError("Telephone Number must start with 0")
        return tel
    
    @property
    def get_id(self): return self.__user_id
    
    @property
    def get_name(self): return self.__name

    @property
    def get_expired_date(self): return self.__expired_date

    @property
    def get_max_reserve_days(self): return self.__max_reserve_days

    @property
    def get_line_item(self): return self.__line_item_list

    @property
    def get_discount(self): return self.__discount

    @property
    def get_reservation_list(self): return self.__reservation_list

    def show_info(self): 
        return {
            "UID": self.__user_id,
            "NAME": self.__name,
            "TEL": self.__tel,
            "ROLE": self.__role,
            "EXPIRED-DATE": self.__expired_date,
            "MAX-RESERVE-DAYS": self.__max_reserve_days,
            "BLACKLIST": self.__is_blacklist
        }

    def show_notification(self):
        return [
            {
                "topic": n.get_topic,
                "detail": n.get_detail
            }
            for n in self.__notification_list
        ]

    def add_certificate(self, certificate): self.__certificate_list.append(certificate)
    def add_reservation(self, reservation): self.__reservation_list.append(reservation)
    def add_invoice(self, invoice): self.__invoice_list.append(invoice)
    def add_receipt(self, receipt): self.__receipt_list.append(receipt)
    def add_notification(self, notification): self.__notification_list.append(notification)

    def search_invoice_by_id(self, inv_id):
        for inv in self.__invoice_list:
            if inv.get_id == inv_id: return inv
        return None

    def search_reservation_by_id(self, rsv_id):
        for rsv in self.__reservation_list:
            if rsv.get_id == rsv_id: return rsv
        return None

    def check_blacklist(self): return self.__is_blacklist

    def check_invoice(self): return len(self.__invoice_list) > 0

    def check_expertise(self, resource):
        if not self.__certificate_list:
            if resource.check_expertise(None): return True
            else: return False
        for cert in self.__certificate_list:
            if resource.check_expertise(cert.get_expertise): return True
        return False

    def update_role(self, role: UserRole): self.__role = role

    def subscribe(self):
        self.__expired_date = datetime.now() + timedelta(days=365)

    def activate_membership(self):
        self.__role = UserRole.MEMBER
        self.__max_reserve_days = 14
        self.__discount = 0.2
    
    def create_invoice(self, invoice_type, detail, cost):
        from transaction_class import Invoice
        inv = Invoice(self, invoice_type, detail, cost)
        self.add_invoice(inv)
        return inv
    
    def create_receipt(self, inv, change, method):
        from transaction_class import Receipt
        rec = Receipt(inv.get_user, inv.get_invoice_type, inv.get_detail, inv.get_cost, change, type(method))
        self.add_receipt(rec)
        del_inv = self.search_invoice_by_id(inv.get_id)
        self.__invoice_list.remove(del_inv)
    
    def add_to_cart(self, res, amount, start_time, end_time):
        from transaction_class import LineItem, TimeRange
        lit = list(res.create_line_item(amount, TimeRange(start_time, end_time)))
        self.__line_item_list.extend(lit)
    
    def check_duplicate_cart(self, res, start_time, end_time):
        from resource_class import Space, Material
        for lit in self.__line_item_list:
            lit_res = lit.get_resource
            if not isinstance(lit_res, (Space, Material)): continue
            if lit_res == res and lit.get_reserved_time.check_overlap(start_time, end_time): return True
        return False

    def clear_line_item(self): self.__line_item_list.clear()

    def remove_invoice(self, inv):
        if inv in self.__invoice_list:
            self.__invoice_list.remove(inv)

class Instructor(User):
    def __init__(self, user_id, name, tel, expertise, instructor_fee: float):
        super().__init__(user_id, name, tel)
        self.update_role(UserRole.MEMBER)
        self.__expertise = expertise
        self.__instructor_fee = float(instructor_fee)
        self.__schedule = []
    
    @property
    def get_expertise(self): return self.__expertise
    
    @property
    def get_fee(self): return self.__instructor_fee

    def check_schedule(self, start_time, end_time):
        for t in self.__schedule:
            if t.check_overlap(start_time, end_time): return False
        return True
    
    def add_schedule(self, time_range):
        self.__schedule.append(time_range)
    
    def remove_schedule(self, time_range):
        if time_range in self.__schedule:
            self.__schedule.remove(time_range)

class Admin:
    def __init__(self, admin_id, department):
        self.__admin_id = admin_id
        self.__department = department
    
    @property
    def get_id(self): return self.__admin_id