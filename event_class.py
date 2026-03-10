from itertools import count
from datetime import datetime, timedelta
from enum_class import EventStatus

class Event:
    __id_counter = count(1)

    def __init__(self, topic, detail, time, instructor, space, item_list, max_attender: float, join_fee: float, certified_topic):
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
    def get_status(self):
        return self.__status

    def check_joinable(self, user):
        if len(self.__attendants) >= float(self.__max_attender): return False
        if self.__status == EventStatus.SCHEDULED or self.__status == EventStatus.OPEN: return True
        if user in self.__attendants: return False
        return True

    def calculate_fee(self, user):
        return self.__join_fee * (1 - user.get_discount)
    
    def join(self, user):
        self.__attendants.append(user)
        if len(self.__attendants) >= float(self.__max_attender): self.__status = EventStatus.FULL
    
    def add_eq(self, ite):
        self.__item_list.extend(ite)
    
    def show_info(self):
        return {
        "event_id": self.__event_id,
        "status": self.__status.value,
        "topic": self.__topic,
        "detail": self.__detail,
        "time": str(self.__time),
        "instructor": self.__instructor.get_id,
        "location": self.__space.get_id if self.__space else None,
        "attenders": f"{len(self.__attendants)}/{self.__max_attender}",
        "join_fee": self.__join_fee,
        "certified_topic": self.__certified_topic.value if hasattr(self.__certified_topic, 'value') else self.__certified_topic
    }

class Certification:
    def __init__(self, owner, event, certified_topic):
        self.__owner = owner
        self.__event = event
        self.__certified_topic = certified_topic
        self.__certified_date = datetime.now()
        self.__expired_date = datetime.now() + timedelta(days=365)
    
    @property
    def get_expertise(self): return self.__certified_topic