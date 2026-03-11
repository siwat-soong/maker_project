from fastapi import FastAPI
import uvicorn
from controller import system_init
from enum_class import InvoiceType
from datetime import datetime, timedelta

sys = system_init()

app = FastAPI()

@app.get("/")
def ping():
    return {
        "status": "ok",
        "message": "pong"
    }

@app.get("/notifications")
def show_notifications(user_id):
    try:
        user = sys.search_user_by_id(user_id)
        if not user: user = sys.search_instructor_by_id(user_id)
        if not user: raise Exception
        return user.show_notification()
    except:
        return "⛔ Get Notifications Failed"

@app.get("/user_info")
def show_user_info(user_id):
    user = sys.search_user_by_id(user_id)
    
    if not user: user = sys.search_instructor_by_id(user_id)
    if not user: return "⛔ User Not Found"
    return user.show_info()

@app.post("/subscribe")
def subscribe(user_id):
    try:
        user = sys.search_user_by_id(user_id)
        if user is None: raise Exception
        elif user.check_blacklist(): raise Exception
        elif user.check_invoice(): raise Exception
        elif user.get_expired_date > datetime.now(): raise Exception
        else: 
            user.subscribe()
            inv = user.create_invoice(InvoiceType.SUBSCRIBE, f'{user.get_name} subscribe member from {datetime.now()} for 365 days', 100)
            sys.notify(user, 'Subscribe', f'สมัครสมาชิกสำเร็จ กรุณาชำระค่าสมัคร 100฿ ที่ใบแจ้งหนี้ {inv.get_id}')
            return f'✅ Subscribe Success, Please pay fee 100$ to ID: {inv.get_id}'
    except:
        return f'⛔ Subscribe Failed'

@app.post("/pay")
def pay(user_id, inv_id, cost: float, method_id):
    try:
        user = sys.search_user_by_id(user_id)
        if not user: user = sys.search_instructor_by_id(user_id)
        if not user: raise Exception
        inv = user.search_invoice_by_id(inv_id)
        method = sys.search_method_by_id(method_id)
        if(method.validate(inv.get_cost, cost)): 
            change = method.process_payment()
            user.create_receipt(inv, change, method)
            if inv.get_invoice_type == InvoiceType.SUBSCRIBE:
                user.activate_membership()
            sys.notify(user, 'Payment', f'ชำระเงิน {inv.get_cost}฿ สำเร็จ ทอน {change}฿')
            return f'✅ Pay Success with change {change}'
        else: raise Exception
    except:
        return f'⛔ Pay Failed'

@app.post("/add_to_cart")
def add_to_cart(user_id, item_id, start_time, end_time, amount: float):
    try:
        mode = "INDIVIDUAL"

        start_time = datetime.strptime(start_time, "%d/%m/%Y,%H:%M")
        end_time = datetime.strptime(end_time, "%d/%m/%Y,%H:%M")

        if start_time >= end_time: raise Exception

        target_user = sys.search_user_by_id(user_id)
        if not target_user: 
            ins = sys.search_instructor_by_id(user_id)
            if not ins: raise Exception
            else:
                mode = "COMPANY"
                target_user = ins

        res = sys.search_resource_by_id(item_id)
        if not res: raise Exception

        if mode != "COMPANY":
            if target_user.check_blacklist(): raise Exception
            adv_res_dur = start_time - datetime.now()
            if adv_res_dur.days > target_user.get_max_reserve_days: raise Exception
            if not target_user.check_expertise(res): raise Exception
            
        if target_user.check_duplicate_cart(res, start_time, end_time): raise Exception

        if not res.check_reservable(start_time, end_time, amount): raise Exception

        target_user.add_to_cart(res, amount, start_time, end_time)

        return '✅ Add to Cart Done'

    except:
        return f'⛔ Add to Cart Failed'

