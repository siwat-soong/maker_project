from datetime import datetime, time, timedelta

from user_class import User, Instructor, Admin
from payment_class import Cash, QRCode
from resource_class import Space, ThreeDPrinter, LaserCutter, ToolSet, Filament, Acrylic, Plank
from enum_class import SpaceType, Expertise
from transaction_class import TimeRange

class Club:
    def __init__(self, name):
        self.__name = name
        
        # User Storage
        self.__user_list = []
        self.__instructor_list = []
        self.__admin_list = []

        # Resource Storage
        self.__space_list = []
        self.__equipment_list = []
        self.__material_list = []

        # Payment Method Storage
        self.__payment_method_list = []

        # Event Storage
        self.__event_list = []
    
    # Add Method
    def add_user(self, user: User): self.__user_list.append(user)
    def add_instructor(self, instructor): self.__instructor_list.append(instructor)
    def add_admin(self, admin): self.__admin_list.append(admin)

    def add_space(self, space): self.__space_list.append(space)
    def add_equipment(self, equipment): self.__equipment_list.append(equipment)
    def add_material(self, material): self.__material_list.append(material)

    def add_payment_method(self, payment_method): self.__payment_method_list.append(payment_method)
    
    def add_event(self, event): self.__event_list.append(event)

    # Search Method
    def search_user_by_id(self, user_id):
        for user in self.__user_list:
            if user.get_id == user_id: return user
        return None
    
    def search_admin_by_id(self, admin_id):
        for admin in self.__admin_list:
            if admin.get_id == admin_id: return admin
        return None
    
    def search_instructor_by_id(self, instructor_id):
        for instructor in self.__instructor_list:
            if instructor.get_id == instructor_id: return instructor
        return None

    def search_method_by_id(self, method_id):
        for method in self.__payment_method_list:
            if method.get_id == method_id: return method
        return None
    
    def search_space_by_id(self, space_id):
        for space in self.__space_list:
            if space.get_id == space_id: return space
        return None
    
    def search_equipment_by_id(self, equipment_id):
        for equipment in self.__equipment_list:
            if equipment.get_id == equipment_id: return equipment
        return None
    
    def search_material_by_id(self, material_id):
        for material in self.__material_list:
            if material.get_id == material_id: return material
        return None
    
    def search_event_by_id(self, event_id):
        for event in self.__event_list:
            if event.get_id == event_id: return event
        return None

    def search_resource_by_id(self, resource_id):
        res = None

        res = self.search_space_by_id(resource_id)
        if res is not None: return res

        res = self.search_equipment_by_id(resource_id)
        if res is not None: return res

        res = self.search_material_by_id(resource_id)
        if res is not None: return res

def system_init():
    try:
        maker = Club("Maker Club")
        butter = User("4517", "Butter", "0144796685")
        thana = Instructor("4244", "Thana", "0671799986", Expertise.THREE_D_PRINTER, 200)
        amnach = Admin("3308", "Computer Engineering")
        cash = Cash("C-0001", 3000)
        qr = QRCode("Q-0001")

        lab_a = Space("SPA-LAB-001", SpaceType.LABORATORY, 30, time(6, 0), time(22, 0))
        desk_a = Space("SPA-DESK-001", SpaceType.HOT_DESK, 4, time(6, 0), time(22, 0))
        meet_a = Space("SPA-MEET-001", SpaceType.MEETING_ROOM, 10, time(6, 0), time(22, 0))

        filament_a = Filament("MAT-PLA-001", 1000, "grams", 0, "PLA", 1.75, "RED")
        acrylic_a = Acrylic("MAT-ACR-001", 20, "sheets", 1, 5, "20x20", "CLEAR")
        plank_a = Plank("MAT-WOOD-001", 30, "sheets", 1, "PLYWOOD", 5)

        printer_a = ThreeDPrinter("EQM-3DP-001", lab_a, filament_a)
        laser_a = LaserCutter("EQM-LSC-001", lab_a, acrylic_a)
        tool_a = ToolSet("EQM-TOOL-001", Expertise.ADVANCED, desk_a, 10)
        tool_b = ToolSet("EQM-TOOL-002", None, desk_a, 15)

    #     from event_class import Event
    #     from transaction_class import TimeRange
    
    #     # Mock Event 1 → ได้ WS-0001
    #     t1 = TimeRange(datetime(2026, 3, 20, 10, 0), datetime(2026, 3, 20, 16, 0))
    #     meet_a.process_reserve(1, t1)
    #     event1 = Event("3D Printing Workshop", "เรียนรู้การใช้ 3D Printer", t1, thana, meet_a, None, 10, 200, Expertise.THREE_D_PRINTER)
    #     maker.add_event(event1)

    # # Mock Event 2 → ได้ WS-0002
    #     t2 = TimeRange(datetime(2026, 3, 25, 13, 0), datetime(2026, 3, 25, 17, 0))
    #     event2 = Event("Laser Cutter Basic", "พื้นฐาน Laser Cutter", t2, thana, meet_a, None, 5, 150, Expertise.LASER_CUTTER)
    #     maker.add_event(event2)

        maker.add_user(butter)
        maker.add_instructor(thana)
        maker.add_admin(amnach)
        maker.add_payment_method(cash)
        maker.add_payment_method(qr)

        maker.add_space(lab_a)
        maker.add_space(desk_a)
        maker.add_space(meet_a)

        maker.add_material(filament_a)
        maker.add_material(acrylic_a)
        maker.add_material(plank_a)

        maker.add_equipment(printer_a)
        maker.add_equipment(laser_a)
        maker.add_equipment(tool_a)
        maker.add_equipment(tool_b)

        print("✅ Init Success")
        return maker
    except: print("⛔ Init Failed")