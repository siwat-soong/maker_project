from fastapi import FastAPI
import uvicorn
from typing import Optional
from controller import system_init
from datetime import datetime

app = FastAPI()
sys = system_init()

@app.get("/")
def root():
    return {
        "status": "OK"
    }

@app.get("/event/info")
def show_event_info(event_id: str):
    try:
        event = sys.search_event_from_id(event_id)
        if not event: raise Exception("ไม่พบกิจกรรมนี้")
        return event.detail()
    except Exception as e: return { "ERROR": str(e) }

@app.get("/event/attender")
def show_event_attender(ins_id: str, event_id: str):
    try:
        ins = sys.search_instructor_from_id(ins_id)
        if not ins: raise Exception("ไม่พบวิทยากรท่านนี้")
        event = sys.search_event_from_id(event_id)
        if not event: raise Exception("ไม่พบกิจกรรมนี้")
        if event.get_ins != ins: raise Exception("คุณไม่ได้เป็นวิทยากรของกิจกรรมนี้")
        return [x.detail() for x in event.get_attendants]
    except Exception as e: return { "ERROR": str(e) }

@app.get("/event/all")
def show_all_event():
    try:
        return { "EVENTS": [x.detail() for x in sys.get_events]}
    except Exception as e: return { "ERROR": str(e) }

@app.get("/event/available")
def show_available_event():
    try:
        from _enum import EventStatus
        return { "EVENTS": [x.detail() for x in sys.get_events if x.get_status == EventStatus.SCHEDULED or x.get_status == EventStatus.OPEN]}
    except Exception as e: return { "ERROR": str(e) }

@app.get("/resource/info")
def show_resource_info(res_id):
    try:
        res = sys.search_space_from_id(res_id)
        if not res: res = sys.search_equipment_from_id(res_id)
        if not res: res = sys.search_material_from_id(res_id)
        if not res: raise Exception("ไม่พบทรัพยากรที่คุณต้องการ")
        return res.detail()
    except Exception as e: return { "ERROR": str(e) }

@app.get("/resource/all")
def show_all_resource():
    try:
        res = []
        res.append({ "SPACE": [x.detail() for x in sys.get_spaces]})
        res.append({ "EQUIPMENT": [x.detail() for x in sys.get_equipments]})
        res.append({ "MATERIAL": [x.detail() for x in sys.get_materials]})
        return res
    except Exception as e: return { "ERROR": str(e) }

@app.get("/resource/available")
def show_available_resource(start_time: str, end_time: str):
    try:
        start_time = datetime.strptime(start_time, "%d-%m-%Y %H:%M")
        end_time = datetime.strptime(end_time, "%d-%m-%Y %H:%M")
        if start_time > end_time: raise Exception("เวลาเริ่มต้นหลังเวลาสิ้นสุด")
        if start_time < datetime.now(): raise Exception("ข้อมูลในอดีต")
        if start_time == end_time: raise Exception("เวลาเริ่มต้นและสิ้นสุดเป็นแวลาเดียวกัน")

        from _enum import ResourceStatus
        res = []
        res.append({ "SPACE": [x.detail() for x in sys.get_spaces if x.check_available(start_time, end_time)]})
        res.append({ "EQUIPMENT": [x.detail() for x in sys.get_equipments if x.check_available(start_time, end_time)]})
        res.append({ "MATERIAL": [x.detail() for x in sys.get_materials if x.check_available(start_time, end_time)]})
        return res
    except Exception as e: return { "ERROR": str(e) }

@app.get("/instructor/all")
def show_all_instructor():
    try:
        return [x.detail() for x in sys.get_instructors]
    except Exception as e: return { "ERROR": str(e) }

@app.get("/instructor/available")
def show_available_instructor(start_time: str, end_time: str):
    try:
        start_time = datetime.strptime(start_time, "%d-%m-%Y %H:%M")
        end_time = datetime.strptime(end_time, "%d-%m-%Y %H:%M")
        if start_time > end_time: raise Exception("เวลาเริ่มต้นหลังเวลาสิ้นสุด")
        if start_time < datetime.now(): raise Exception("ข้อมูลในอดีต")
        if start_time == end_time: raise Exception("เวลาเริ่มต้นและสิ้นสุดเป็นแวลาเดียวกัน")
        from _transaction import TimeRange
        time = TimeRange(start_time, end_time)
        return [x.detail() for x in sys.get_instructors if not x.check_schedule(time)]
    except Exception as e: return { "ERROR": str(e) }