@app.post("/reserve")
def reserve(user_id):
    try:
        reserve_list = []
        purchase_list = []

        user = sys.search_user_by_id(user_id)
        if not user: user = sys.search_instructor_by_id(user_id)
        if not user: raise Exception

        if user.check_invoice(): raise Exception
        if user.check_blacklist(): raise Exception

        lit_list = user.get_line_item
        if not lit_list: raise Exception
        
        for lit in lit_list:
            if not lit.get_resource.check_reservable(lit.get_reserved_time.get_start_time, lit.get_reserved_time.get_end_time, lit.get_amount): raise Exception
            low_stock = lit.get_resource.process_reserve(lit.get_amount, lit.get_reserved_time)
            if low_stock:
                sys.broadcast('Low Stock', f'วัสดุ {lit.get_resource.get_id} ใกล้หมดแล้ว')

            from resource_class import Material
            if isinstance(lit.get_resource, Material): purchase_list.append(lit)
            else: reserve_list.append(lit)

        from transaction_class import Reservation
        user.add_reservation(Reservation(user, reserve_list))

        total = 0
        if purchase_list:
            for item in purchase_list:
                total += item.get_resource.calculate_fee(user, item.get_amount, None)
            user.create_invoice(InvoiceType.RESOURCE, "Purchased Material", total)

        user.clear_line_item()

        sys.notify(user, 'Reserve', f'จองสำเร็จ รหัสการจอง {user.get_reservation_list[-1].get_id} ค่าวัสดุ {total}฿')
        return f'✅ Reserve Done, total cost {total}$'

    except:
        return '⛔ Reserve Failed'

@app.post("/event/create")
def create_event(admin_id, topic, detail, start_time, end_time, instructor_id, space_id, max_attender, join_fee: float):
    try:
        adm = sys.search_admin_by_id(admin_id)
        if not adm: raise Exception

        ins = sys.search_instructor_by_id(instructor_id)
        if not ins: raise Exception

        sp = sys.search_space_by_id(space_id)
        if not sp: raise Exception

        start_time = datetime.strptime(start_time, "%d/%m/%Y,%H:%M")
        end_time = datetime.strptime(end_time, "%d/%m/%Y,%H:%M")

        if start_time >= end_time: raise Exception

        if not ins.check_schedule(start_time, end_time): raise Exception
        if not sp.check_schedule(start_time, end_time): raise Exception

        from transaction_class import TimeRange
        from event_class import Event
        t = TimeRange(start_time, end_time)
        sp.process_reserve(1, t)
        ins.add_schedule(t)

        event = Event(topic, detail, t, ins, sp, None, max_attender, float(join_fee), ins.get_expertise)
        sys.add_event(event)
        sys.broadcast('New Event', f'มี event ใหม่ [{event.get_id}] {topic} วันที่ {t.get_start_time.strftime("%d/%m/%Y %H:%M")} - {t.get_end_time.strftime("%H:%M")} โดย {ins.get_name}')
        return f'✅ Create Event Success, Event ID: {event.get_id}'
    except:
        return '⛔ Create Event Failed'
    
@app.post("/event/join")
def join_event(user_id, event_id):
    try:
        user = sys.search_user_by_id(user_id)
        if not user: raise Exception

        event = sys.search_event_by_id(event_id)
        if not event: raise Exception

        if user.check_blacklist(): raise Exception
        if user.check_invoice(): raise Exception
        if not event.check_joinable(user): raise Exception

        fee = event.calculate_fee(user)
        event.join(user)

        user.create_invoice(InvoiceType.EVENT, f'You has joined event {event.get_id}', fee)
        sys.notify(user, 'Join Event', f'เข้าร่วม event {event.get_id} สำเร็จ ค่าเข้าร่วม {fee}฿')
        return f'✅ Join Event Success, fee = {fee}$'

    except:
        return '⛔ Join Event Failed'

@app.post("/event/certificate")
def add_certificate(instructor_id, event_id, user_id, score: float):
    try:
        ins = sys.search_instructor_by_id(instructor_id)
        if not ins: raise Exception
        event = sys.search_event_by_id(event_id)
        if not event: raise Exception
        attendant = sys.search_user_by_id(user_id)
        if not attendant: raise Exception
        if not event.get_instructor.get_id == instructor_id: raise Exception
        if not event.search_attendant_by_id(user_id): raise Exception
        grade = "PASS" if score >= 50 else "FAIL"
        from event_class import Certification
        attendant.add_certificate(Certification(attendant, event, event.get_certified_topic, grade))
        return "✅ Add Certificate Success"
    except:
        return "⛔ Add Certificate Failed"

