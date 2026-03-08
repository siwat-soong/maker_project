from abc import ABC, abstractmethod
from enum_class import ResourceStatus, SpaceType, EquipmentType, Expertise
from datetime import time

class Resource(ABC):
    def __init__(self, resource_id):
        self.__resource_id = resource_id
        self.__status = ResourceStatus.AVAILABLE
    
    @property
    def get_id(self):
        return self.__resource_id
    
    @property
    def get_status(self):
        return self.__status
    
    def update_status(self, status):
        if isinstance(status, ResourceStatus):
            self.__status = status
    
    def check_status(self, status):
        if isinstance(status, ResourceStatus) and status == self.__status: return True
        else: return False
    
    @abstractmethod
    def calculate_fee(self, user, amount, duration):
        pass

    @abstractmethod
    def validate_access(self, user, amount, start_time, end_time, line_item_list):
        pass

class Space(Resource):
    def __init__(self, resource_id, space_type, capacity, opening_time, closing_time):
        super().__init__(resource_id)
        self.__space_type = self.__validate_input_type(space_type, SpaceType)
        self.__capacity = self.__validate_input_capacity(capacity)
        self.__opening_time = self.__validate_input_type(opening_time, time)
        self.__closing_time = self.__validate_input_type(closing_time, time)

    # Input Validation
    def __validate_input_type(self, obj, obj_type):
        if isinstance(obj, obj_type): return obj
        else: raise TypeError(f"{obj} Type not in the list")
    
    def __validate_input_capacity(self, capacity):
        try:
            if int(capacity) > 0: return capacity
            else: raise Exception()
        except: raise ValueError("Capacity must be positive integer")

    
    # Abstract Method
    def calculate_fee(self, user, amount, duration):
        pass
    
    def validate_access(self, user, amount, start_time, end_time, line_item_list):
        pass

    #show detail
    def show_detail(self):
        return {
            "resource_id": self.get_id,
            "category": "Space",
            "space_type": self.__space_type.value if hasattr(self.__space_type, 'value') else self.__space_type,
            "capacity": self.__capacity,
            # รวมเวลาเปิด-ปิดให้อ่านง่ายขึ้น
            "operating_hours": f"{self.__opening_time.strftime('%H:%M')} - {self.__closing_time.strftime('%H:%M')}"
        }
class Equipment(Resource):
    def __init__(self, resource_id, required_cert, eq_type):
        super().__init__(resource_id)
        self.__required_cert = self.__validate_input_specific_type(required_cert, Expertise)
        self.__eq_type = self.__validate_input_specific_type(eq_type, EquipmentType)
    
    # Input Validation
    def __validate_input_specific_type(self, obj, obj_type):
        if obj is None or isinstance(obj, obj_type): return obj
        else: raise TypeError(f"{obj} is not appropriate type")
    
    @property
    def get_eq_type(self):
        return self.__eq_type
    
    # Abstract Method
    def calculate_fee(self, user, amount, duration):
        pass
    
    def validate_access(self, user, amount, start_time, end_time, line_item_list):
        pass

    def show_detail(self):
        return {
            "resource_id": self.get_id,
            "category": "Equipment",
            "equipment_type": self.__eq_type.value if hasattr(self.__eq_type, 'value') else self.__eq_type,
            "required_cert": self.__required_cert.value if hasattr(self.__required_cert, 'value') else self.__required_cert
        }

class ThreeDPrinter(Equipment):
    def __init__(self, resource_id, required_cert, eq_type, print_volume, current_filament):
        super().__init__(resource_id, required_cert, eq_type)
        self.__print_volume = print_volume
        self.__current_filament = self.__validate_input_current_filament(current_filament)
        self.__filament_usage = 0
    
    # Input validation
    def __validate_input_current_filament(self, filament):
        if filament is None or isinstance(filament, Filament): return filament
        else: raise TypeError("Please insert filament only")
    
    # Abstract Method
    def calculate_fee(self, user, amount, duration):
        pass

class LaserCutter(Equipment):
    def __init__(self, resource_id, required_cert, eq_type, work_area_size, current_material):
        super().__init__(resource_id, required_cert, eq_type)
        self.__print_volume = work_area_size
        self.__current_filament = self.__validate_input_current_material(current_material)
        self.__filament_usage = 0
    
    # Input validation
    def __validate_input_current_material(self, material):
        if material is None or (isinstance(material, Material) and material.get_supported_machine == self.get_eq_type): return material
        else: raise TypeError("Please insert appropriate material")
    
    # Abstract Method
    def calculate_fee(self, user, amount, duration):
        pass

class ToolSet(Equipment):
    def __init__(self, resource_id, required_cert, eq_type, tool_count):
        super().__init__(resource_id, required_cert, eq_type)
        self.__tool_count = self.__validate_input_positive_amount(tool_count)
    
    # Input Validation
    def __validate_input_positive_amount(self, tool_count):
        try:
            if float(tool_count) > 0: return tool_count
            else: raise Exception()
        except: raise ValueError("Count must greater than 0")
    
    # Abstract Method
    def calculate_fee(self, user, amount, duration):
        pass