@app.get("/user/info")
def show_user_info(uid: str):
    try:
        user = sys.search_user_from_id(uid)
        if not user: sys.search_admin_from_id(uid)
        if not user: raise Exception("ไม่พบ user id นี้")
        return user.detail()
    except Exception as e: return { "ERROR": str(e) }

@app.get("/user/expired_date")
def show_user_expired_date(uid: str):
    try:
        user = sys.search_user_from_id(uid)
        if not user: raise Exception("ไม่พบ user id นี้")
        return { "EXP": user.get_exp }
    except Exception as e: return { "ERROR": str(e) }

@app.get("/user/max_reserve_days")
def show_user_max_rsv(uid: str):
    try:
        user = sys.search_user_from_id(uid)
        if not user: raise Exception("ไม่พบ user id นี้")
        return { "MAX": str(user.get_max_rsv) + " วัน" }
    except Exception as e: return { "ERROR": str(e) }

@app.get("/user/blacklist")
def show_user_blacklist(uid: str):
    try:
        user = sys.search_user_from_id(uid)
        if not user: raise Exception("ไม่พบ user id นี้")
        return { "BLACKLIST": user.is_blacklist }
    except Exception as e: return { "ERROR": str(e) }

@app.get("/user/invoice")
def show_user_invoice(uid: str):
    try:
        user = sys.search_user_from_id(uid)
        if not user: raise Exception("ไม่พบ user id นี้")
        return { "INVOICE": user.get_invoice.detail() if hasattr(user.get_invoice, "detail") else "ไม่มีใบแจ้งหนี้"}
    except Exception as e: return { "ERROR": str(e) }

@app.get("/user/notification")
def show_user_notification(uid: str):
    try:
        user = sys.search_user_from_id(uid)
        if not user: raise Exception("ไม่พบ user id นี้")
        return { "NOTIFICATIONS": [x.detail() for x in user.get_notification]}
    except Exception as e: return { "ERROR": str(e) }

@app.get("/user/receipt")
def show_user_receipt(uid: str):
    try:
        user = sys.search_user_from_id(uid)
        if not user: raise Exception("ไม่พบ user id นี้")
        return { "RECEIPTS": [x.detail() for x in user.get_receipt]}
    except Exception as e: return { "ERROR": str(e) }

@app.get("/user/cart")
def show_user_cart(uid: str):
    try:
        user = sys.search_user_from_id(uid)
        if not user: raise Exception("ไม่พบ user id นี้")
        return { "CARTS": [x.detail() for x in user.get_cart]}
    except Exception as e: return { "ERROR": str(e) }

@app.get("/user/reservation")
def show_user_reservation(uid: str):
    try:
        user = sys.search_user_from_id(uid)
        if not user: raise Exception("ไม่พบ user id นี้")
        return { "RESERVATIONS": [x.detail() for x in user.get_reservation]}
    except Exception as e: return { "ERROR": str(e) }

@app.post("/user/register")
def register(uid: str, name: str, tel: str):
    try:
        user = sys.search_user_from_id(uid)
        if user: raise Exception("คุณได้ลงทะเบียนแล้ว")
        from _user import User
        sys.add_user(User(uid, name, tel))
        return { "STATUS": "SUCCESS" }
    except Exception as e: return { "ERROR": str(e) }

@app.post("/user/subscribe")
def subscribe(uid: str):
    try:
        user = sys.search_user_from_id(uid)
        if not user: raise Exception("ไม่พบ user id นี้")
        if user.get_invoice: raise Exception("มียอดค้างชำระ กรุณาชำระก่อนทำรายการ")
        if user.is_blacklist: raise Exception("คุณติด blacklist ไม่สามารถดำเนินการได้")

        user.subscribe()
        from _enum import InvoiceType
        user.create_invoice(InvoiceType.SUBSCRIBE, "Subscription", 100)

        return { "STATUS": "SUCCESS" }
    except Exception as e: return { "ERROR": str(e) }

