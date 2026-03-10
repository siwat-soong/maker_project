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
    def check_status(self): pass

    def calculate_fee(self, user, amount, duration): pass

    def validate_access(self, user, amount, start_time, end_time, line_item_list): pass

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
        pass

    def show_detail(self):
        return {
            "resource_id": self.get_id,
            "status": self.get_status.value
        }

class Space(Resource):
    def __init__(self, resource_id, space_type: SpaceType, capacity, valid_start_time, valid_end_time):
        super().__init__(resource_id)
        self.__space_type = space_type
        self.__capacity = capacity
        self.__valid_start_time = valid_start_time
        self.__valid_end_time = valid_end_time
        self.__schedule = []
        self.__equipment_in_space = []
    
    def assign_eq(self, eq): self.__equipment_in_space.append(eq)
    
    def calculate_fee(self, user, amount, duration): return 0

    def validate_access(self, user, amount, start_time, end_time, line_item_list): pass

    def check_expertise(self, user_expertise):
        for eq in self.__equipment_in_space:
            if not eq.check_expertise(user_expertise): return False
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

    def show_detail(self):
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

    def validate_access(self, user, amount, start_time, end_time, line_item_list): pass

    def check_expertise(self, user_expertise): return self.__required_cert is None or user_expertise == self.__required_cert

    def check_schedule(self, start_time: datetime, end_time: datetime):
        for sc in self.__schedule:
            if sc.check_overlap(start_time, end_time): return False
        return True
    
    def process_reserve(self, amount, time):
        self.__schedule.append(time)

    def show_detail(self):
        return {
            "resource_id": self.get_id,
            "status": self.get_status.value,
            "eq_type": self.__eq_type.value,
            "required_cert": self.__required_cert.value if self.__required_cert else None,
            "location": self.__location.get_id
        }

class ThreeDPrinter(Equipment):
    def __init__(self, resource_id, location, current_filament):
        super().__init__(resource_id, EquipmentType.THREE_D_PRINTER, Expertise.THREE_D_PRINTER, location)
        self.__current_filament = current_filament
        self.__filament_usage = 0
    
    def calculate_fee(self, user, amount, duration): pass

class LaserCutter(Equipment):
    def __init__(self, resource_id, location, current_material):
        super().__init__(resource_id, EquipmentType.LASER_CUTTER, Expertise.LASER_CUTTER, location)
        self.__current_material = current_material
        self.__material_usage = 0
    
    def calculate_fee(self, user, amount, duration): pass

    def check_reservable(self, start_time, end_time, amount):
        if not (self.get_status == ResourceStatus.AVAILABLE): return False
        if not (self.check_schedule(start_time, end_time)): return False
        
        diff = end_time - start_time
        mins = diff.total_seconds() / 60
        if mins < 15: return False

        return True

class ToolSet(Equipment):
    def __init__(self, resource_id, required_cert, location, tool_count):
        super().__init__(resource_id, EquipmentType.TOOL_SET, required_cert, location)
        self.__tool_count = tool_count

    def calculate_fee(self, user, amount, duration): pass

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
    
    def calculate_fee(self, user, amount, duration): 
        total = amount * self.COST_PER_UNIT * (1 - user.get_discount)
        return total

    def validate_access(self, user, amount, start_time, end_time, line_item_list): pass

    def check_reservable(self, start_time, end_time, amount):
        if not (self.get_status == ResourceStatus.AVAILABLE): return False
        if self.__stock_qty - amount < 0: return False

        return True
    def show_detail(self):
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