@app.put("/event/add")
def add_equipment_to_event(user_id, event_id):
    try:
        ins = sys.search_instructor_by_id(user_id)
        if not ins: raise Exception

        event = sys.search_event_by_id(event_id)
        if not event: raise Exception

        if event.get_instructor != ins: raise Exception

        if ins.check_invoice(): raise Exception

        lit_list = ins.get_line_item
        if not lit_list: raise Exception
        
        from resource_class import Material
        total = 0
        for lit in lit_list:
            if not lit.get_resource.check_reservable(lit.get_reserved_time.get_start_time, lit.get_reserved_time.get_end_time, lit.get_amount): raise Exception
            lit.get_resource.process_reserve(lit.get_amount, lit.get_reserved_time)
            if isinstance(lit.get_resource, Material):
                total += lit.get_resource.calculate_fee(ins, lit.get_amount, None)

        event.add_eq(lit_list)
        ins.clear_line_item()

        if total > 0:
            inv = ins.create_invoice(InvoiceType.RESOURCE, f"Material for event {event_id}", total)
            sys.notify(ins, 'Add to Event', f'เพิ่มของเข้า event {event_id} สำเร็จ ค่าวัสดุ {total}฿ ที่ใบแจ้งหนี้ {inv.get_id}')
            return f'✅ Add to Event Success, material cost {total}฿'

        sys.notify(ins, 'Add to Event', f'เพิ่มของเข้า event {event_id} สำเร็จ ไม่มีค่าวัสดุ')
        return '✅ Add to Event Success, no material cost'

    except: return '⛔ Add to Event Failed'

@app.post("/checkin")
def check_in(user_id, rsv_id, space_id, start_time):
    try:
        start_time = datetime.strptime(start_time, "%d/%m/%Y,%H:%M")

        user = sys.search_user_by_id(user_id)
        if not user: user = sys.search_instructor_by_id(user_id)
        if not user: raise Exception

        rsv = user.search_reservation_by_id(rsv_id)
        if not rsv: raise Exception

        space = sys.search_space_by_id(space_id)
        lit = rsv.search_item_list(space, start_time)
        if not lit: raise Exception

        if lit.get_status: raise Exception

        if user.check_blacklist(): raise Exception
        if user.check_invoice(): raise Exception
        if not space.check_available(): raise Exception

        now = datetime.now()
        diff_mins = (start_time - now).total_seconds() / 60
        if diff_mins > 15: raise Exception
        elif diff_mins < -15:
            if (diff_mins * -1) <= 15: return '⚠️ Fine : 0.00$'
    
            base_fine = 50 
            rate_per_half_hour = 20
            extra_periods = ((diff_mins * -1) - 15) / 30
            total_fine = base_fine + (extra_periods * rate_per_half_hour)

            user.create_invoice(InvoiceType.FEE, "Check In Late Fine", total_fine)
            return f'⚠️ Fine : {total_fine:.2f}$'
        else:
            from enum_class import ResourceStatus, LineItemStatus
            space.update_status(ResourceStatus.IN_USE)
            lit.update_status(LineItemStatus.CHECKED_IN)
            lit.set_start_time = now
            sys.notify(user, 'Check In', f'Check in {space_id} เวลา {now.strftime("%d/%m/%Y %H:%M")} สำเร็จ')
        return '✅ Check In Success'
    except: return '⛔ Check In Failed'

@app.post("/checkout")
def check_out(user_id, rsv_id, space_id, start_time):
    from enum_class import LineItemStatus
    try:
        start_time = datetime.strptime(start_time, "%d/%m/%Y,%H:%M")

        user = sys.search_user_by_id(user_id)
        if not user: user = sys.search_instructor_by_id(user_id)
        if not user: raise Exception

        rsv = user.search_reservation_by_id(rsv_id)
        if not rsv: raise Exception

        space = sys.search_space_by_id(space_id)
        lit = rsv.search_item_list(space, start_time)
        if not lit: raise Exception

        if lit.get_status != LineItemStatus.CHECKED_IN: raise Exception

        lit.set_end_time = datetime.now()
        fee = space.calculate_fee(user, lit.get_amount, lit.get_reserved_time.get_duration())
        lit.update_status(LineItemStatus.COMPLETED)
        space.cancel_reserve(lit.get_reserved_time)

        user.create_invoice(InvoiceType.RESOURCE, "Check Out", fee)
        sys.notify(user, 'Check Out', f'Check out {space_id} สำเร็จ ค่าบริการ {fee}฿')
        return f'✅ Check Out Success, cost = {fee}$'
    except: return '⛔ Check Out Failed'

@app.post("/return_eq")
def return_eq(user_id, rsv_id, equipment_id, start_time):
    from enum_class import LineItemStatus
    try:
        start_time = datetime.strptime(start_time, "%d/%m/%Y,%H:%M")

        user = sys.search_user_by_id(user_id)
        if not user: user = sys.search_instructor_by_id(user_id)
        if not user: raise Exception

        rsv = user.search_reservation_by_id(rsv_id)
        if not rsv: raise Exception

        eq = sys.search_equipment_by_id(equipment_id)
        lit = rsv.search_item_list(eq, start_time)
        if not lit: raise Exception

        lit.set_end_time = datetime.now()
        fee = eq.calculate_fee(user, lit.get_amount, lit.get_reserved_time.get_duration())
        lit.update_status(LineItemStatus.COMPLETED)
        eq.cancel_reserve(lit.get_reserved_time)

        user.create_invoice(InvoiceType.RESOURCE, "Return Equipment", fee)
        sys.notify(user, 'Return Equipment', f'คืน {equipment_id} สำเร็จ ค่าบริการ {fee}฿')
        return f'✅ Return Success, cost = {fee}$'
    except: return '⛔ Return Failed'