@app.post("/user/add_to_cart")
def add_to_cart(
    uid: str,
    resource_id: str,
    amount: float = 1,
    start_time: Optional[str] = None,
    end_time: Optional[str] = None,
    event: Optional[bool] = False
    ):
    try:
        from _enum import ReserveType
        user = user = sys.search_user_from_id(uid)
        if not user: raise Exception("ไม่พบ user id นี้")

        if start_time is not None and end_time is not None:
            start_time = datetime.strptime(start_time, "%d-%m-%Y %H:%M")
            end_time = datetime.strptime(end_time, "%d-%m-%Y %H:%M")
            if start_time > end_time: raise Exception("เวลาเริ่มต้นหลังเวลาสิ้นสุด")
            if start_time < datetime.now(): raise Exception("คุณจองทรัพยากรในอดีต")
            if start_time == end_time: raise Exception("คุณไม่สามารถจองเวลาเริ่มต้นและสิ้นสุดเป็นแวลาเดียวกันได้")

            if not event:
                diff = start_time - datetime.now()
                if diff.total_seconds() / 86400 > user.get_max_rsv: raise Exception("คุณจองเกินกว่าสิทธิเวลาจองล่วงหน้าสูงสุด")

        if not event:
            if user.get_invoice: raise Exception("มียอดค้างชำระ กรุณาชำระก่อนทำรายการ")
            if user.is_blacklist: raise Exception("คุณติด blacklist ไม่สามารถดำเนินการได้")

        if amount < 0: raise Exception("จำนวนมีค่าน้อยกว่า 0")

        res = sys.search_space_from_id(resource_id)
        if not res: res = sys.search_equipment_from_id(resource_id)
        if not res: res = sys.search_material_from_id(resource_id)
        if not res: raise Exception("ไม่พบทรัพยากรที่คุณต้องการ")

        if res.get_rsv_type == ReserveType.RESERVE and (not start_time or not end_time): raise Exception("จำเป็นต้องระบุเวลาจอง")
        if hasattr(res, "free_condition") and not res.free_condition: raise Exception("ไม่สามารถเพิ่มทรัพยากรที่จำกัดพื้นที่ในตะกร้าได้")
        if not res.validate(user, amount, start_time, end_time): raise Exception("ไม่สามารถเพิ่มทรัพยากรในตะกร้าได้")

        user.add_to_cart(res, amount, start_time, end_time)

        return { "STATUS": "SUCCESS" }

    except Exception as e: return { "ERROR": str(e) }

@app.post("/user/remove_from_cart")
def remove_from_cart(uid: str, resource_id: str, start_time: Optional[str] = None):
    try:
        if start_time: start_time = datetime.strptime(start_time, "%d-%m-%Y %H:%M")

        user = sys.search_user_from_id(uid)
        if not user: raise Exception("ไม่พบ user id นี้")

        res = sys.search_space_from_id(resource_id)
        if not res: res = sys.search_equipment_from_id(resource_id)
        if not res: res = sys.search_material_from_id(resource_id)
        if not res: raise Exception("ไม่พบทรัพยากรที่คุณต้องการ")

        user.remove_from_cart(res, start_time)

        return { "STATUS": "SUCCESS" }

    except Exception as e: return { "ERROR": str(e) }

