from itertools import count
from datetime import datetime, timedelta
from enum_class import EventStatus

class Event:
    __id_counter = count(1)

    def __init__(self, topic, detail, time, instructor, space, item_list, max_attender: str, join_fee: float, certified_topic):
        self.__event_id = f'WS-{next(self.__id_counter):04d}'
        self.__topic = topic
        self.__detail = detail
        self.__time = time
        self.__instructor = instructor
        self.__space = space
        self.__item_list = item_list if item_list else []
        self.__max_attender = max_attender
        self.__join_fee = float(join_fee)
        self.__certified_topic = certified_topic
        self.__status = EventStatus.SCHEDULED
        self.__attendants = []
    
    @property
    def get_id(self): return self.__event_id
    
    @property
    def get_instructor(self): return self.__instructor

    @property
    def get_attendants(self): return self.__attendants

    @property
    def get_certified_topic(self): return self.__certified_topic

    @property
    def get_time(self): return self.__time

    @property
    def get_space(self): return self.__space

    @property
    def get_item_list(self): return self.__item_list

    def search_attendant_by_id(self, user_id):
        for atd in self.__attendants:
            if atd.get_id == user_id: return atd
        return None

    def check_attender(self, user_id):
        for atd in self.__attendants:
            if atd.get_id == user_id: return True
        return False

    def check_joinable(self, user):
        if user in self.get_attendants: return False
        if len(self.get_attendants) >= float(self.__max_attender): return False
        if self.__status == EventStatus.SCHEDULED or self.__status == EventStatus.OPEN: return True
        return False

    def calculate_fee(self, user):
        return round(self.__join_fee * (1 - user.get_discount), 2)
    
    def join(self, user):
        print("JOIN")
        self.get_attendants.append(user)
        if len(self.__attendants) >= float(self.__max_attender): self.__status = EventStatus.FULL
    
    def add_eq(self, ite):
        self.__item_list.extend(ite)
    
    def rm_uid(self, user): self.__attendants.remove(user)

    def remove_attendant(self, user_id):
        for u in self.get_attendants:
            if u.get_id == user_id:
                print(u)
                self.rm_uid(u)
                return 0
        raise Exception
    
    def update_status(self, status: EventStatus): self.__status = status
    
    def show(self):
        return {
        "ID": self.__event_id,
        "TOPIC": self.__topic,
        "DETAIL": self.__detail,
        "TIME": self.__time,
        "FEE": self.__join_fee,
        "CERTIFIED": self.__certified_topic,
        "STATUS": self.__status
        }

class Certification:
    def __init__(self, owner, event, certified_topic, grade=None):
        self.__owner = owner
        self.__event = event
        self.__certified_topic = certified_topic
        self.__grade = grade
        self.__certified_date = datetime.now()
        self.__expired_date = datetime.now() + timedelta(days=365)
    
    @property
    def get_expertise(self): return self.__certified_topic