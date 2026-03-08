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
        self.__notification = []
    
    # Add Method
    def add_user(self, user):
        from user_class import User
        if isinstance(user, User):
            self.__user_list.append(user)

    def add_instructor(self, instructor):
        from user_class import Instructor
        if isinstance(instructor, Instructor):
            self.__instructor_list.append(instructor)

    def add_admin(self, admin):
        from user_class import Admin
        if isinstance(admin, Admin):
            self.__admin_list.append(admin)
    
    def add_member(self,member):
        pass
    
    def add_resource(self, resource):
        from resource_class import (Space , Equipment, Material)
        if isinstance(resource, Space): self.__space_list.append(resource)
        elif isinstance(resource, Equipment): self.__equipment_list.append(resource)
        elif isinstance(resource, Material): self.__material_list.append(resource)
    
    def add_payment_method(self, payment_method):
        from payment_class import PaymentMethod
        if isinstance(payment_method, PaymentMethod):
            self.__payment_method_list.append(payment_method)

    def add_event(self, event):
        from event_class import Event
        if isinstance(event, Event):
            self.__event_list.append(event)
    
    def add_notification(self,noti):
        self.__notification.append(noti)
            
    # Search Method
    def search_user_by_id(self, user_id):
        from user_class import User 
        for user in self.__user_list:
            if user.get_id == user_id:
                return user
        return None
    
    def search_member_by_id(self, user_id):
        from enum_class import UserRole
        for user in self.__user_list:
            if (user.get_role == UserRole.ANNUALMEMBER ) and user.get_id == user_id:
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
    
    def reserve(self, user_id):
        from enum_class import ResourceStatus
        from resource_class import Material
        from transaction import Invoice, Notification, Reservation
        # ==========================================

        target_user = None
        for user in self.__user_list:
            if user.get_id == user_id: 
                target_user = user
                break
        
        if target_user is None:
            return {"status": "error", "message": "This user is not found"}

        cart = target_user.line_item_list
        
        if not cart:
            return {"status": "error", "message": "cart is empty"}

        booking_list = []
        purchase_list = []

    
        for line_item in cart:
            qty = line_item.get_qty
            item = line_item.get_item

            item.update_resource(ResourceStatus.RESERVE, qty)

        
            if isinstance(item, Material):
                if item.stock_qty <= item.minimum_stock: 
                    noti_detail = f"{item.unit_name} is running out of stock!"
                    club_noti = Notification(self, "Out Min Stock", noti_detail)
                    self.add_notification(club_noti)
                
                purchase_list.append(line_item)
            else:
                booking_list.append(line_item)

        if purchase_list:
            invoice = Invoice(target_user, purchase_list)
            target_user.add_invoice(invoice)

        if booking_list:
            reservation = Reservation(target_user, booking_list)
            target_user.add_reservation(reservation)

       
        target_user.clear_cart()

        user_noti = Notification(target_user, "Reservation to Event or Equipment", booking_list)
        target_user.notify(user_noti)

    
        return {"status": "success", "message": "Reservation to Event or Equipment list success"}


# Init Function
def system_init():
    from datetime import time
    from controller import Club
    from enum_class import EquipmentType, Expertise, SpaceType
    from event_class import Event
    from payment_class import Cash, QRCode
    from resource_class import (
        Acrylic,
        Filament,
        LaserCutter,
        Plank,
        Space,
        ThreeDPrinter,
        ToolSet,
    )
    from user_class import Admin, Instructor, User
    
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
        room_a = Space("room-001", SpaceType.MEETING_ROOM,50,time(10, 0), time(22, 0))
        red_filament = Filament("MAT-001", 2000, "grams", 0, EquipmentType.THREE_D_PRINTER, "PLA", 0.2, "RED")
        printer_a = ThreeDPrinter("3DP-001", Expertise.THREE_D_PRINTER, EquipmentType.THREE_D_PRINTER, "20x20", red_filament)
        wooden_plank = Plank("WDP-001", 10, "plate", 0, EquipmentType.LASER_CUTTER, 5, "SOFT")
        acrylic_a = Acrylic("ACL-001", 20, "plate", 0, EquipmentType.LASER_CUTTER, 2, "CLEAR", "20x20")
        laser_cutter_a = LaserCutter("LSC-001", Expertise.LASER_CUTTER, EquipmentType.LASER_CUTTER, "120x120", None)
        tool_set_a = ToolSet("TOOL-001", Expertise.BASIC, EquipmentType.TOOL_SET, 5)
        cash_machine = Cash()
        qr_machine = QRCode()

        event1 = Event("EV-001", "Ossiliscope", "Introduction", amnach, lab_a, 10, 100, Expertise.ADVANCE)
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

        maker.add_event(event1)
        maker.add_member(jane.get_id)

        print("-"*10, "✅ Init Success ", sep=" ", end="-"*10)
        print("\n")

        return maker
    except Exception as e:
        print("-"*10, "❌ Init Failed ", sep=" ", end="-"*10)
        print(f"\n - {e}")