@app.post("/user/reserve")
def reserve(uid: str):
    try:
        user = sys.search_user_from_id(uid)
        if not user: raise Exception("ไม่พบ user id นี้")
        if user.get_invoice: raise Exception("มียอดค้างชำระ กรุณาชำระก่อนทำรายการ")
        if user.is_blacklist: raise Exception("คุณติด blacklist ไม่สามารถดำเนินการได้")

        from _enum import ReserveType, ReservedStatus
        reserved = []
        for cart in user.get_cart:
            if cart.get_resource.get_rsv_type == ReserveType.RESERVE and cart.get_status == ReservedStatus.IN_CART:
                res = cart.get_resource
                if not res.validate(user, cart.get_amount, cart.get_time.get_start_time, cart.get_time.get_end_time): raise Exception(f"ทรัพยากร {res.get_id} ไม่พร้อมให้ทำการจองแล้ว")
                cart.reserve()
                reserved.append(cart)

        if not reserved: raise Exception("ไม่มีทรัพยากรที่จองได้ในตะกร้า")

        rsv = user.create_reservation(reserved)
        user.clear_cart(reserved)

        user.notify("RESERVE", f"You reserved resources {rsv.get_id}! Please check in on time. Search Reservation for more information")

        return { "STATUS": "SUCCESS" }

    except Exception as e: return { "ERROR": str(e) }

@app.post("/user/cancel_reserve")
def cancel_reserve(uid: str, rsv_id: str, res_id: Optional[str] = None, start_time: Optional[str] = None):
    try:
        if start_time: start_time = datetime.strptime(start_time, "%d-%m-%Y %H:%M")

        user = sys.search_user_from_id(uid)
        if not user: raise Exception("ไม่พบ user id นี้")
        if user.get_invoice: raise Exception("มียอดค้างชำระ กรุณาชำระก่อนทำรายการ")
        if user.is_blacklist: raise Exception("คุณติด blacklist ไม่สามารถดำเนินการได้")

        rsv = user.search_reservation_by_id(rsv_id)
        if not rsv: raise Exception("ไม่พบใบจองนี้")

        res = sys.search_space_from_id(res_id)
        if not res: res = sys.search_equipment_from_id(res_id)
        if not res: res = sys.search_material_from_id(res_id)

        item_to_cancel = rsv.cancel(res, start_time)
        if not item_to_cancel: raise Exception("ไม่พบทรัพยากรที่ต้องการยกเลิก")
        total_fine = 0
        for item in item_to_cancel: total_fine += item.cancel()

        user.notify("CANCEL", f"You cancelled {rsv_id}!")

        if total_fine > 0:
            from _enum import InvoiceType
            user.create_invoice(InvoiceType.FINE, [str(i.get_resource.get_id) for i in item_to_cancel], total_fine)
            return { "STATUS": "SUCCESS", "FINE": "$" + str(total_fine)}

        return { "STATUS": "SUCCESS"}

    except Exception as e: return { "ERROR": str(e) }

@app.post("/user/buy")
def buy(uid: str):
    try:
        user = sys.search_user_from_id(uid)
        if not user: raise Exception("ไม่พบ user id นี้")
        if user.get_invoice: raise Exception("มียอดค้างชำระ กรุณาชำระก่อนทำรายการ")
        if user.is_blacklist: raise Exception("คุณติด blacklist ไม่สามารถดำเนินการได้")

        from _enum import ReserveType, ReservedStatus
        items = []
        total = 0
        for cart in user.get_cart:
            if cart.get_resource.get_rsv_type == ReserveType.INSTANT_PAY and cart.get_status == ReservedStatus.IN_CART:
                res = cart.get_resource
                total += res.calculate_fee(user, cart.get_amount)
                res.deduct(cart.get_amount)

                items.append(cart)
        
        if not items: raise Exception("ไม่มีทรัพยากรที่ซื้อได้ในตะกร้า")

        from _enum import InvoiceType
        user.create_invoice(InvoiceType.RESOURCE, [str(i.get_resource.get_id) for i in items], total)

        user.clear_cart(items)

        return { "STATUS": "SUCCESS", "TOTAL": total }

    except Exception as e: return { "ERROR": str(e) }

