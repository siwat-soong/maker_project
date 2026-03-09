from enum_class import UserRole
from datetime import datetime, timedelta

class User:
    def __init__(self, user_id, name, tel):
        # Basic Info
        self.__user_id = user_id
        self.__name = self.__validate_input_name(name)
        self.__tel = self.__validate_input_tel(tel)
        self.__role = UserRole.GUEST
        self.__expired_date = datetime.now() + timedelta(days=1)
        self.__max_reserve_days = 1
        self.__is_blacklist = False

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

    def add_certificate(self, certificate): self.__certificate_list.append(certificate)
    def add_reservation(self, reservation): self.__reservation_list.append(reservation)
    def add_line_item(self, line_item): self.__line_item_list.append(line_item)
    def add_invoice(self, invoice): self.__invoice_list.append(invoice)
    def add_receipt(self, receipt): self.__receipt_list.append(receipt)
    def add_notification(self, notification): self.__notification_list.append(notification)

    def search_invoice_by_id(self, inv_id):
        for inv in self.__invoice_list:
            if inv.get_id == inv_id: return inv
        return None

    def check_blacklist(self): return self.__is_blacklist

    def update_role(self, role: UserRole): self.__role = role

    def subscribe(self):
        self.__role = UserRole.MEMBER
        self.__expired_date = datetime.now() + timedelta(days=365)
        self.__max_reserve_days = 14
    
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

class Instructor(User):
    def __init__(self, user_id, name, tel, expertise, instructor_fee):
        super().__init__(user_id, name, tel)
        self.update_role(UserRole.MEMBER)
        self.__expertise = expertise
        self.__instructor_fee = instructor_fee

class Admin:
    def __init__(self, admin_id, department):
        self.__admin_id = admin_id
        self.__department = department