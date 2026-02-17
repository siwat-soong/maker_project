from datetime import time
from user_class import *
from enum_class import *
from resource_class import *

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


# Init Function
def system_init():
    try:
        maker = Club("maker")
        
        thana = Instructor("123", "Thana", "0123456789", Expertise.ADVANCE, 500)
        jira = User("123", "Jira", "0123456789")
        
        lab_a = Space("LAB-001", SpaceType.LABORATORY, 10, time(10, 0), time(22, 0))
        
        red_filament = Filament("MAT-001", 2000, "grams", 0, EquipmentType.THREE_D_PRINTER, "PLA", 0.2, "RED")
        printer_a = ThreeDPrinter("3DP-001", Expertise.THREE_D_PRINTER, EquipmentType.THREE_D_PRINTER, "20x20", red_filament)

        wooden_plank = Plank("WDP-001", 10, "plate", 0, EquipmentType.LASER_CUTTER, 5, "SOFT")
        acrylic_a = Acrylic("ACL-001", 20, "plate", 0, EquipmentType.LASER_CUTTER, 2, "CLEAR", "20x20")
        laser_cutter_a = LaserCutter("LSC-001", Expertise.LASER_CUTTER, EquipmentType.LASER_CUTTER, "120x120", None)

        tool_set_a = ToolSet("TOOL-001", Expertise.BASIC, EquipmentType.TOOL_SET, 5)


        print("-"*5, " ✅ Init Success ", sep="", end="-"*5)
    except Exception as e:
        print(f"❌ {e}")

# test run - delete when use with API
system_init()