from datetime import datetime, time
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
        res = self.search_space_by_id(resource_id)
        if res is not None: return res
        res = self.search_equipment_by_id(resource_id)
        if res is not None: return res
        res = self.search_material_by_id(resource_id)
        if res is not None: return res

    # List Properties
    @property
    def get_space_list(self): return self.__space_list

    @property
    def get_equipment_list(self): return self.__equipment_list

    @property
    def get_material_list(self): return self.__material_list

    @property
    def get_event_list(self): return self.__event_list

    # Notification Methods
    def notify(self, user, topic, detail):
        from transaction_class import Notification
        user.add_notification(Notification(user, topic, detail))

    def broadcast(self, topic, detail):
        from transaction_class import Notification
        for user in self.__user_list:
            user.add_notification(Notification(user, topic, detail))
        for ins in self.__instructor_list:
            ins.add_notification(Notification(ins, topic, detail))\
    
    def remove_event(self, event):
        if event in self.__event_list:
            space = event.get_space
            time_range = event.get_time
            if space and time_range:
                space.cancel_reserve(time_range)
            
            instructor = event.get_instructor
            if instructor and time_range:
                instructor.remove_schedule(time_range)
            
            for item in event.get_item_list:
                resource = item.get_resource
                item_time = item.get_reserved_time
                if hasattr(resource, 'cancel_reserve'):
                    resource.cancel_reserve(item_time)
                    
            self.__event_list.remove(event)
            return True
        return False

def system_init():
    try:
        maker = Club("Maker Club")
        butter = User("4517", "Butter", "0144796685")
        akiko = User("9999", "Akiko", "0800000000")
        god = User("0001", "God", "0999999999")
        from event_class import Certification
        for exp in [Expertise.ADVANCED, Expertise.THREE_D_PRINTER, Expertise.LASER_CUTTER]:
            god.add_certificate(Certification(god, None, exp))
        thana = Instructor("4244", "Thana", "0671799986", Expertise.THREE_D_PRINTER, 200)
        jirasak = Instructor("4245", "Jirasak", "0671799987", Expertise.LASER_CUTTER, 150)
        thanunchai = Instructor("4246", "Thanunchai", "0671799988", Expertise.ADVANCED, 100)
        amnach = Admin("3308", "Computer Engineering")
        orachat = Admin("3309", "Information Technology")
        cash = Cash("C-0001", 3000)
        qr = QRCode("Q-0001")

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
        tool_b = ToolSet("EQM-TOOL-002", None, desk_a, 15)

        maker.add_user(butter)
        maker.add_user(akiko)
        maker.add_user(god)
        maker.add_instructor(thana)
        maker.add_instructor(jirasak)
        maker.add_instructor(thanunchai)
        maker.add_admin(amnach)
        maker.add_admin(orachat)
        maker.add_payment_method(cash)
        maker.add_payment_method(qr)

        maker.add_space(lab_a)
        maker.add_space(lab_b)  
        maker.add_space(desk_a)
        maker.add_space(desk_b)
        maker.add_space(meet_a)
        maker.add_space(meet_b)

        maker.add_material(filament_a)
        maker.add_material(acrylic_a)
        maker.add_material(plank_a)

        maker.add_equipment(printer_a)
        maker.add_equipment(laser_a)
        maker.add_equipment(tool_a)
        maker.add_equipment(tool_b)

        print("✅ Init Success")
        return maker
    except:
        print("⛔ Init Failed")
        