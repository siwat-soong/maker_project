from itertools import count
from datetime import datetime, timedelta

class Event:
    __id_counter = count(1)

    def __init__(self, topic, detail, time, instructor, space, item_list, max_attender, join_fee, certified_topic):
        self.__event_id = f'WS-{next(self.__id_counter):04d}'
        self.__topic = topic
        self.__detail = detail
        self.__time = time
        self.__instructor = instructor
        self.__space = space
        self.__item_list = item_list
        self.__max_attender = max_attender
        self.__join_fee = join_fee
        self.__certified_topic = certified_topic

class Certification:
    def __init__(self, owner, event, certified_topic):
        self.__owner = owner
        self.__event = event
        self.__certified_topic = certified_topic
        self.__certified_date = datetime.now()
        self.__expired_date = datetime.now() + timedelta(days=365)