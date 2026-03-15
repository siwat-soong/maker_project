from _user import *
from _payment import *
from _resource import *
from _event import *

from datetime import time

class Club:
    def __init__(self):
        # User
        self.__user_list = []
        self.__instructor_list = []
        self.__admin_list = []
        
        # Resource
        self.__space_list = []
        self.__equipment_list = []
        self.__material_list = []

        # Event
        self.__event_list = []

        # Payment
        self.__payment_method_list = []
    
    def add_user(self, user: User): self.__user_list.append(user)
    def add_instructor(self, ins: Instructor): 
        self.__instructor_list.append(ins)
        self.__user_list.append(ins)
    def add_admin(self, admin: Admin): self.__admin_list.append(admin)
    def add_space(self, space: Space): self.__space_list.append(space)
    def add_equipment(self, equipment: Equipment): self.__equipment_list.append(equipment)
    def add_material(self, material: Material): self.__material_list.append(material)
    def add_event(self, event: Event): self.__event_list.append(event)
    def add_payment_method(self, payment_method: PaymentMethod): self.__payment_method_list.append(payment_method)

    @property
    def get_instructors(self): return self.__instructor_list

    @property
    def get_spaces(self): return self.__space_list
    @property
    def get_equipments(self): return self.__equipment_list
    @property
    def get_materials(self): return self.__material_list

    @property
    def get_events(self): return self.__event_list

    def search_user_from_id(self, uid: str):
        for user in self.__user_list:
            if user.get_id == uid: return user
        return None
    
    def search_admin_from_id(self, uid: str):
        for admin in self.__admin_list:
            if admin.get_id == uid: return admin
        return None
    
    def search_instructor_from_id(self, uid: str):
        for instructor in self.__instructor_list:
            if instructor.get_id == uid: return instructor
        return None

    def search_space_from_id(self, res_id: str):
        for sp in self.__space_list:
            if sp.get_id == res_id: return sp
        return None

    def search_equipment_from_id(self, res_id: str):
        for eq in self.__equipment_list:
            if eq.get_id == res_id: return eq
        return None
    
    def search_material_from_id(self, res_id: str):
        for mat in self.__material_list:
            if mat.get_id == res_id: return mat
        return None
    
    def search_event_from_id(self, event_id: str):
        for event in self.__event_list:
            if event.get_id == event_id: return event
        return None
    
    def search_payment_from_type(self, type: str):
        for pm in self.__payment_method_list:
            if pm.get_type.value == type: return pm
        return None
    
    def create_event(self, topic, detail, time, ins, space, items, max_attender, join_fee):
        event = Event(topic, detail, time, ins, space, items, max_attender, join_fee)
        self.__event_list.append(event)

def system_init():
    try:
        sys = Club()
        dummy1 = User("0001", "Alpha", "0123456789")
        cash = Cash(20000)
        qr = QRCode()

        god = User("0002", "God", "0999999999")
        for exp in [Expertise.ADVANCED, Expertise.THREE_D_PRINTER, Expertise.LASER_CUTTER]:
            god.add_certificate(Certification(god, None, exp))
        
        thana = Instructor("4244", "Thana", "0671799986", Expertise.THREE_D_PRINTER, 200)
        jirasak = Instructor("4245", "Jirasak", "0671799987", Expertise.LASER_CUTTER, 150)
        thanunchai = Instructor("4246", "Thanunchai", "0671799988", Expertise.ADVANCED, 100)
        amnach = Admin("3308", "Computer Engineering")
        orachat = Admin("3309", "Information Technology")

        lab_a = Space("SPA-LAB-001", SpaceType.LABORATORY, 30, time(6, 0), time(22, 0))
        lab_b = Space("SPA-LAB-002", SpaceType.LABORATORY, 30, time(6, 0), time(22, 0))
        desk_a = Space("SPA-DESK-001", SpaceType.HOT_DESK, 4, time(6, 0), time(22, 0))
        desk_b = Space("SPA-DESK-002", SpaceType.HOT_DESK, 4, time(6, 0), time(22, 0))
        meet_a = Space("SPA-MEET-001", SpaceType.MEETING_ROOM, 10, time(6, 0), time(22, 0))
        meet_b = Space("SPA-MEET-002", SpaceType.MEETING_ROOM, 10, time(6, 0), time(22, 0))

        filament_a = Filament("MAT-PLA-001", 1000, "grams", 0, "PLA", 1.75, "RED")
        acrylic_a = Acrylic("MAT-ACR-001", 20, "sheets", 1, 5, "20x20", "CLEAR")
        plank_a = Plank("MAT-WOOD-001", 30, "sheets", 1, "PLYWOOD", 5)

        printer_a = ThreeDPrinter("EQM-3DP-001", lab_a, filament_a)
        laser_a = LaserCutter("EQM-LSC-001", lab_a, acrylic_a)
        tool_a = ToolSet("EQM-TOOL-001", Expertise.ADVANCED, desk_a, 10)
        tool_b = ToolSet("EQM-TOOL-002", Expertise.ADVANCED, None, 15)
        tool_c = ToolSet("EQM-TOOL-003", None, None, 20)

        sys.add_user(dummy1)
        sys.add_user(god)
        sys.add_instructor(thana)
        sys.add_instructor(jirasak)
        sys.add_instructor(thanunchai)
        sys.add_admin(amnach)
        sys.add_admin(orachat)
        sys.add_payment_method(cash)
        sys.add_payment_method(qr)

        sys.add_space(lab_a)
        sys.add_space(lab_b)  
        sys.add_space(desk_a)
        sys.add_space(desk_b)
        sys.add_space(meet_a)
        sys.add_space(meet_b)

        sys.add_material(filament_a)
        sys.add_material(acrylic_a)
        sys.add_material(plank_a)

        sys.add_equipment(laser_a)
        sys.add_equipment(printer_a)
        sys.add_equipment(tool_a)
        sys.add_equipment(tool_b)
        sys.add_equipment(tool_c)

        return sys
    
    except Exception as e:
        print(f"{e}")