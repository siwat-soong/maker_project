from datetime import time, timedelta, datetime
import uuid
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

    def add_member(self, id):
        pass

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

    def search_resource_by_id(self, resource_id):
        for space in self.__space_list: 
            if space.get_id == resource_id: return space
        for eq in self.__equipment_list: 
            if eq.get_id == resource_id: return eq
        for mat in self.__material_list: 
            if mat.get_id == resource_id: return mat
        return None

    def get_user_list(self):
        return self.__user_list
        
    def get_resource_list(self):
        return self.__space_list + self.__equipment_list + self.__material_list

    def process_return(self, user_id: str, reservation_id: str, item_ids: list):
        target_user = next((u for u in self.__user_list if u.get_id == user_id), None)
        if not target_user:
            return {"error": "User not found"}

        target_reservation = target_user.search_reservation_by_id(reservation_id)
        if not target_reservation:
            return {"error": "Reservation not found"}

        # ตรวจว่าทุก item มีอยู่จริงก่อน
        target_items = []
        for item_id in item_ids:
            item = target_reservation.check_item(item_id)
            if not item:
                return {"error": f"Item not found: {item_id}"}
            target_items.append((item_id, item))

        # คืนทุกชิ้น รวม cost เป็น invoice เดียว
        total_cost = 0.0
        for item_id, _ in target_items:
            total_cost += target_reservation.return_items(item_id)

        invoice = Invoice(target_user, reservation=target_reservation, cost=total_cost)

        # pop items ออกหลัง return ครบแล้ว
        for _, item in target_items:
            target_reservation.pop_item(item)

        # ถ้ายอด 0 — ออกใบเสร็จเลย
        if total_cost == 0:
            from payment_class import Cash
            invoice.mark_as_paid()
            from transaction import Receipt
            receipt = Receipt(target_user, Cash(), invoice)
            target_user._User__receipt_list.append(receipt)
            target_user.add_invoice(invoice)
            return {
                "receipt_id": receipt.receipt_id,
                "cost": 0.0,
                "payment_status": "PAID",
                "message": f"Auto-paid (no charge) — {len(target_items)} item(s) returned"
            }

        invoice_info = target_user.add_invoice(invoice)
        invoice_info["returned_items"] = [i for i, _ in target_items]
        return invoice_info


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
        room_a = Space("room-001", SpaceType.MEETING_ROOM, 6, time(10, 0), time(22, 0))
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

        # ── Seed Reservations (ID คงที่ ไม่เปลี่ยนทุก restart) ────────
        now = datetime.now()

        # Jane ยืม 3D Printer และ Tool Set
        rsv_jane = Reservation(jane, now + timedelta(days=3), fixed_id="REV-JANE-001")
        li_printer = LineItem(printer_a, 1, now - timedelta(hours=2), now + timedelta(days=3))
        li_tool    = LineItem(tool_set_a, 1, now - timedelta(hours=2), now + timedelta(days=3))
        rsv_jane.add_line_item(li_printer)
        rsv_jane.add_line_item(li_tool)
        jane.add_reservation(rsv_jane)

        # Jira ยืม Laser Cutter (overdue)
        rsv_jira = Reservation(jira, now - timedelta(days=1), fixed_id="REV-JIRA-001")
        li_laser = LineItem(laser_cutter_a, 1, now - timedelta(days=3), now - timedelta(days=1))
        rsv_jira.add_line_item(li_laser)
        jira.add_reservation(rsv_jira)

        # Jane ยืมหลายชิ้น overdue 2 วัน (สำหรับ test คืนหลายอัน + จ่ายหลาย invoice)
        rsv_jane_overdue = Reservation(jane, now - timedelta(days=2), fixed_id="REV-JANE-OVD")
        li_printer_ovd = LineItem(printer_a, 1, now - timedelta(days=5), now - timedelta(days=2))
        li_tool_ovd    = LineItem(tool_set_a, 1, now - timedelta(days=5), now - timedelta(days=2))
        rsv_jane_overdue.add_line_item(li_printer_ovd)
        rsv_jane_overdue.add_line_item(li_tool_ovd)
        jane.add_reservation(rsv_jane_overdue)

        # Jira ยืม Laser Cutter อีกชุด overdue 3 วัน
        rsv_jira2 = Reservation(jira, now - timedelta(days=3), fixed_id="REV-JIRA-002")
        li_laser2 = LineItem(laser_cutter_a, 1, now - timedelta(days=6), now - timedelta(days=3))
        rsv_jira2.add_line_item(li_laser2)
        jira.add_reservation(rsv_jira2)

        print(f"\n📋 Seed Reservations (ID คงที่):")
        print(f"  Jane  (USE-001)  REV-JANE-001  | items: 3DP-001, TOOL-001  (due +3d, ไม่มี fine)")
        print(f"  Jane  (USE-001)  REV-JANE-OVD  | items: 3DP-001, TOOL-001  (overdue 2d → fine 400 THB)")
        print(f"  Jira  (USE-002)  REV-JIRA-001  | items: LSC-001             (overdue 1d → fine 100 THB)")
        print(f"  Jira  (USE-002)  REV-JIRA-002  | items: LSC-001             (overdue 3d → fine 300 THB)")
        # ──────────────────────────────────────────────────────────────

        print("-"*10, "✅ Init Success ", sep=" ", end="-"*10)
        print("\n")

        return maker
    except Exception as e:
        print("-"*10, "❌ Init Failed ", sep=" ", end="-"*10)
        print(f"\n - {e}")