@app.post("/user/check_in")
def check_in(uid: str, rsv_id: str, res_id: str, start_time: str, check_in_time: Optional[str] = None):
    try:
        start_time = datetime.strptime(start_time, "%d-%m-%Y %H:%M")
        if check_in_time: check_in_time = datetime.strptime(check_in_time, "%d-%m-%Y %H:%M")
        else: check_in_time = datetime.now()

        user = sys.search_user_from_id(uid)
        if not user: raise Exception("ไม่พบ user id นี้")
        if user.get_invoice: raise Exception("มียอดค้างชำระ กรุณาชำระก่อนทำรายการ")
        if user.is_blacklist: raise Exception("คุณติด blacklist ไม่สามารถดำเนินการได้")

        fine = 0
        diff = check_in_time - start_time
        diff_in_min = diff.total_seconds() / 60
        if diff_in_min < -15: raise Exception("ไม่สามารถเช็คอินก่อนเวลาเกิน 15 นาที")
        elif diff_in_min > 15: fine = int(diff_in_min - 15) * 10

        rsv = user.search_reservation_by_id(rsv_id)
        if not rsv: raise Exception("ไม่พบใบจองนี้")

        res = sys.search_space_from_id(res_id)
        if not res: res = sys.search_equipment_from_id(res_id)
        if not res: res = sys.search_material_from_id(res_id)
        if not res: raise Exception("ไม่พบทรัพยากรที่คุณต้องการ")
        
        if fine > 0:
            item_to_cancel = rsv.cancel(res, start_time)
            for item in item_to_cancel: item.cancel()
            from _enum import InvoiceType
            user.create_invoice(InvoiceType.FINE, "CHECK IN LATE", fine)
            raise Exception(f"ระบบยกเลิกการเช็คอิน เสียค่าปรับ ${fine}")
        else:
            items = rsv.check_in(res, start_time)
            if not items: raise Exception("ทรัพยากรถูกเช็คอินครบแล้ว")
            for item in items: item.check_in()
        
        user.notify("CHECK IN", f"You checked in {res_id} from {rsv_id}!")
        
        return { "STATUS": "SUCCESS" }

    except Exception as e: return { "ERROR": str(e) }

@app.post("/user/check_out")
def check_out(uid: str, rsv_id: str, res_id: str, check_out_time: Optional[str] = None):
    try:
        if check_out_time: check_out_time = datetime.strptime(check_out_time, "%d-%m-%Y %H:%M")
        else: check_out_time = datetime.now()

        user = sys.search_user_from_id(uid)
        if not user: raise Exception("ไม่พบ user id นี้")
        if user.get_invoice: raise Exception("มียอดค้างชำระ กรุณาชำระก่อนทำรายการ")
        if user.is_blacklist: raise Exception("คุณติด blacklist ไม่สามารถดำเนินการได้")

        rsv = user.search_reservation_by_id(rsv_id)
        if not rsv: raise Exception("ไม่พบใบจองนี้")

        res = sys.search_space_from_id(res_id)
        if not res: res = sys.search_equipment_from_id(res_id)
        if not res: res = sys.search_material_from_id(res_id)
        if not res: raise Exception("ไม่พบทรัพยากรที่คุณต้องการ")

        total = 0
        items = rsv.check_out(res)
        for item in items: total += item.check_out(user, check_out_time)

        if total > 0:
            from _enum import InvoiceType
            user.create_invoice(InvoiceType.RESOURCE, "CHECK OUT", total)
        
        user.notify("CHECK OUT", f"You checked out {res_id} from {rsv_id} with total {total}! Please purchased.")
        
        return { "STATUS": "SUCCESS", "TOTAL_FEE": "$" + str(total)}

    except Exception as e: return { "ERROR": str(e) }

@app.post("/user/join")
def join(uid: str, event_id: str):
    try:
        user = sys.search_user_from_id(uid)
        if not user: raise Exception("ไม่พบ user id นี้")
        if user.get_invoice: raise Exception("มียอดค้างชำระ กรุณาชำระก่อนทำรายการ")
        if user.is_blacklist: raise Exception("คุณติด blacklist ไม่สามารถดำเนินการได้")

        event = sys.search_event_from_id(event_id)
        if not event: raise Exception("ไม่พบกิจกรรมนี้")

        total = event.join(user) * (1 - user.get_discount)

        if total > 0:
            from _enum import InvoiceType
            user.create_invoice(InvoiceType.EVENT, f"JOIN {event_id}", total)
        
        return { "STATUS": "SUCCESS", "TOTAL_FEE": "$" + str(total)}

    except Exception as e: return { "ERROR": str(e) }

