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
        self.__notification_list = []

    # Add Methods
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

    def add_notification(self, notification):
        if isinstance(notification, Notification):
            self.__notification_list.append(notification)

    # alias ที่ new_main.py ใช้
    def add_noti(self, notification):
        self.add_notification(notification)

    # Search Methods
    def search_user_by_id(self, user_id):
        for user in self.__user_list:
            if user.get_id == user_id:
                return user
        return None

    def search_payment_method_by_name(self, name: str):
        for pm in self.__payment_method_list:
            if name.lower() in pm.__class__.__name__.lower():
                return pm
        return None

    def search_member_by_id(self, user_id):
        for user in self.__user_list:
            if user.get_role == UserRole.ANNUALMEMBER and user.get_id == user_id:
                return user
        return None

    def search_admin_by_id(self, admin_id):
        for admin in self.__admin_list:
            if admin.get_id == admin_id:
                return admin
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

    def search_event_by_id(self, event_id):
        for event in self.__event_list:
            if event.get_id == event_id:
                return event
        return None

    def search_all_matching_item(self, resource_id):
        all_match_item = []
        for user in self.__user_list:
            for rsv in user.get_user_reservation:
                all_match_item.extend(rsv.list_all_match_line_item(resource_id))
        return all_match_item

    def get_user_list(self):
        return self.__user_list

    def get_all_users(self):
        return self.__user_list

    def get_resource_list(self):
        return self.__space_list + self.__equipment_list + self.__material_list

    # Event Methods
    def show_event_attenders(self, event_id):
        event = self.search_event_by_id(event_id)
        if not event:
            return {"error": "Event not found"}
        return {
            "event_id": event_id,
            "status": event._Event__status.value,
            "attenders": event.get_attenders() or [],
            "count": len(event._Event__attenders)
        }

    def close_event(self, instructor_id: str, event_id: str, expired_days: int = None):
        instructor = next((i for i in self.__instructor_list if i.get_id == instructor_id), None)
        if not instructor:
            return {"error": "Instructor not found"}

        target_event = self.search_event_by_id(event_id)
        if not target_event:
            return {"error": "Event not found"}

        if target_event._Event__status == EventStatus.CLOSED:
            return {"error": "Event is already closed"}

        attenders = target_event._Event__attenders
        if not attenders:
            return {"error": "No attenders in this event"}

        target_event._Event__status = EventStatus.CLOSED
        certified_topic = target_event._Event__certified_topic

        now = datetime.now()
        expired_date = now + timedelta(days=expired_days) if expired_days else None
        issued = []

        for user in attenders:
            try:
                cert = Certificate(user, target_event, certified_topic, now, expired_date)
                user.add_certificate(cert)
                issued.append(user.get_id)
            except Exception as e:
                issued.append(f"{user.get_id} (failed: {e})")

        return {
            "status": "success",
            "event_id": event_id,
            "certified_topic": certified_topic.value,
            "expired_date": expired_date.strftime("%Y-%m-%d") if expired_date else "no expiry",
            "issued_to": issued,
            "message": f"Event closed. {len(issued)} certificate(s) issued"
        }

    # Reserve / Return
    def reserve(self, user_id: str, due_date):
        target_user = self.search_user_by_id(user_id)
        if target_user is None:
            return {"error": "User not found"}

        cart = target_user.line_item_list
        if not cart:
            return {"error": "Cart is empty"}

        booking_list = []
        purchase_list = []

        for line_item in cart:
            item = line_item.get_resource
            item.update_status(ResourceStatus.RESERVED)
            if isinstance(item, Material):
                purchase_list.append(line_item)
            else:
                booking_list.append(line_item)

        if purchase_list:
            invoice = Invoice(target_user, purchase_list)
            target_user.add_invoice(invoice)

        reservation = None
        if booking_list:
            reservation = Reservation(target_user, due_date)
            for li in booking_list:
                reservation.add_line_item(li)
            target_user.add_reservation(reservation)

        target_user.clear_cart()

        reserved_ids = [li.get_resource.get_id for li in booking_list + purchase_list]
        return {
            "reservation_id": reservation.get_reservation_id if reservation else None,
            "user_id": user_id,
            "resources": reserved_ids,
            "due_date": due_date.strftime("%Y-%m-%d %H:%M"),
            "status": "CONFIRMED",
            "message": f"Reserved {len(reserved_ids)} item(s) successfully"
        }

    def process_return(self, user_id: str, reservation_id: str, item_ids: list):
        target_user = self.search_user_by_id(user_id)
        if not target_user:
            return {"error": "User not found"}

        target_reservation = target_user.search_reservation_by_id(reservation_id)
        if not target_reservation:
            return {"error": "Reservation not found"}

        target_items = []
        for item_id in item_ids:
            item = target_reservation.check_item(item_id)
            if not item:
                return {"error": f"Item not found: {item_id}"}
            target_items.append((item_id, item))

        total_cost = 0.0
        for item_id, _ in target_items:
            total_cost += target_reservation.return_items(item_id)

        invoice = Invoice(target_user, reservation=target_reservation, cost=total_cost)

        for _, item in target_items:
            target_reservation.pop_item(item)

        if total_cost == 0:
            from payment_class import Cash
            invoice.mark_as_paid()
            receipt = Receipt(target_user, Cash(), invoice)
            target_user._User__receipt_list.append(receipt)
            target_user.add_invoice(invoice)
            return {
                "receipt_id": receipt.receipt_id,
                "cost": 0.0,
                "payment_status": "PAID",
                "message": f"Auto-paid (no charge) — {len(target_items)} item(s) returned"
            }

        target_user.add_invoice(invoice)
        return {
            "invoice_id": invoice.get_id,
            "cost": invoice.get_cost(),
            "payment_status": "UNPAID",
            "returned_items": [i for i, _ in target_items],
            "message": "Invoice added"
        }


