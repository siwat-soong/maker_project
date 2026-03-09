from abc import ABC, abstractmethod

class PaymentMethod(ABC):
    def __init__(self): pass

    @abstractmethod
    def validate(self): pass

    @abstractmethod
    def process_payment(self): pass

class Cash(PaymentMethod):
    def __init__(self, cash_in_machine):
        self.__cash_in_machine = cash_in_machine
    
    def validate(self): pass

    def process_payment(self): pass

class QRCode(PaymentMethod):
    
    def validate(self): pass

    def process_payment(self): pass