@app.post("/user/unjoin")
def unjoin(uid: str, event_id: str, time: str):
    try:
        time = datetime.strptime(time, "%d-%m-%Y %H:%M")

        user = sys.search_user_from_id(uid)
        if not user: raise Exception("ไม่พบ user id นี้")
        if user.get_invoice: raise Exception("มียอดค้างชำระ กรุณาชำระก่อนทำรายการ")
        if user.is_blacklist: raise Exception("คุณติด blacklist ไม่สามารถดำเนินการได้")

        event = sys.search_event_from_id(event_id)
        if not event: raise Exception("ไม่พบกิจกรรมนี้")

        total_refund = event.unjoin(user, time)
        
        return { "STATUS": "SUCCESS" , "REFUND": "$" + str(total_refund)}

    except Exception as e: return { "ERROR": str(e) }

@app.post("/user/use")
def use(eq_id: str, amount: Optional[float] = None):
    try:
        eq = sys.search_equipment_from_id(eq_id)
        if not eq: raise Exception("ไม่พบอุปกรณ์นี้")

        eq.use(amount)

    except Exception as e: return { "ERROR": str(e) }

@app.post("/user/add_own")
def add_own(eq_id: str):
    try:
        eq = sys.search_equipment_from_id(eq_id)
        if not eq: raise Exception("ไม่พบอุปกรณ์นี้")

        if hasattr(eq, "set_own"): eq.add_own()
        else: raise Exception("ไม่สามารถเพิ่มวัสดุใด ๆ ในอุปกรณ์นี้ได้") 

    except Exception as e: return { "ERROR": str(e) }

@app.post("/user/breakdown")
def breakdown(eq_id: str):
    try:
        eq = sys.search_equipment_from_id(eq_id)
        if not eq: raise Exception("ไม่พบอุปกรณ์นี้")

        from _enum import ResourceStatus
        eq.update_status(ResourceStatus.MAINTENANCE)

        return { "STATUS": "SUCCESS" }

    except Exception as e: return { "ERROR": str(e) }

@app.post("/admin/repair")
def repair(admin_id: str, eq_id: str):
    try:
        admin = sys.search_admin_from_id(admin_id)
        if not admin: raise Exception("ไม่พบ admin ท่านนี้")

        eq = sys.search_equipment_from_id(eq_id)
        if not eq: raise Exception("ไม่พบอุปกรณ์นี้")

        from _enum import ResourceStatus
        if eq.get_status != ResourceStatus.MAINTENANCE: raise Exception("อุปกรณ์ไม่จำเป็นต้องซ่อม")
        
        eq.update_status(ResourceStatus.AVAILABLE)

        return { "STATUS": "SUCCESS" }

    except Exception as e: return { "ERROR": str(e) }

@app.post("/admin/restock")
def restock(uid: str, mat_id: str, amount: float):
    try:
        admin = sys.search_admin_from_id(uid)
        if not admin: raise Exception("ไม่พบ admin ท่านนี้")

        mat = sys.search_material_from_id(mat_id)
        if not mat: raise Exception("ไม่พบวัสดุนี้")

        mat.restock(float)
        
        return { "STATUS": "SUCCESS" }

    except Exception as e: return { "ERROR": str(e) }

@app.post("/admin/blacklist")
def blacklist(admin_id: str, uid: str):
    try:
        admin = sys.search_admin_from_id(admin_id)
        if not admin: raise Exception("ไม่พบ admin ท่านนี้")

        user = sys.search_user_from_id(uid)
        if not user: raise Exception("ไม่พบ user ท่านนี้")

        user.blacklist()
        
        return { "STATUS": "SUCCESS" }

    except Exception as e: return { "ERROR": str(e) }

@app.post("/admin/unblacklist")
def unblacklist(admin_id: str, uid: str):
    try:
        admin = sys.search_admin_from_id(admin_id)
        if not admin: raise Exception("ไม่พบ admin ท่านนี้")

        user = sys.search_user_from_id(uid)
        if not user: raise Exception("ไม่พบ user ท่านนี้")

        user.unblacklist()
        
        return { "STATUS": "SUCCESS" }

    except Exception as e: return { "ERROR": str(e) }