# Init Function
def system_init():
    try:
        maker = Club("maker")
        jane = User("USE-001", "Jane", "0123456789")
        jira = User("USE-002", "Jira", "0123456789")
        thana = Instructor("INS-001", "Thana", "0123456789", Expertise.ADVANCE, 500)
        amnach = Instructor("INS-002", "Amnach", "0123456789", Expertise.ADVANCE, 800)
        tom = Admin("ADM-001", "Tom", "reception")
        jerry = Admin("ADM002", "Jerry", "reception")
        lab_a = Space("LAB-001", SpaceType.LABORATORY, 10, time(10, 0), time(22, 0))
        desk_a = Space("DESK-001", SpaceType.HOT_DESK, 8, time(10, 0), time(22, 0))
        room_a = Space("ROOM-001", SpaceType.MEETING_ROOM, 6, time(10, 0), time(22, 0))
        red_filament = Filament("MAT-001", 2000, "grams", 0, EquipmentType.THREE_D_PRINTER, "PLA", 0.2, "RED")
        printer_a = ThreeDPrinter("3DP-001", Expertise.THREE_D_PRINTER, EquipmentType.THREE_D_PRINTER, "20x20", red_filament)
        wooden_plank = Plank("WDP-001", 10, "plate", 0, EquipmentType.LASER_CUTTER, 5, "SOFT")
        acrylic_a = Acrylic("ACL-001", 20, "plate", 0, EquipmentType.LASER_CUTTER, 2, "CLEAR", "20x20")
        laser_cutter_a = LaserCutter("LSC-001", Expertise.LASER_CUTTER, EquipmentType.LASER_CUTTER, "120x120", None)
        tool_set_a = ToolSet("TOOL-001", None, EquipmentType.TOOL_SET, 5)
        cash_machine = Cash()
        qr_machine = QRCode()

        event1 = Event("EV-001", "Ossiliscope", "Introduction",
                       datetime(2026, 3, 10, 10, 0), datetime(2026, 3, 10, 13, 0),
                       amnach, lab_a, 10, 100, Expertise.ADVANCE)

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

        # ── Seed Reservations ──────────────────────────────────────────
        now = datetime.now()

        rsv_jane = Reservation(jane, now + timedelta(days=3), fixed_id="REV-JANE-001")
        rsv_jane.add_line_item(LineItem(printer_a, 1, now - timedelta(hours=2), now + timedelta(days=3)))
        rsv_jane.add_line_item(LineItem(tool_set_a, 1, now - timedelta(hours=2), now + timedelta(days=3)))
        jane.add_reservation(rsv_jane)

        rsv_jira = Reservation(jira, now - timedelta(days=1), fixed_id="REV-JIRA-001")
        rsv_jira.add_line_item(LineItem(laser_cutter_a, 1, now - timedelta(days=3), now - timedelta(days=1)))
        jira.add_reservation(rsv_jira)

        rsv_jane_overdue = Reservation(jane, now - timedelta(days=2), fixed_id="REV-JANE-OVD")
        rsv_jane_overdue.add_line_item(LineItem(printer_a, 1, now - timedelta(days=5), now - timedelta(days=2)))
        rsv_jane_overdue.add_line_item(LineItem(tool_set_a, 1, now - timedelta(days=5), now - timedelta(days=2)))
        jane.add_reservation(rsv_jane_overdue)

        rsv_jira2 = Reservation(jira, now - timedelta(days=3), fixed_id="REV-JIRA-002")
        rsv_jira2.add_line_item(LineItem(laser_cutter_a, 1, now - timedelta(days=6), now - timedelta(days=3)))
        jira.add_reservation(rsv_jira2)

        print(f"\n📋 Seed Reservations:")
        print(f"  Jane  (USE-001)  REV-JANE-001  | 3DP-001, TOOL-001  (due +3d)")
        print(f"  Jane  (USE-001)  REV-JANE-OVD  | 3DP-001, TOOL-001  (overdue 2d → 400฿)")
        print(f"  Jira  (USE-002)  REV-JIRA-001  | LSC-001             (overdue 1d → 100฿)")
        print(f"  Jira  (USE-002)  REV-JIRA-002  | LSC-001             (overdue 3d → 300฿)")
        print("-" * 10, "✅ Init Success", "-" * 10)

        return maker

    except Exception as e:
        print("-" * 10, "❌ Init Failed", "-" * 10)
        print(f"\n - {e}")
        raise