from datetime import time
from user_class import *
from enum_class import *
from resource_class import *
from payment_class import *
from event_class import *
from transaction import *

class Club:
    def __init__(self, name):
        self.__name = name
        self.__user_list = []
        self.__instructor_list = []
        self.__admin_list = []
        self.__space_list = []
        self.__equipment_list = []
        self.__material_list = []
        self.__payment_method_list = []
        self.__event_list = []
    
    # Add Method
    def add_user(self, user):
        if isinstance(user, User):
            self.__user_list.append(user)

    def add_instructor(self, instructor):
        if isinstance(instructor, Instructor):
            self.__instructor_list.append(instructor)

    def add_admin(self, admin):
        if isinstance(admin, Admin):
            self.__admin_list.append(admin)
    
    def add_resource(self, resource):
        if isinstance(resource, Space): self.__space_list.append(resource)
        elif isinstance(resource, Equipment): self.__equipment_list.append(resource)
        elif isinstance(resource, Material): self.__material_list.append(resource)
    
    def add_payment_method(self, payment_method):
        if isinstance(payment_method, PaymentMethod):
            self.__payment_method_list.append(payment_method)

    # Search Method
    def search_user_by_id(self, user_id):
        for user in self.__user_list:
            if user.get_id == user_id:
                return user
        return None
    
    def search_member_by_id(self, user_id):
        for user in self.__user_list:
            if isinstance(user, Member) and user.get_id == user_id:
                return user
        return None

    def search_resource_by_id(self, resource_id):
        for space in self.__space_list: 
            if space.get_id == resource_id: return space
        for eq in self.__equipment_list: 
            if eq.get_id == resource_id: return eq
        for mat in self.__material_list: 
            if mat.get_id == resource_id: return mat
        return None


# Init Function
def system_init():
    try:
        # Create Instance
        maker = Club("maker")
        thana = Instructor("123", "Thana", "0123456789", Expertise.ADVANCE, 500)
        jira = Guest("123", "Jira", "0123456789")
        lab_a = Space("LAB-001", SpaceType.LABORATORY, 10, time(10, 0), time(22, 0))
        red_filament = Filament("MAT-001", 2000, "grams", 0, EquipmentType.THREE_D_PRINTER, "PLA", 0.2, "RED")
        printer_a = ThreeDPrinter("3DP-001", Expertise.THREE_D_PRINTER, EquipmentType.THREE_D_PRINTER, "20x20", red_filament)
        wooden_plank = Plank("WDP-001", 10, "plate", 0, EquipmentType.LASER_CUTTER, 5, "SOFT")
        acrylic_a = Acrylic("ACL-001", 20, "plate", 0, EquipmentType.LASER_CUTTER, 2, "CLEAR", "20x20")
        laser_cutter_a = LaserCutter("LSC-001", Expertise.LASER_CUTTER, EquipmentType.LASER_CUTTER, "120x120", None)
        tool_set_a = ToolSet("TOOL-001", Expertise.BASIC, EquipmentType.TOOL_SET, 5)
        cash_machine = Cash()
        qr_machine = QRCode()

        # Add Instance
        maker.add_user(jira)
        maker.add_instructor(thana)
        maker.add_resource(lab_a)
        maker.add_resource(red_filament)
        maker.add_resource(printer_a)
        maker.add_resource(wooden_plank)
        maker.add_resource(acrylic_a)
        maker.add_resource(laser_cutter_a)
        maker.add_resource(tool_set_a)
        maker.add_payment_method(cash_machine)
        maker.add_payment_method(qr_machine)


        print("-"*10, "✅ Init Success ", sep=" ", end="-"*10)
        print("\n")
    except Exception as e:
        print("-"*10, "❌ Init Failed ", sep=" ", end="-"*10)
        print(f"\n - {e}")

# test run - delete when use with API
system_init()