from _enum import UserRole, InvoiceType
from datetime import datetime, timedelta
from _transaction import Invoice

class User:
    def __init__(self, uid: str, name: str, tel: str):
        self.__uid = uid
        self.__name = self.__validate_input_name(name)
        self.__tel = self.__validate_input_tel(tel)
        self.__role = UserRole.GUEST
        self.__expired_date = None
        self.__max_reserve_days = 1
        self.__is_blacklist = False
        self.__discount = 0

        # Storage
        self.__cart = []
        self.__reservation_list = []
        self.__invoice = None
        self.__receipt_list = []
        self.__notification_list = []
        self.__certificate_list = []
    
    def __validate_input_name(self, name: str):
        if all(char.isalpha() or char.isspace() for char in name) and name != "": return name
        else: raise ValueError("ชื่อต้องเป็นตัวอักษรหรือช่องว่างเท่านั้น")
    
    def __validate_input_tel(self, tel: str):
        if not tel.isdigit(): raise ValueError("เบอร์มือถือต้องเป็นตัวเลขเท่านั้น")
        if len(tel) != 10: raise ValueError("เบอร์มือถือต้องมี 10 หลักเท่านั้น")
        if tel[0] != "0": raise ValueError("เบอร์มือถือต้องขึ้นต้นด้วย 0 เท่านั้น")
        return tel
    
    @property
    def get_id(self): return self.__uid

    @property
    def get_name(self): return self.__name

    @property
    def get_tel(self): return self.__tel

    @property
    def get_role(self): return self.__role

    @property
    def get_exp(self): return self.__expired_date

    @property
    def get_max_rsv(self): return self.__max_reserve_days

    @property
    def is_blacklist(self): return self.__is_blacklist

    @property
    def get_discount(self): return self.__discount

    @property
    def get_cart(self): return self.__cart

    @property
    def get_reservation(self): return self.__reservation_list

    @property
    def get_invoice(self): return self.__invoice

    @property
    def get_receipt(self):return self.__receipt_list

    @property
    def get_notification(self): return self.__notification_list

    def blacklist(self): self.__is_blacklist = True
    def unblacklist(self): self.__is_blacklist = False

    def create_reservation(self, item_list):
        from _transaction import Reservation
        rsv = Reservation(self, item_list)
        self.__reservation_list.append(rsv)
        return rsv
    
    def update_role(self, role): self.__role = role

    def subscribe(self):
        self.__role = UserRole.MEMBER
        self.__expired_date = datetime.now() + timedelta(days= 365)
        self.__max_reserve_days = 14
        self.__discount = 0.20
    
    def add_to_cart(self, resource, amount: float, start_time, end_time):
        from _transaction import ReserveSlot, TimeRange
        if not start_time or not end_time: t = None
        else: t = TimeRange(start_time, end_time)
        res = resource.process_cart()

        slot = []
        for r in res:
            slot.append(ReserveSlot(r, amount, t))
        for c in self.__cart:
            for s in slot:
                if c.check_duplicate(s): 
                    if t is not None: raise Exception("มีการเพิ่มซ้ำ")
                    elif t is None: 
                        if resource.get_stock_qty - c.get_amount - amount < 0: raise Exception("ไม่สามารถเพิ่มทรัพยากรในตะกร้าได้")
                        c.add_amount(amount)
                        return
                    
        self.__cart.extend(slot)
    
    def remove_from_cart(self, resource, start_time):
        res = resource.to_cancel()
        found = 0
        rm_list = []
        for c in self.__cart:
            for r in res:
                if c.get_resource.get_id == r.get_id:
                    if  (c.get_time is not None and c.get_time.get_start_time == start_time) or c.get_time is None: 
                        rm_list.append(c)
                        found += 1
        
        if found == 0: raise Exception("ไม่พบทรัพยากรในตะกร้าของคุณ")
        else: 
            for i in range(len(rm_list)):
                self.__cart.remove(rm_list[i])
    
    def clear_cart(self, item):
        for i in item:
            self.__cart.remove(i)

    def create_invoice(self, type: InvoiceType, detail, cost: float):
        inv = Invoice(self, type, detail, cost)
        self.__invoice = inv
    
    def clear_invoice(self): self.__invoice = None

    def create_receipt(self, inv_id: str, type: InvoiceType, detail, total: float, purchased: float, change: float):
        from _transaction import Receipt
        rec = Receipt(self, inv_id, type, detail, total, purchased, change)
        self.__receipt_list.append(rec)

    def notify(self, topic, detail):
        from _transaction import Notification
        noti = Notification(self, topic, detail)
        self.__notification_list.append(noti)
    
    def check_expertise(self, required_cert):
        if required_cert is None: return True
        if self.__certificate_list:
            for cert in self.__certificate_list:
                if cert.get_expertise == required_cert: return True
            return False
        return False
    
    def add_certificate(self, certificate): self.__certificate_list.append(certificate)

    def create_certificate(self, event, grade):
        from _event import Certification
        cert = Certification(self, event, event.get_cert, grade)
        self.add_certificate(cert)

    def search_reservation_by_id(self, rsv_id):
        for rsv in self.__reservation_list:
            if rsv.get_id == rsv_id: return rsv
        return None
    
    def detail(self): return {
        "UID": self.__uid,
        "NAME": self.__name,
        "TEL": self.__tel,
        "ROLE": self.__role
    }

class Instructor(User):
    def __init__(self, user_id, name, tel, expertise, instructor_fee: float):
        super().__init__(user_id, name, tel)
        self.subscribe()
        self.__expertise = expertise
        self.__instructor_fee = float(instructor_fee)
        self.__schedule = []
    
    @property
    def get_expertise(self): return self.__expertise

    @property
    def get_fee(self): return self.__instructor_fee

    def check_schedule(self, time):
        for sch in self.__schedule:
            if sch.check_overlap(time.get_start_time, time.get_end_time): return True
        return False
    
    def check_expertise(self, required_cert): return True

    def add_schedule(self, time): self.__schedule.append(time)
    def remove_schedule(self, time): self.__schedule.remove(time)

    def detail(self):
        data = super().detail()
        data.update({
            "EXPERTISE": self.__expertise,
            "FEE": self.__instructor_fee
        })
        return data

class Admin:
    def __init__(self, admin_id, department):
        self.__admin_id = admin_id
        self.__department = department
    
    @property
    def get_id(self): return self.__admin_id

    def check_expertise(self, required_cert): return True

    def detail(self): return {
        "ID": self.__admin_id,
        "DEPARTMENT": self.__department
    }