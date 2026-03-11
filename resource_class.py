from enum_class import ResourceStatus, SpaceType, Expertise, EquipmentType
from datetime import datetime

class Resource:
    def __init__(self, resource_id):
        self.__resource_id = resource_id
        self.__status = ResourceStatus.AVAILABLE
    
    @property
    def get_id(self): return self.__resource_id

    @property
    def get_status(self): return self.__status

    def check_available(self): return self.__status == ResourceStatus.AVAILABLE

    def update_status(self, status: ResourceStatus): self.__status = status

    def calculate_fee(self, user, amount, duration): pass

    def validate_access(self, user, amount, start_time, end_time, line_item_list):
        if user.check_blacklist(): return False
        if user.check_invoice(): return False
        return True

    def check_expertise(self, user_expertise): return True
    def check_schedule(self, start_time: datetime, end_time: datetime): return True

    def check_reservable(self, start_time, end_time, amount):
        if not (self.get_status == ResourceStatus.AVAILABLE): return False
        if not (self.check_schedule(start_time, end_time)): return False
        return True
    
    def create_line_item(self, amount, time):
        res = []
        from transaction_class import LineItem
        res.append(LineItem(self, amount, time))
        return res
    
    def process_reserve(self, amount, time):
        self.__schedule.append(time)
        self.update_status(ResourceStatus.IN_USE)

    def cancel_reserve(self, time):
        if time in self.__schedule:
            self.__schedule.remove(time)
            self.update_status(ResourceStatus.AVAILABLE)
        if not self.__schedule:
            self.update_status(ResourceStatus.AVAILABLE)

    def show_info(self):
        return {
            "resource_id": self.get_id,
            "status": self.get_status.value
        }

class Space(Resource):
    COWORK_GUEST_RATE_PER_HR  = 50
    COWORK_MEMBER_FREE_HR     = 2
    COWORK_MEMBER_RATE_PER_HR = 20

    def __init__(self, resource_id, space_type: SpaceType, capacity, valid_start_time, valid_end_time):
        super().__init__(resource_id)
        self.__space_type = space_type
        self.__capacity = capacity
        self.__valid_start_time = valid_start_time
        self.__valid_end_time = valid_end_time
        self.__schedule = []
        self.__equipment_in_space = []
    
    def assign_eq(self, eq): self.__equipment_in_space.append(eq)

    def calculate_fee(self, user, amount, duration):
        if self.__space_type == SpaceType.LABORATORY:
            return 0
        hours = duration / 60
        is_member = user.get_discount > 0
        if is_member:
            billable_hours = max(0, hours - self.COWORK_MEMBER_FREE_HR)
            total = billable_hours * self.COWORK_MEMBER_RATE_PER_HR
        else:
            total = hours * self.COWORK_GUEST_RATE_PER_HR
        return round(total, 2)

    def validate_access(self, user, amount, start_time, end_time, line_item_list):
        if not super().validate_access(user, amount, start_time, end_time, line_item_list): return False
        if not self.check_available(): return False
        if amount > self.__capacity: return False
        adv_days = (start_time - datetime.now()).days
        if adv_days > user.get_max_reserve_days: return False
        if not user.check_expertise(self): return False
        return True

    def check_expertise(self, user_expertise):
        return True
    
    def check_schedule(self, start_time: datetime, end_time: datetime): 
        if start_time.time() < self.__valid_start_time or end_time.time() > self.__valid_end_time: return False
        for sc in self.__schedule:
            if sc.check_overlap(start_time, end_time): return False
        return True
    
    def create_line_item(self, amount, time):
        from transaction_class import LineItem
        res = []
        for eq in self.__equipment_in_space:
            res.append(LineItem(eq, amount, time))
        res.append(LineItem(self, amount, time))
        return res
    
    def process_reserve(self, amount, time):
        self.__schedule.append(time)

    def cancel_reserve(self, time):
        if time in self.__schedule:
            self.__schedule.remove(time)
            if not self.__schedule:
                self.update_status(ResourceStatus.AVAILABLE)

    def show_info(self):
        return {
            "resource_id": self.get_id,
            "status": self.get_status.value,
            "space_type": self.__space_type.value,
            "capacity": self.__capacity,
            "valid_time": f"{self.__valid_start_time} - {self.__valid_end_time}"
        }

class Equipment(Resource):
    def __init__(self, resource_id, eq_type, required_cert: Expertise, location: Space):
        super().__init__(resource_id)
        self.__eq_type = eq_type
        self.__required_cert = required_cert
        self.__location = location
        self.__location.assign_eq(self)
        self.__schedule = []

    def calculate_fee(self, user, amount, duration): pass

    def validate_access(self, user, amount, start_time, end_time, line_item_list):
        if not super().validate_access(user, amount, start_time, end_time, line_item_list): return False
        if not self.check_available(): return False
        if not user.check_expertise(self): return False
        adv_days = (start_time - datetime.now()).days
        if adv_days > user.get_max_reserve_days: return False
        return True

    def check_expertise(self, user_expertise): return self.__required_cert is None or user_expertise == self.__required_cert

    def check_schedule(self, start_time: datetime, end_time: datetime):
        for sc in self.__schedule:
            if sc.check_overlap(start_time, end_time): return False
        return True
    
    def process_reserve(self, amount, time):
        self.__schedule.append(time)

    def cancel_reserve(self, time):
        if time in self.__schedule:
            self.__schedule.remove(time)
            if not self.__schedule:
                self.update_status(ResourceStatus.AVAILABLE)

    def show_info(self):
        return {
            "resource_id": self.get_id,
            "status": self.get_status.value,
            "eq_type": self.__eq_type.value,
            "required_cert": self.__required_cert.value if self.__required_cert else None,
            "location": self.__location.get_id
        }

