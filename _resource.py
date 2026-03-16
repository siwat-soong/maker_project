from _enum import ResourceStatus, EquipmentType, ReserveType, SpaceType, Expertise, UserRole
from abc import ABC, abstractmethod

class Resource(ABC):
    def __init__(self, resource_id: str, reserve_type: ReserveType):
        self.__resource_id = resource_id
        self.__status = ResourceStatus.AVAILABLE
        self.__rsv_type = reserve_type
    
    @property
    def get_id(self): return self.__resource_id

    @property
    def get_status(self): return self.__status

    @property
    def get_rsv_type(self): return self.__rsv_type

    @abstractmethod
    def validate(self, user, amount, start_time, end_time): pass

    def detail(self): return {
        "ID": self.__resource_id,
        "STATUS": self.__status,
        "TYPE": self.__rsv_type
    }

    def update_status(self, status): self.__status = status

    def process_cart(self): return [self]
    def to_cancel(self): return [self]

class Space(Resource):
    GUEST_RATE_PER_HR  = 50
    MEMBER_FREE_HR = 2
    MEMBER_RATE_PER_HR = 20

    def __init__(self, resource_id, space_type: SpaceType, capacity, valid_start_time, valid_end_time):
        super().__init__(resource_id, ReserveType.RESERVE)
        self.__space_type = space_type
        self.__capacity = capacity
        self.__valid_start_time = valid_start_time
        self.__valid_end_time = valid_end_time
        self.__schedule = []
        self.__equipment_in_space = []
    
    def detail(self):
        data = super().detail()
        data.update({
            "CAPACITY": self.__capacity,
            "OPEN": self.__valid_start_time.strftime("%d-%m-%Y %H:%M"),
            "CLOSE": self.__valid_end_time.strftime("%d-%m-%Y %H:%M"),
            "EQUIPMENTS": [x.get_id for x in self.__equipment_in_space] if self.__equipment_in_space else None
            })
        return data

    @property
    def get_eq(self): return self.__equipment_in_space

    @property
    def get_capacity(self): return self.__capacity

    def check_available(self, start_time, end_time):
        if start_time.time() < self.__valid_start_time or end_time.time() > self.__valid_end_time: return False
        if self.__schedule:
            for t in self.__schedule:
                if t.check_overlap(start_time, end_time): return False
        if self.get_status != ResourceStatus.AVAILABLE: return False
        return True
    
    def assign_eq(self, eq): self.__equipment_in_space.append(eq)

    def add_schedule(self, time): self.__schedule.append(time)
    def remove_schedule(self, time): self.__schedule.remove(time)
    
    def validate(self, user, amount, start_time, end_time):
        if start_time.time() < self.__valid_start_time or end_time.time() > self.__valid_end_time: return False
        if self.__schedule:
            for t in self.__schedule:
                if t.check_overlap(start_time, end_time): return False
        if self.get_status != ResourceStatus.AVAILABLE: return False

        for eq in self.__equipment_in_space:
            if not eq.validate(user, amount, start_time, end_time): return False

        return True
    
    def calculate_fee(self, user, amount, duration):
        if self.__space_type == SpaceType.LABORATORY:
            return 0
        hours = duration / 60
        if user.get_role == UserRole.MEMBER:
            billable_hours = max(0, hours - self.MEMBER_FREE_HR)
            total = billable_hours * self.MEMBER_RATE_PER_HR
        else:
            total = hours * self.GUEST_RATE_PER_HR
        return round(total, 2)
    
    def process_cart(self):
        res = [self]
        for eq in self.__equipment_in_space:
            res.append(eq)
        return res
    
    def to_cancel(self):
        res = [self]
        for eq in self.__equipment_in_space:
            res.append(eq)
        return res
    

class Equipment(Resource):
    def __init__(self, resource_id, eq_type, required_cert: Expertise, location: Space):
        super().__init__(resource_id, ReserveType.RESERVE)
        self.__eq_type = eq_type
        self.__required_cert = required_cert
        self.__location = location
        if self.__location is not None: self.__location.assign_eq(self) 
        self.__schedule = []
    
    def detail(self):
        data = super().detail()
        data.update({
            "REQUIRED CERTIFIED": self.__required_cert,
            "LOCATION": self.__location.get_id if self.__location else None
            })
        return data
    
    @property
    def get_cert(self): return self.__required_cert

    @property
    def get_schedule(self): return self.__schedule

    @property
    def free_condition(self): return self.__location is None

    def check_available(self, start_time, end_time):
        if self.__schedule:
            for t in self.__schedule:
                if t.check_overlap(start_time, end_time): return False
        if self.get_status != ResourceStatus.AVAILABLE: return False
        return True

    def add_schedule(self, time): self.__schedule.append(time)
    def remove_schedule(self, time): self.__schedule.remove(time)
    
    def calculate_fee(self, user, amount, duration): pass
    
    def validate(self, user, amount, start_time, end_time):
        if self.__schedule:
            for t in self.__schedule:
                if t.check_overlap(start_time, end_time): return False
        if self.get_status != ResourceStatus.AVAILABLE: return False
        if not user.check_expertise(self.__required_cert): return False

        return True

