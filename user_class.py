from enum_class import UserRole
from datetime import datetime, timedelta

class User:
    MEMBER_FEE = 100

    def __init__(self, user_id, name, tel):
        # Basic Info
        self.__user_id = user_id
        self.__name = self.__validate_input_name(name)
        self.__tel = self.__validate_input_tel(tel)
        self.__role = UserRole.GUEST
        self.__expired_date = datetime.now() + timedelta(days=1)
        self.__monthly_quota = 0
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

    def add_certificate(self, certificate): self.__certificate_list.append(certificate)
    def add_reservation(self, reservation): self.__reservation_list.append(reservation)
    def add_line_item(self, line_item): self.__line_item_list.append(line_item)
    def add_invoice(self, invoice): self.__invoice_list.append(invoice)
    def add_receipt(self, receipt): self.__receipt_list.append(receipt)
    def add_notification(self, notification): self.__notification_list.append(notification)

    def check_blacklist(self): return self.__is_blacklist

    def update_role(self, role: UserRole): self.__role = role

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