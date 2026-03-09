from enum_class import ResourceStatus, SpaceType, Expertise, EquipmentType

class Resource:
    def __init__(self, resource_id):
        self.__resource_id = resource_id
        self.__status = ResourceStatus.AVAILABLE
        self.__reserved_time_list = []

    def update_status(self, status: ResourceStatus): self.__status = status
    def check_status(self): pass

    def calculate_fee(self, user_id, amount, duration): pass

    def validate_access(self, user, amount, start_time, end_time, line_item_list): pass

class Space(Resource):
    def __init__(self, resource_id, space_type: SpaceType, capacity, valid_time):
        super().__init__(resource_id)
        self.__space_type = space_type
        self.__capacity = capacity
        self.__valid_time = valid_time
    
    def calculate_fee(self, user_id, amount, duration): pass

    def validate_access(self, user, amount, start_time, end_time, line_item_list): pass

class Equipment(Resource):
    def __init__(self, resource_id, eq_type, required_cert: Expertise, location: Space):
        super().__init__(resource_id)
        self.__eq_type = eq_type
        self.__required_cert = required_cert
        self.__location = location

    def calculate_fee(self, user_id, amount, duration): pass

    def validate_access(self, user, amount, start_time, end_time, line_item_list): pass

class ThreeDPrinter(Equipment):
    def __init__(self, resource_id, location, current_filament):
        super().__init__(resource_id, EquipmentType.THREE_D_PRINTER, Expertise.THREE_D_PRINTER, location)
        self.__current_filament = current_filament
        self.__filament_usage = 0
    
    def calculate_fee(self, user_id, amount, duration): pass

class LaserCutter(Equipment):
    def __init__(self, resource_id, location, current_material):
        super().__init__(resource_id, EquipmentType.LASER_CUTTER, Expertise.LASER_CUTTER, location)
        self.__current_material = current_material
        self.__material_usage = 0
    
    def calculate_fee(self, user_id, amount, duration): pass

class ToolCount(Equipment):
    def __init__(self, resource_id, required_cert, location, tool_count):
        super().__init__(resource_id, EquipmentType.TOOL_SET, required_cert, location)
        self.__tool_count = tool_count

    def calculate_fee(self, user_id, amount, duration): pass

class Material(Resource):
    def __init__(self, resource_id, stock_qty, unit_name, minimum_stock, supported_machine: EquipmentType):
        super().__init__(resource_id)
        self.__stock_qty = stock_qty
        self.__unit_name = unit_name
        self.__minimum_stock = minimum_stock
        self.__supported_machine = supported_machine
    
    def calculate_fee(self, user_id, amount, duration): pass

    def validate_access(self, user, amount, start_time, end_time, line_item_list): pass


class Filament(Material):
    def __init__(self, resource_id, stock_qty, unit_name, minimum_stock, filament_type, diameter, color):
        super().__init__(resource_id, stock_qty, unit_name, minimum_stock, EquipmentType.THREE_D_PRINTER)
        self.__filament_type = filament_type
        self.__diameter = diameter
        self.__color = color
    
    def calculate_fee(self, user_id, amount, duration): pass

class Acrylic(Material):
    def __init__(self, resource_id, stock_qty, unit_name, minimum_stock, thickness, dimension, color):
        super().__init__(resource_id, stock_qty, unit_name, minimum_stock, EquipmentType.LASER_CUTTER)
        self.__thickness = thickness
        self.__dimension = dimension
        self.__color = color
    
    def calculate_fee(self, user_id, amount, duration): pass
    
class Plank(Material):
    def __init__(self, resource_id, stock_qty, unit_name, minimum_stock, wood_type, thickness):
        super().__init__(resource_id, stock_qty, unit_name, minimum_stock, EquipmentType.LASER_CUTTER)
        self.__wood_type = wood_type
        self.__thickness = thickness
    
    def calculate_fee(self, user_id, amount, duration): pass