@app.post("/event/create")
def create_event(uid: str, topic: str, detail: str, start_time: str, end_time: str, ins_id: str, space_id: str, max_attender: float, join_fee: float):
    try:
        admin = sys.search_admin_from_id(uid)
        if not admin: raise Exception("ไม่พบ admin ท่านนี้")

        if join_fee < 0: raise Exception("ค่าเงินติดลบ")

        start_time = datetime.strptime(start_time, "%d-%m-%Y %H:%M")
        end_time = datetime.strptime(end_time, "%d-%m-%Y %H:%M")
        if start_time > end_time: raise Exception("เวลาเริ่มต้นหลังเวลาสิ้นสุด")
        if start_time < datetime.now(): raise Exception("คุณจองทรัพยากรในอดีต")
        if start_time == end_time: raise Exception("คุณไม่สามารถจองเวลาเริ่มต้นและสิ้นสุดเป็นแวลาเดียวกันได้")

        ins = sys.search_instructor_from_id(ins_id)
        if not ins: raise Exception("ไม่พบวิทยากรท่านนี้")

        space = sys.search_space_from_id(space_id)
        if not space: raise Exception("ไม่พบพื้นที่จัดกิจกรรม")

        items = [space]
        items.extend([eq for eq in space.get_eq])

        from _transaction import TimeRange, ReserveSlot
        time = TimeRange(start_time, end_time)
        slots = [ReserveSlot(item, 1, time) for item in items]

        if ins.check_schedule(time): raise Exception("วิทยากรไม่พร้อมบรรยายในเวลาดังกล่าว")

        if max_attender > space.get_capacity: raise Exception("พื้นที่ไม่สามารถรองรับคนได้เพียงพอ")
    
        for slot in slots:
            res = slot.get_resource
            if not res.validate(admin, 1, start_time, end_time): raise Exception(f"ทรัพยากร {res.get_id} ไม่พร้อมให้ทำการจองในเวลาดังกล่าว")
            slot.reserve()
        
        ins.add_schedule(time)

        sys.create_event(topic, detail, time, ins, space, slots, max_attender, join_fee)

        return { "STATUS": "SUCCESS"}
    except Exception as e: return { "ERROR": str(e) }

@app.post("/event/open")
def unjoin(uid: str, event_id: str):
    try:
        admin = sys.search_admin_from_id(uid)
        if not admin: raise Exception("ไม่พบ admin ท่านนี้")

        event = sys.search_event_from_id(event_id)
        if not event: raise Exception("ไม่พบกิจกรรมนี้")

        event.open_event()

        sys.broadcast("OPEN EVENT", "Event {event.get_id} was openned! Please join us. Show Event for more details.")
        
        return { "STATUS": "SUCCESS" }

    except Exception as e: return { "ERROR": str(e) }

@app.post("/event/close")
def close_event(uid: str, event_id: str, end_time: str):
    try:
        end_time = datetime.strptime(end_time, "%d-%m-%Y %H:%M")

        admin = sys.search_admin_from_id(uid)
        if not admin: raise Exception("ไม่พบ admin ท่านนี้")

        event = sys.search_event_from_id(event_id)
        if not event: raise Exception("ไม่พบกิจกรรมนี้")

        from _enum import EventStatus
        if event.get_status == EventStatus.CLOSED: raise Exception("กิจกรรมนี้ได้ปิดไปแล้ว")

        ins = event.get_ins
        ins.remove_schedule(event.get_time)

        slots = event.get_items
        for slot in slots:
            from _enum import ReservedStatus
            slot.update_status(ReservedStatus.CANCELLED)
            slot.get_resource.remove_schedule(event.get_time)

        from _enum import EventStatus
        event.update_status(EventStatus.CLOSED)

        refund = False
        if end_time < event.get_time.get_start_time: refund = True

        sys.broadcast("CLOSE EVENT", "Event {event.get_id} closed.")

        return { "STATUS": "SUCCESS", "REFUND": refund}
    except Exception as e: return { "ERROR": str(e) }

