from enum_class import Expertise, EventStatus
from user_class import Instructor
from resource_class import Space
from user_class import User
from datetime import datetime

class Event:
    def __init__(self, event_id, event_topic, event_detail, instructor, space, max_attender, join_fee, certified_topic):
        self.__event_id = event_id
        self.__event_detail = event_detail
        self.__instructor = self.__validate_input_specific_type(instructor, Instructor)
        self.__space = self.__validate_input_specific_type(space, Space)
        self.__max_attender = self.__validate_input_number(max_attender, 1)
        self.__join_fee = self.__validate_input_number(join_fee, 0)
        self.__certified_topic = self.__validate_input_specific_type(certified_topic, Expertise)
        self.__attenders = []
        self.__status = EventStatus.SCHEDULED

        # Input Validation
    def __validate_input_specific_type(self, obj, obj_type):
        if isinstance(obj, obj_type): return obj
        else: raise ValueError("Wrong Type")
    
    def __validate_input_number(self, number, minimum):
        try:
            if float(number) >= float(minimum): return number
            else: raise Exception()
        except: raise ValueError(f"Number must be equal or greater than {minimum}")
    
    def check_attender(self, user_id):
        for user in self.__attenders:
            if user.get_id == user_id: return True
        return False
    
    def check_status(self):
        return self.__status
    
    def check_availability(self):
        return self.__status == EventStatus.OPEN
    
    def join(self, user):
        if len(self.__attenders) + 1 <= self.__max_attender:
            for attender in self.__attenders:
                if user.get_id == attender.get_id: raise SystemError("Duplicate Join")
            self.__attenders.append(user)
            if len(self.__attenders) == self.__max_attender:
                self.__status = EventStatus.FULL
        else: raise SystemError("Join over limit")
    
    def remove_attender(self, user):
        for attender in self.__attenders:
            if user.get_id == attender.get_id:
                self.__attenders.remove(attender)
                if len(self.__attenders) < self.__max_attender:
                    self.__status = EventStatus.OPEN
    

class Certificate:
    def __init__(self, owner, event, certified_topic, certified_date, expired_date=None):
        self.__owner = self.__validate_input_specific_type(owner, User)
        self.__event = self.__validate_input_specific_type(event, Event)
        self.__certified_topic = self.__validate_input_specific_type(certified_topic, Expertise)
        self.__certified_date = self.__validate_input_specific_type(certified_date, datetime)
        self.__expired_date = self.__validate_input_specific_type(expired_date, datetime, True)
    
    # Input Validation
    def __validate_input_specific_type(self, obj, obj_type, accept_none=False):
        if accept_none:
            if obj is None: return None
        elif isinstance(obj, obj_type): return obj
        else: raise TypeError("Wrong Type")
    
    @property
    def get_certified_topic(self):
        return self.__certified_topic
    
    @property
    def get_certified_date(self):
        return self.__certified_date
    
    @property
    def get_expired_date(self):
        return self.__expired_date