class Material(Resource):
    def __init__(self, resource_id, stock_qty, unit_name, minimum_stock, supported_machine):
        super().__init__(resource_id)
        self.__stock_qty = self.__validate_input_positive_amount(stock_qty)
        self.__unit_name = unit_name
        self.__minimum_stock = self.__validate_input_positive_amount(minimum_stock)
        self.__supported_machine = self.__validate_input_supported_machine(supported_machine)
    
    # Input Validation
    def __validate_input_positive_amount(self, stock_qty):
        try:
            if float(stock_qty) >= 0: return stock_qty
            else: raise Exception()
        except: raise ValueError("Amount in stock must equal or greater than 0")
    
    def __validate_input_supported_machine(self, machine):
        if isinstance(machine, EquipmentType): return machine
        else: raise TypeError(f"{machine} is not appropriate type")
    
    @property
    def get_supported_machine(self):
        return self.__supported_machine
    
    @property
    def unit_name(self):
        return self.__unit_name
    
    @property
    def stock_qty(self):
        return self.__stock_qty

    # Abstract Method
    def calculate_fee(self, user, amount, duration):
        pass
    
    def validate_access(self, user, amount, start_time, end_time, line_item_list):
        pass

    def check_deductible(self, amount):
        try:
            if float(amount) >= 0:
                if self.__stock_qty >= amount  and self.__stock_qty - amount >= self.__minimum_stock: return True
                else: return False
            else: raise Exception()
        except: raise ValueError("Amount deduct must equal or greater than 0")
    
    def deduct(self, amount):
        try:
            if float(amount) >= 0: self.__stock_qty -= amount
            else: raise Exception()
        except: raise ValueError("Amount deduct must equal or greater than 0")
    
    def restock(self, amount):
        try:
            if float(amount) >= 0: self.__stock_qty += amount
            else: raise Exception()
        except: raise ValueError("Amount restock must equal or greater than 0")

class Filament(Material):
    def __init__(self, resource_id, stock_qty, unit_name, minimum_stock, supported_machine, filament_type, diameter, color):
        super().__init__(resource_id, stock_qty, unit_name, minimum_stock, supported_machine)
        self.__filament_type = filament_type
        self.__diameter = self.__validate_input_diameter(diameter)
        self.__color = color
    
    # Input Validation
    def __validate_input_diameter(self, diameter):
        try:
            if float(diameter) > 0: return diameter
            else: raise Exception()
        except: raise ValueError("Diameter must greater than 0")

    def calculate_fee(self, user, amount, duration):
        pass
    def show_detail(self):
        return {
            "resource_id": self.get_id,
            "category": "Material",
            "material_name": "Filament",
            "filament_type": self.__filament_type,
            "diameter": self.__diameter,
            "color": self.__color,
            "stock_quantity": f"{self.stock_qty} {self.unit_name}" # รวมตัวเลขกับหน่วยเข้าด้วยกัน
        }

class Acrylic(Material):
    def __init__(self, resource_id, stock_qty, unit_name, minimum_stock, supported_machine, thickness, color, dimension):
        super().__init__(resource_id, stock_qty, unit_name, minimum_stock, supported_machine)
        self.__diameter = self.__validate_input_thickness(thickness)
        self.__color = color
        self.__dimension = dimension
    
    # Input Validation
    def __validate_input_thickness(self, thickness):
        try:
            if float(thickness) > 0: return thickness
            else: raise Exception()
        except: raise ValueError("Thickness must greater than 0")

    def calculate_fee(self, user, amount, duration):
        pass
    def show_detail(self):
        return {
            "resource_id": self.get_id,
            "category": "Material",
            "material_name": "Acrylic",
            "thickness": self.__diameter, # ในโค้ดคุณเก็บความหนาไว้ใน __diameter
            "color": self.__color,
            "dimension": self.__dimension,
            "stock_quantity": f"{self.stock_qty} {self.unit_name}"
        }

class Plank(Material):
    def __init__(self, resource_id, stock_qty, unit_name, minimum_stock, supported_machine, thickness, wood_type):
        super().__init__(resource_id, stock_qty, unit_name, minimum_stock, supported_machine)
        self.__diameter = self.__validate_input_thickness(thickness)
        self.__wood_type = wood_type
    
    # Input Validation
    def __validate_input_thickness(self, thickness):
        try:
            if float(thickness) > 0: return thickness
            else: raise Exception()
        except: raise ValueError("Thickness must greater than 0")

    def calculate_fee(self, user, amount, duration):
        pass
    def show_detail(self):
        return {
            "resource_id": self.get_id,
            "category": "Material",
            "material_name": "Plank",
            "wood_type": self.__wood_type,
            "thickness": self.__diameter, # ในโค้ดคุณเก็บความหนาไว้ใน __diameter
            "stock_quantity": f"{self.stock_qty} {self.unit_name}"
        }