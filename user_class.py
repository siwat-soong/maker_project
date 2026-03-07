from datetime import datetime
from enum_class import UserRole, Expertise
from event_class import *
from enum_class import *

# User & sub class
class User:
    MEMBER_FEE = 100
    def __init__(self, user_id, name, tel):
        self.__user_id = user_id
        self.__name = self.__validate_input_name(name)
        self.__tel = self.__validate_input_tel(tel)
        self.__role = UserRole.GUEST
        self.__certificate_list = []
        self.__notification_list = []
        self.__reservation_list = []
        self.__invoice_list = []
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
    def get_role(self):
        return self.__role
    
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
        if status == UserRole.ANNUALMEMBER:
            self.__role = status
            current_date = datetime.now()
            self.__registry_date = current_date
            self.__expired_date = current_date.replace(year=current_date.year + 1)
            self.__monthly_quota = 120  # minutes
    
    def notify(self, notification):
        from transaction import Notification
        if isinstance(notification, Notification):
            self.__notification_list.append(notification)

    def join_event(self, event_id):
        pass

    def add_invoice(self, invoice):
        from transaction import Invoice
        if isinstance(invoice, Invoice):
            self.__invoice_list.append(invoice)
            return {"invoice_id": invoice.get_id, "cost": invoice.get_cost(), "payment_status": "PAID" if invoice.is_purchased() else "UNPAID", "message": "Invoice added"}
        else:
            raise TypeError("Please add Invoice only")

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

    def pay_invoice(self, user_id: str, invoice_ids: list, amount: float, payment_method=None):
        from transaction import Invoice, Receipt
        from payment_class import Cash

        if user_id != self.__user_id:
            return {"status": "failed", "message": f"User '{user_id}' is not authorized to pay these invoices"}

        target_invoices = []
        for invoice_id in invoice_ids:
            found = None
            for inv in self.__invoice_list:
                if inv.get_id == invoice_id:
                    found = inv
                    break
            if not found:
                return {"status": "failed", "message": f"Invoice not found: {invoice_id}"}
            if found.is_purchased():
                return {"status": "failed", "message": f"Invoice already paid: {invoice_id}"}
            target_invoices.append(found)

        total_required = sum(inv.get_cost() for inv in target_invoices)

        if total_required == 0:
            receipts = []
            for inv in target_invoices:
                inv.mark_as_paid()
                r = Receipt(inv.user, Cash(), inv)
                self.__receipt_list.append(r)
                receipts.append(r.receipt_id)
            return {"status": "success", "receipt_ids": receipts, "total": 0.0}

        pm = payment_method
        if pm is None:
            return {"status": "failed", "message": "No payment method provided"}

        if not pm.validate(amount, total_required):
            return {"status": "failed", "message": f"Insufficient amount. Required: {total_required}, Got: {amount}"}

        if pm.process_payment(amount):
            receipts = []
            for inv in target_invoices:
                inv.mark_as_paid()
                reservation = inv.get_reservation()
                if reservation:
                    reservation.update_status("COMPLETED")
                r = Receipt(inv.user, pm, inv)
                self.__receipt_list.append(r)
                receipts.append(r.receipt_id)
            self.__unpaid_balance = max(0, self.__unpaid_balance - total_required)
            return {"status": "success", "receipt_ids": receipts, "total": total_required}

        return {"status": "failed", "message": "Payment processing failed"}

    def reserve(self):
        pass

    def return_resource(self, reservation_id, resource_id=None):
        pass
    

    def add_reservation(self, reservation):
        from transaction import Reservation
        if isinstance(reservation, Reservation):
            self.__reservation_list.append(reservation)

    def search_reservation_by_id(self, reservation_id: str):
        for reservation in self.__reservation_list:
            if reservation.get_reservation_id == reservation_id:
                return reservation
        return None

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