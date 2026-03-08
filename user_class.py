from datetime import datetime
from enum_class import UserRole, Expertise
from event_class import *
from enum_class import *

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

    def __repr__(self):
        if self.__role == UserRole.ANNUALMEMBER:
            return f"⭐ Member:\nID = {self.get_id}\nNAME = {self.get_name}\nTEL = {self.get_tel}\nSTATUS = {self.__role}\n"
        else:
            return f"👤 User:\nID = {self.__user_id}\nNAME = {self.__name}\nTEL = {self.__tel}\n"

    # Input Validation
    def __validate_input_name(self, name):
        if all(char.isalpha() or char.isspace() for char in name) and name != "": return name
        else: raise ValueError("Name must be character or space")

    def __validate_input_tel(self, tel):
        if not tel.isdigit(): raise ValueError("Telephone Number must be number")
        if len(tel) != 10: raise ValueError("Telephone Number must have 10 digits")
        if tel[0] != "0": raise ValueError("Telephone Number must start with 0")
        return tel

    # Getters
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
        return 14 if self.__role == UserRole.ANNUALMEMBER else 1

    @property
    def get_user_reservation(self):
        return self.__reservation_list

    @property
    def line_item_list(self):
        return self.__line_item_list

    @property
    def get_user_item_list(self):
        return self.__line_item_list

    # Status
    def update_status(self, status):
        if status == UserRole.ANNUALMEMBER:
            self.__role = status
            current_date = datetime.now()
            self.__registry_date = current_date
            self.__expired_date = current_date.replace(year=current_date.year + 1)
            self.__monthly_quota = 120

    def check_blacklist(self):
        return self.__is_blacklist

    def check_certified(self, required_certified):
        if required_certified is None: return True
        for certificate in self.__certificate_list:
            if certificate.get_certified_topic == required_certified:
                if certificate.get_expired_date is None: return True
                elif datetime.now() < certificate.get_expired_date: return True
                else: return False
        return False

    # Notification
    def notify(self, notification):
        from transaction import Notification
        if isinstance(notification, Notification):
            self.__notification_list.append(notification)

    # Certificate
    def add_certificate(self, certificate):
        if isinstance(certificate, Certificate): self.__certificate_list.append(certificate)
        else: raise TypeError("Please add certificate only")

    # Cart
    def add_to_cart(self, line_item):
        from transaction import LineItem
        if isinstance(line_item, LineItem):
            self.__line_item_list.append(line_item)
        else:
            raise TypeError("Please add LineItem only")

    def add_item_list(self, line_item):
        from transaction import LineItem
        if isinstance(line_item, LineItem):
            self.__line_item_list.append(line_item)

    def clear_cart(self):
        self.__line_item_list = []

    # Invoice
    def add_invoice(self, invoice):
        from transaction import Invoice
        if isinstance(invoice, Invoice):
            self.__invoice_list.append(invoice)
            return "✅ Add Invoice Success"
        return "⚠️ failed to add Invoice"

    def add_receipt(self, receipt):
        from transaction import Receipt
        if isinstance(receipt, Receipt):
            self.__receipt_list.append(receipt)
            return "✅ Add Receipt Success"
        return "⚠️ failed to add Receipt"

    # Reservation
    def add_reservation(self, reservation):
        from transaction import Reservation
        if isinstance(reservation, Reservation):
            self.__reservation_list.append(reservation)

    def search_reservation_by_id(self, reservation_id: str):
        for reservation in self.__reservation_list:
            if reservation.get_reservation_id == reservation_id:
                return reservation
        return None

    def list_reserve_history(self):
        result = []
        for rsv in self.__reservation_list:
            item_ids = [item.get_resource.get_id for item in rsv._Reservation__line_item_list]
            result.append({
                "reservation_id": rsv.get_reservation_id,
                "status": rsv._Reservation__status.value,
                "due_date": rsv._Reservation__due_date.strftime("%Y-%m-%d"),
                "items": item_ids
            })
        return result

    def cancel_reservation(self, reservation_id):
        for rsv in self.__reservation_list:
            if rsv.get_reservation_id == reservation_id:
                if rsv._Reservation__status != ReserveStatus.CONFIRMED:
                    return f"failed: cannot cancel reservation with status {rsv._Reservation__status.value}"
                rsv.update_status(ReserveStatus.CANCELLED)
                return f"success: {reservation_id} cancelled"
        return "failed: Reservation not found"

    # Payment
    def pay_invoice(self, user_id: str, invoice_ids: list, amount: float, payment_method=None):
        from transaction import Invoice, Receipt
        from payment_class import Cash

        if user_id != self.__user_id:
            return "⚠️ User can't pay this Invoice"

        target_invoices = []
        for invoice_id in invoice_ids:
            found = next((inv for inv in self.__invoice_list if inv.get_id == invoice_id), None)
            if not found:
                return f"⚠️ Invoice not found: {invoice_id}"
            if found.is_purchased():
                return f"⚠️ already paid: {invoice_id}"
            target_invoices.append(found)

        total_required = sum(inv.get_cost() for inv in target_invoices)

        if total_required == 0:
            for inv in target_invoices:
                inv.mark_as_paid()
                r = Receipt(inv.user, Cash(), inv)
                self.__receipt_list.append(r)
            return "✅ Pay Invoice Success"

        if payment_method is None:
            return "⚠️ No Payment Method"

        if not payment_method.validate(amount, total_required):
            return f"⚠️ Not enough money: required {total_required}, paid {amount}"

        if payment_method.process_payment(amount):
            receipts = []
            for inv in target_invoices:
                inv.mark_as_paid()
                reservation = inv.get_reservation()
                if reservation:
                    reservation.update_status(ReserveStatus.COMPLETED)
                r = Receipt(inv.user, payment_method, inv)
                self.__receipt_list.append(r)
                receipts.append({
                    "receipt_id": r.receipt_id,
                    "invoice_id": inv.get_id,
                    "cost": inv.get_cost(),
                    "payment_status": "PAID"
                })
            self.__unpaid_balance = max(0, self.__unpaid_balance - total_required)
            return receipts
        return "❌ Payment Processing Failed"

    # Events
    def join_event(self, event_id):
        pass

    def cancel_event(self, event_id):
        pass

    def check_in(self, reservation_id, space_id):
        pass

    def check_out(self, reservation_id, space_id):
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

    @property
    def get_id(self):
        return super().get_id

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

    def list_event_attender(self, event_id):
        pass


class Admin:
    def __init__(self, admin_id, name, department):
        self.__admin_id = admin_id
        self.__name = self.__validate_input_name(name)
        self.__department = department

    def __validate_input_name(self, name):
        if all(char.isalpha() or char.isspace() for char in name) and name != "": return name
        else: raise ValueError("Name must be character or space")

    @property
    def get_id(self):
        return self.__admin_id

    def force_cancel_membership(self, user_id, reason):
        pass

    def generate_report(self):
        pass