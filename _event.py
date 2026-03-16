from itertools import count
from datetime import datetime, timedelta
from _enum import EventStatus, InvoiceType
from _transaction import Invoice, Receipt

class Event:
    __id_counter = count(1)

    def __init__(self, topic, detail, time, instructor, space, item_list, max_attender: float, join_fee: float):
        self.__event_id = f'WS-{next(self.__id_counter):04d}'
        self.__topic = topic
        self.__detail = detail
        self.__time = time
        self.__instructor = instructor
        self.__space = space
        self.__item_list = item_list if item_list else []
        self.__max_attender = max_attender
        self.__join_fee = float(join_fee) + self.__instructor.get_fee
        self.__certified_topic = self.__instructor.get_expertise
        self.__status = EventStatus.SCHEDULED
        self.__attendants = []
        self.__receipt = []
    
    @property
    def get_id(self): return self.__event_id

    @property
    def get_time(self): return self.__time

    @property
    def get_items(self): return self.__item_list

    @property
    def get_ins(self): return self.__instructor

    @property
    def get_status(self): return self.__status

    @property
    def get_cert(self): return self.__certified_topic

    @property
    def get_attendants(self): return self.__attendants

    def check_attendant(self, user): return user in self.__attendants
    
    def join(self, user):
        if self.__status != EventStatus.OPEN: raise Exception("กิจกรรมนี้ไม่เปิดรับ")
        if len(self.__attendants) == self.__max_attender: raise Exception("กิจกรรมนี้เต็มแล้ว")
        if self.check_attendant(user): raise Exception("คุณได้เข้าร่วมกิจกรรมนี้แล้ว")
        self.__attendants.append(user)
        if len(self.__attendants) == self.__max_attender: self.__status = EventStatus.FULL
        return self.__join_fee
    
    def unjoin(self, user, time):
        if not self.check_attendant(user): raise Exception("คุณไม่ได้เข้าร่วมกิจกรรมนี้")
        if time > self.__time.get_end_time: raise Exception("เกินเวลาของกิจกรรมแล้ว")
        if self.__status == EventStatus.CLOSED: raise Exception("กิจกรรมนี้ได้ปิดไปแล้ว")

        self.__attendants.remove(user)
        if len(self.__attendants) < self.__max_attender and time > self.__time.get_start_time: self.__status = EventStatus.OPEN
        elif len(self.__attendants) < self.__max_attender and time < self.__time.get_start_time: self.__status = EventStatus.SCHEDULED

        diff = time - self.__time.get_start_time
        if diff.total_seconds() / 3600 < -4: return self.__join_fee
        else: return 0
    
    def open_event(self): self.__status = EventStatus.OPEN 

    def update_status(self, status): self.__status = status

    def create_receipt(self, user, type: InvoiceType, detail, cost: float):
        inv = Invoice(self, type, detail, cost)
        receipt = Receipt(user, inv.get_id, inv.get_type, inv.get_detail, cost, cost, 0)
        self.__receipt.append(receipt)
    
    def detail(self): return {
        "ID": self.__event_id,
        "TOPIC": self.__topic,
        "DETAIL": self.__detail,
        "START": self.__time.get_start_time.strftime("%d-%m-%Y %H:%M"),
        "END": self.__time.get_end_time.strftime("%d-%m-%Y %H:%M"),
        "INSTRUCTOR": self.__instructor.get_name,
        "LOCATION": self.__space.get_id,
        "MAX ATTENDER": self.__max_attender,
        "FEE": self.__join_fee,
        "STATUS": self.__status
    }

class Certification:
    def __init__(self, owner, event, certified_topic, grade=None):
        self.__owner = owner
        self.__event = event
        self.__certified_topic = certified_topic
        self.__grade = grade
        self.__certified_date = datetime.now()
    
    @property
    def get_expertise(self): return self.__certified_topic