@app.post("/cancel_reserve")
def cancel_reserve(user_id, rsv_id):
    try:
        user = sys.search_user_by_id(user_id)
        if not user: user = sys.search_instructor_by_id(user_id)
        if not user: raise Exception
        rsv = user.search_reservation_by_id(rsv_id)
        if not rsv: raise Exception
        fee = rsv.cancel()
        if fee is None: raise Exception
        if fee > 0:
            user.create_invoice(InvoiceType.FEE, f'No-show fee for {rsv_id}', fee)
            sys.notify(user, 'Cancel Reserve', f'ยกเลิกการจอง {rsv_id} มีค่าปรับ {fee}฿')
            return f'✅ Cancelled with no-show fee {fee}฿'
        sys.notify(user, 'Cancel Reserve', f'ยกเลิกการจอง {rsv_id} สำเร็จ ไม่มีค่าปรับ')
        return '✅ Cancelled, no fee'
    except: return '⛔ Cancel Failed'

@app.post("/event/cancel_join")
def cancel_join_event(user_id, event_id):
    try:
        user = sys.search_user_by_id(user_id)
        if not user: raise Exception

        event = sys.search_event_by_id(event_id)
        if not event: raise Exception

        event.remove_attendant(user) 
        
        sys.notify(user, 'Cancel Join Event', f'ยกเลิกการเข้าร่วมกิจกรรม {event.get_topic()} สำเร็จ')
        return '✅ Cancel Join Event Success'
    except:
        return '⛔ Cancel Join Event Failed'
    
@app.post("/event/cancel_event")
def cancel_event(instructor_id, event_id):
    try:
        ins = sys.search_instructor_by_id(instructor_id)
        if not ins: raise Exception

        event = sys.search_event_by_id(event_id)
        if not event: raise Exception

        if event.get_instructor != ins: raise Exception

        for attender in event.get_attendants:
            sys.notify(attender, 'Event Cancelled', f'กิจกรรม {event.get_topic()} ถูกยกเลิกโดยผู้สอน')
        
        sys.remove_event(event)

        return '✅ Cancel Event Success'
    except:
        return '⛔ Cancel Event Failed'

@app.post("/show_event_attenders")
def show_event_attenders(instructor_id, event_id):
    try:
        instructor = sys.search_instructor_by_id(instructor_id)
        if not instructor: raise Exception
        event = sys.search_event_by_id(event_id)
        if not event: raise Exception
        if event.get_instructor != instructor: raise Exception
        result = [attender.show_info() for attender in event.get_attendants]
        return {"message": "Show Event Attenders Complete", "data": result}
    except:
        return "⛔ Show Event Attenders Failed"

@app.get("/show_available_resource")
def show_available_resource():
    try:
        from enum_class import ResourceStatus
        available_resource = []
        for space in sys.get_space_list:
            if space.get_status == ResourceStatus.AVAILABLE:
                available_resource.append(space.show_info())
        for equipment in sys.get_equipment_list:
            if equipment.get_status == ResourceStatus.AVAILABLE:
                available_resource.append(equipment.show_info())
        for material in sys.get_material_list:
            if material.get_status == ResourceStatus.AVAILABLE:
                available_resource.append(material.show_info())
        return {"message": "Show Available Resource Complete", "data": available_resource}
    except Exception as e:
        return {"error": str(e)}
    
@app.get("/show_all_resource")
def show_all_resource():
    try:
        show_resource = []
        for space in sys.get_space_list:
            show_resource.append(space.show_info())
        for equipment in sys.get_equipment_list:
            show_resource.append(equipment.show_info())
        for material in sys.get_material_list:
            show_resource.append(material.show_info())
        return {"message": "Show All Resource Complete", "data": show_resource}
    except Exception as e:
        return {"error": str(e)}

@app.get("/show_all_events")
def show_all_events():
    try:
        show_events = []
        for event in sys.get_event_list: 
            show_events.append(event.show_info())
        return {"message": "Show All Events Complete", "data": show_events}
    except Exception as e:
        return {"error": str(e)}

def run_api():
    uvicorn.run("api_demo:app", host="127.0.0.1", port=8000, reload=True)

if __name__ == "__main__":
    run_api()