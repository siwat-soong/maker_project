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
        self.__notification_list = []
    
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

    def add_event(self, event):
        if isinstance(event, Event):
            self.__event_list.append(event)

    def add_notification(self, notification):
        if isinstance(notification,Notification):
            self.__notification_list.append(notification)

    def get_all_users(self):
        return self.__user_list
    
    def search_admin_by_id(self, admin_id):
        for admin in self.__admin_list:
            if admin.get_id == admin_id:
                return admin
        return None
    
    # Search Method
    def search_user_by_id(self, user_id):
        for user in self.__user_list:
            if user.get_id == user_id:
                return user
        return None
    
    def search_member_by_id(self, user_id):
        for user in self.__user_list:
            if (user.get_role == UserRole.ANNUALMEMBER ) and user.get_id == user_id:
                return user
        return None
    
    def search_instructor_by_id(self, user_id):
        for user in self.__instructor_list:
            if user.get_id == user_id:
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
    
    def search_all_matching_item(self, resource_id):
        all_match_item = list()
        for user in self.__user_list:
            for rsv in user.get_user_reservation:
                all_match_item.extend(rsv.list_all_match_line_item(resource_id))
        
        return all_match_item

    # def add_member(self, user_id):
    #     user = self.search_user_by_id(user_id)
    #     if not user:
    #         return "user not found"
    #     else: 
    #         if user.check_blacklist():
    #             return "You're blacklist"
    #         else: 
    #             user.change_role(UserRole.ANNUAL_MEMBER)
    #             user.create_invoice(user_id, None, None, None, Club.MEMBER_FEE)
    #             role = user.role.value
    #             return f"success! now you are {role}"

# Init Function
def system_init():
    try:
        # Create Instance
        maker = Club("maker")
        jane = User("USE-001","Jane","0123456789")
        jira = User("USE-002", "Jira", "0123456789")
        thana = Instructor("INS-001", "Thana", "0123456789", Expertise.ADVANCE, 500)
        amnach = Instructor("INS-002", "Amnach", "0123456789", Expertise.ADVANCE, 800)
        tom = Admin("ADM-001", "Tom", "reception")
        jerry = Admin("ADM002", "Jerry", "reception")
        lab_a = Space("LAB-001", SpaceType.LABORATORY, 10, time(10, 0), time(22, 0))
        desk_a = Space("DESK-001", SpaceType.HOT_DESK, 8, time(10, 0), time(22, 0))
        room_a = Space("ROOM-001", SpaceType.MEETING_ROOM,6, time(10, 0), time(22, 0))
        red_filament = Filament("MAT-001", 2000, "grams", 0, EquipmentType.THREE_D_PRINTER, "PLA", 0.2, "RED")
        printer_a = ThreeDPrinter("3DP-001", Expertise.THREE_D_PRINTER, EquipmentType.THREE_D_PRINTER, "20x20", red_filament)
        wooden_plank = Plank("WDP-001", 10, "plate", 0, EquipmentType.LASER_CUTTER, 5, "SOFT")
        acrylic_a = Acrylic("ACL-001", 20, "plate", 0, EquipmentType.LASER_CUTTER, 2, "CLEAR", "20x20")
        laser_cutter_a = LaserCutter("LSC-001", Expertise.LASER_CUTTER, EquipmentType.LASER_CUTTER, "120x120", None)
        tool_set_a = ToolSet("TOOL-001", None, EquipmentType.TOOL_SET, 5)
        cash_machine = Cash()
        qr_machine = QRCode()

        # event1 = Event("EV-001", "Ossiliscope", "Introduction", amnach, lab_a, 10, 100, Expertise.ADVANCE)
        
        # Add Instance
        maker.add_user(jane)
        maker.add_user(jira)
        maker.add_instructor(thana)
        maker.add_instructor(amnach)
        maker.add_admin(tom)
        maker.add_admin(jerry)
        maker.add_resource(lab_a)
        maker.add_resource(desk_a)
        maker.add_resource(room_a)
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

        return maker
    except Exception as e:
        print("-"*10, "❌ Init Failed ", sep=" ", end="-"*10)
        print(f"\n - {e}")

system_init()