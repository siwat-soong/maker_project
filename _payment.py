from abc import ABC, abstractmethod
from _enum import PaymentMethodType

class PaymentMethod(ABC):
    @abstractmethod
    def validate(self, total, amount): pass

    @abstractmethod
    def process_payment(self, total, amount): pass

class Cash(PaymentMethod):
    def __init__(self, in_cash: float):
        self.__type = PaymentMethodType.CASH
        self.__in_cash = in_cash
    
    @property
    def get_type(self): return self.__type
    
    def validate(self, total, amount):
        if amount - total > self.__in_cash: return False
        return True

    def process_payment(self, total, amount): 
        change = amount - total
        self.__in_cash -= change
        return change
    
class QRCode(PaymentMethod):
    def __init__(self):
        self.__type = PaymentMethodType.QRCODE
    
    @property
    def get_type(self): return self.__type
    
    def validate(self, total, amount): return True

    def process_payment(self, total, amount): return 0