class ThreeDPrinter(Equipment):
    RATE_MEMBER = 0.5
    RATE_GUEST  = 1.0
    OWN_MATERIAL_SURCHARGE = 0.20

    def __init__(self, resource_id, location, current_filament):
        super().__init__(resource_id, EquipmentType.THREE_D_PRINTER, Expertise.THREE_D_PRINTER, location)
        self.__current_filament = current_filament
        self.__filament_usage = 0
        self.__own_material_trigger = False
    
    def use(self, amount: float): 
        if not amount: raise Exception("ต้องระบุจำนวนวัสดุที่ใช้")
        self.__filament_usage += amount
    
    def add_own(self): self.__own_material_trigger = True
    
    def calculate_fee(self, user, amount, duration):
        surcharge = 0
        material_fee = 0
        machine_fee = 0
        damage = 0

        rate = self.RATE_MEMBER if user.get_role == UserRole.MEMBER else self.RATE_GUEST
        if self.__filament_usage > 0 or self.__own_material_trigger: machine_fee = duration * rate
        if self.__own_material_trigger: surcharge = machine_fee * self.OWN_MATERIAL_SURCHARGE
        material_fee = self.__current_filament.calculate_fee(user, self.__filament_usage, duration)
        total = round(machine_fee + material_fee + surcharge, 2)
        if self.get_status == ResourceStatus.MAINTENANCE: damage = total * 0.5

        self.__filament_usage = 0
        self.__own_material_trigger = False
        return total + damage

class LaserCutter(Equipment):
    RATE_MEMBER = 5.0
    RATE_GUEST  = 10.0
    OWN_MATERIAL_SURCHARGE = 0.20

    def __init__(self, resource_id, location, current_material):
        super().__init__(resource_id, EquipmentType.LASER_CUTTER, Expertise.LASER_CUTTER, location)
        self.__current_material = current_material
        self.__material_usage = 0
        self.__own_material_trigger = False

    def use(self, amount: float): 
        if not amount: raise Exception("ต้องระบุจำนวนวัสดุที่ใช้")
        self.__material_usage += amount
    
    def add_own(self): self.__own_material_trigger = True
    
    def calculate_fee(self, user, amount, duration):
        surcharge = 0
        material_fee = 0
        machine_fee = 0
        damage = 0

        rate = self.RATE_MEMBER if user.get_role == UserRole.MEMBER else self.RATE_GUEST
        if self.__material_usage > 0 or self.__own_material_trigger: machine_fee  = duration * rate
        if self.__own_material_trigger: surcharge = machine_fee * self.OWN_MATERIAL_SURCHARGE
        material_fee = self.__current_material.calculate_fee(user, self.__material_usage, duration)
        total = round(machine_fee + material_fee + surcharge, 2)
        if self.get_status == ResourceStatus.MAINTENANCE: damage = total * 0.5

        self.__material_usage = 0
        self.__own_material_trigger = False
        return total + damage
    
    def validate(self, user, amount, start_time, end_time):
        dur = end_time - start_time
        if dur.total_seconds() / 60 < 15: return False
        if self.get_schedule:
            for t in self.get_schedule:
                if t.check_overlap(start_time, end_time): return False
        if self.get_status != ResourceStatus.AVAILABLE: return False
        if not user.check_expertise(self.get_cert): return False        
        return True

class ToolSet(Equipment):
    RATE_PER_HR_PER_TOOL = 30

    def __init__(self, resource_id, required_cert, location, tool_count):
        super().__init__(resource_id, EquipmentType.TOOL_SET, required_cert, location)
        self.__tool_count = tool_count
    
    def use(self, amount: float): pass

    def calculate_fee(self, user, amount, duration):
        damage = 0
        hours = duration / 60
        total = hours * self.RATE_PER_HR_PER_TOOL
        if self.get_status == ResourceStatus.MAINTENANCE: damage = total * 0.5
        return total + damage



class Material(Resource):
    COST_PER_UNIT = 0
    def __init__(self, resource_id, stock_qty: float, unit_name, minimum_stock, supported_machine: EquipmentType):
        super().__init__(resource_id, ReserveType.INSTANT_PAY)
        self.__stock_qty = stock_qty
        self.__unit_name = unit_name
        self.__minimum_stock = minimum_stock
        self.__supported_machine = supported_machine
    
    @property
    def get_stock_qty(self): return self.__stock_qty

    def check_available(self, start_time, end_time):
        if self.get_status != ResourceStatus.AVAILABLE: return False
        return True
    
    def deduct(self, amount: float):
        if self.__stock_qty - amount < self.__minimum_stock: raise Exception("ไม่สามารถตัดสต็อกได้")
        if self.__stock_qty - amount == self.__minimum_stock: self.update_status(ResourceStatus.OUT_OF_STOCK)
        self.__stock_qty -= amount

        print(self.__stock_qty)
    
    def restock(self, amount: float):
        self.__stock_qty += amount
        if self.__stock_qty > self.__minimum_stock: self.update_status(ResourceStatus.AVAILABLE)
    
    def calculate_fee(self, user, amount): 
        total = amount * self.COST_PER_UNIT
        return total
    
    def validate(self, user, amount, start_time, end_time):
        if self.__stock_qty - amount < self.__minimum_stock: return False
        if self.get_status != ResourceStatus.AVAILABLE: return False
        return True

    def detail(self):
        data = super().detail()
        data.update({
            "STOCK": self.__stock_qty,
            "COST PER UNIT": self.COST_PER_UNIT
            })
        return data


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