from abc import ABC, abstractmethod

class PaymentMethod(ABC):
    def __init__(self, method_id):
        self.__method_id = method_id
    
    @property
    def get_id(self): return self.__method_id

    @abstractmethod
    def validate(self, total, cost): pass

    @abstractmethod
    def process_payment(self): pass

class Cash(PaymentMethod):
    def __init__(self, method_id, cash_in_machine):
        super().__init__(method_id)
        self.__cash_in_machine = cash_in_machine
        self.__change = 0
    
    def validate(self, total, cost): 
        if cost < total: return False
        else:
            self.__change = cost - total
            if self.__change > 0 and self.__cash_in_machine - self.__change < 0: return False
            else: return True  

    def process_payment(self): 
        return self.__change

class QRCode(PaymentMethod):
    def __init__(self, method_id):
        super().__init__(method_id)
    
    def validate(self, total, cost): 
        if cost < total: return False
        else: return True

    def process_payment(self): 
        return 0