@app.post("/event/add")
def add_resource_to_event(uid: str, event_id: str):
    try:
        ins = sys.search_instructor_from_id(uid)
        if not ins: raise Exception("ไม่พบวิทยากรท่านนี้")

        event = sys.search_event_from_id(event_id)
        if not event: raise Exception("ไม่พบกิจกรรมนี้")

        if not ins.get_cart: raise Exception("ไม่มีทรัพยากรในตะกร้า")
        if event.get_ins != ins: raise Exception("คุณไม่ได้เป็นวิทยากรของกิจกรรมนี้")

        reserved = []
        purchased = []
        total = 0
        for slot in ins.get_cart:
            slot.set_time = event.get_time
            res = slot.get_resource
            if res.validate(ins, slot.get_amount, slot.get_time.get_start_time, slot.get_time.get_end_time):
                from _enum import ReserveType
                if res.get_rsv_type == ReserveType.RESERVE:
                    slot.reserve()
                    reserved.append(slot)
                elif res.get_rsv_type == ReserveType.INSTANT_PAY:
                    total += res.calculate_fee(ins, slot.get_amount)
                    res.deduct(slot.get_amount)
                    purchased.append(slot)
        
        if total > 0:
            from _enum import InvoiceType
            event.create_receipt(ins, InvoiceType.RESOURCE, [str(i.get_resource.get_id) for i in purchased], total)

        ins.clear_cart(reserved)
        ins.clear_cart(purchased)

        return { "STATUS": "SUCCESS"}
    except Exception as e: return { "ERROR": str(e) }

@app.post("/event/grade")
def grade_event(ins_id: str, event_id: str, uid: str, score: float):
    try:
        ins = sys.search_instructor_from_id(ins_id)
        if not ins: raise Exception("ไม่พบวิทยากรท่านนี้")

        event = sys.search_event_from_id(event_id)
        if not event: raise Exception("ไม่พบกิจกรรมนี้")

        user = sys.search_user_from_id(uid)
        if not user: raise Exception("ไม่พบ user id นี้")

        if event.get_ins != ins: raise Exception("คุณไม่ได้เป็นวิทยากรของกิจกรรมนี้")
        if not event.check_attendant(user): raise Exception("ผู้ใช้ไม่ได้เข้าร่วมกิจกรรมนี้")

        if score > 75: grade = 'A'
        elif score > 50: grade = 'B'
        elif score > 25: grade = 'C'
        elif score > 0: grade = 'D'

        user.create_certificate(event, grade)

        return { "STATUS": "SUCCESS"}
    except Exception as e: return { "ERROR": str(e) }

@app.post("/pay")
def pay(uid: str, cost: float, method: str):
    try:
        method = method.upper()
        user = sys.search_user_from_id(uid)
        if not user: raise Exception("ไม่พบ user id นี้")
        if cost < 0: raise Exception("เงินมีค่าน้อยกว่า 0")
        pm = sys.search_payment_from_type(method)
        if not pm: raise Exception("ไม่รองรับการชำระประเภทนี้")
        inv = user.get_invoice
        if not inv: raise Exception("ไม่มีใบแจ้งหนี้ที่ต้องชำระ")
        total = inv.get_cost
        if total > cost: raise Exception("ยอดเงินไม่เพียงพอชำระ")

        if not pm.validate(total, cost): raise Exception("ไม่สามารถชำระเงินได้")

        change = pm.process_payment(total, cost)

        user.notify("PAYMENT", f"You purchased for {inv.get_id} totals ${total}. You paid ${cost} and receive ${change} in change by {method}.")
        user.create_receipt(inv.get_id, inv.get_type, inv.get_detail, total, cost, change)

        user.clear_invoice()

        return { 
            "STATUS": "SUCCESS",
            "CHANGE": "$" + str(change)
        }
    except Exception as e: return { "ERROR": str(e) }

def run_api(): uvicorn.run("api:app", host="127.0.0.1", port=8000, reload=True)

if __name__ == "__main__":
    run_api()