class ThreeDPrinter(Equipment):
    RATE_MEMBER = 0.5
    RATE_GUEST  = 1.0
    OWN_MATERIAL_SURCHARGE = 0.20

    def __init__(self, resource_id, location, current_filament):
        super().__init__(resource_id, EquipmentType.THREE_D_PRINTER, Expertise.THREE_D_PRINTER, location)
        self.__current_filament = current_filament
        self.__filament_usage = 0
    
    def calculate_fee(self, user, amount, duration, own_material=False):
        is_member = user.get_discount > 0
        rate = self.RATE_MEMBER if is_member else self.RATE_GUEST
        machine_fee = duration * rate
        if own_material:
            material_fee = 0
            surcharge    = machine_fee * self.OWN_MATERIAL_SURCHARGE
        else:
            material_fee = amount * self.__current_filament.COST_PER_UNIT
            surcharge    = 0
        return round(machine_fee + material_fee + surcharge, 2)

    def validate_access(self, user, amount, start_time, end_time, line_item_list):
        if not super().validate_access(user, amount, start_time, end_time, line_item_list): return False
        if self.__current_filament.check_reservable(None, None, amount): return True
        return False

class LaserCutter(Equipment):
    RATE_MEMBER = 5.0
    RATE_GUEST  = 10.0

    def __init__(self, resource_id, location, current_material):
        super().__init__(resource_id, EquipmentType.LASER_CUTTER, Expertise.LASER_CUTTER, location)
        self.__current_material = current_material
        self.__material_usage = 0
    
    def calculate_fee(self, user, amount, duration):
        is_member = user.get_discount > 0
        rate = self.RATE_MEMBER if is_member else self.RATE_GUEST
        machine_fee  = duration * rate
        material_fee = amount * self.__current_material.COST_PER_UNIT
        return round(machine_fee + material_fee, 2)

    def validate_access(self, user, amount, start_time, end_time, line_item_list):
        if not super().validate_access(user, amount, start_time, end_time, line_item_list): return False
        diff = (end_time - start_time).total_seconds() / 60
        if diff < 15: return False
        if self.__current_material.check_reservable(None, None, amount): return True
        return False

    def check_reservable(self, start_time, end_time, amount):
        if not (self.get_status == ResourceStatus.AVAILABLE): return False
        if not (self.check_schedule(start_time, end_time)): return False
        diff = end_time - start_time
        mins = diff.total_seconds() / 60
        if mins < 15: return False
        return True

class ToolSet(Equipment):
    RATE_PER_HR_PER_TOOL = 30

    def __init__(self, resource_id, required_cert, location, tool_count):
        super().__init__(resource_id, EquipmentType.TOOL_SET, required_cert, location)
        self.__tool_count = tool_count

    def calculate_fee(self, user, amount, duration):
        hours = duration / 60
        total = hours * self.RATE_PER_HR_PER_TOOL * amount * (1 - user.get_discount)
        return round(total, 2)

    def validate_access(self, user, amount, start_time, end_time, line_item_list):
        if not super().validate_access(user, amount, start_time, end_time, line_item_list): return False
        if amount > self.__tool_count: return False
        return True

class Material(Resource):
    COST_PER_UNIT = 0
    def __init__(self, resource_id, stock_qty, unit_name, minimum_stock, supported_machine: EquipmentType):
        super().__init__(resource_id)
        self.__stock_qty = stock_qty
        self.__unit_name = unit_name
        self.__minimum_stock = minimum_stock
        self.__supported_machine = supported_machine
    
    def process_reserve(self, amount, time):
        self.__stock_qty -= amount
        if self.__stock_qty <= self.__minimum_stock:
            return True
        return False
    
    def calculate_fee(self, user, amount, duration): 
        total = amount * self.COST_PER_UNIT * (1 - user.get_discount)
        return total

    def validate_access(self, user, amount, start_time, end_time, line_item_list):
        if not super().validate_access(user, amount, start_time, end_time, line_item_list): return False
        if self.__stock_qty - amount < 0: return False
        return True

    def check_reservable(self, start_time, end_time, amount):
        if not (self.get_status == ResourceStatus.AVAILABLE): return False
        if self.__stock_qty - amount < 0: return False
        return True

    def show_info(self):
        return {
            "resource_id": self.get_id,
            "status": self.get_status.value,
            "stock_qty": self.__stock_qty,
            "unit_name": self.__unit_name
        }

class Filament(Material):
    COST_PER_UNIT = 2
    def __init__(self, resource_id, stock_qty, unit_name, minimum_stock, filament_type, diameter, color):
        super().__init__(resource_id, stock_qty, unit_name, minimum_stock, EquipmentType.THREE_D_PRINTER)
        self.__filament_type = filament_type
        self.__diameter = diameter
        self.__color = color

class Acrylic(Material):
    COST_PER_UNIT = 80
    def __init__(self, resource_id, stock_qty, unit_name, minimum_stock, thickness, dimension, color):
        super().__init__(resource_id, stock_qty, unit_name, minimum_stock, EquipmentType.LASER_CUTTER)
        self.__thickness = thickness
        self.__dimension = dimension
        self.__color = color
    
class Plank(Material):
    COST_PER_UNIT = 30
    def __init__(self, resource_id, stock_qty, unit_name, minimum_stock, wood_type, thickness):
        super().__init__(resource_id, stock_qty, unit_name, minimum_stock, EquipmentType.LASER_CUTTER)
        self.__wood_type = wood_type
        self.__thickness = thickness