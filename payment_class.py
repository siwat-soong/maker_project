from abc import ABC, abstractmethod

class PaymentMethod(ABC):
    @abstractmethod
    def validate(self):
        pass

    @abstractmethod
    def process_payment(self):
        pass

class Cash(PaymentMethod):
    def validate(self):
        pass

    def process_payment(self):
        pass

class QRCode(PaymentMethod):
    def validate(self):
        pass

    def process_payment(self):
        pass

    def generate_qr_code(self, amount):
        print("✅ QR Code Generated!")