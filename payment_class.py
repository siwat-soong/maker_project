from abc import ABC, abstractmethod

class PaymentMethod(ABC):
    @abstractmethod
    def validate(self, amount, required_cost):
        pass

    @abstractmethod
    def process_payment(self, amount):
        pass

class Cash(PaymentMethod):
    def validate(self, amount, required_cost):
        return amount >= required_cost

    def process_payment(self, amount):
        print(f"Processing cash payment of {amount}")
        return True

class QRCode(PaymentMethod):
    def validate(self, amount, required_cost):
        return amount == required_cost

    def process_payment(self, amount):
        self.generate_qr_code(amount)
        print("📱 QR Code scanned and payment processed!")
        return True

    def generate_qr_code(self, amount):
        print("✅ QR Code Generated!")