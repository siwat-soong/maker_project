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

@app.get("/user_info")
def show_user_info(user_id):
    user = sys.search_user_by_id(user_id)
    return user.show_info()

@app.post("/subscribe")
def subscribe(user_id):
    try:
        user = sys.search_user_by_id(user_id)
        if user is None: raise Exception
        elif user.check_blacklist(): raise Exception
        elif user.check_invoice(): raise Exception
        else: 
            user.subscribe()
            inv = user.create_invoice(InvoiceType.SUBSCRIBE, f'{user.get_name} subscribe member from {datetime.now()} for 365 days', 100)
            return f'✅ Subscribe Success, Please pay fee 100$ to ID: {inv.get_id}'

    except:
        return f'⛔ Subscribe Failed'

@app.post("/pay")
def pay(user_id, inv_id, cost: float, method_id):
    try:
        user = sys.search_user_by_id(user_id)
        inv = user.search_invoice_by_id(inv_id)
        method = sys.search_method_by_id(method_id)
        if(method.validate(inv.get_cost, cost)): 
            change = method.process_payment()
            user.create_receipt(inv, change, method)
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

        # Check User Rights
        if mode != "COMPANY":
            if target_user.check_blacklist(): raise Exception
            adv_res_dur = datetime.now() - start_time
            if adv_res_dur.days > target_user.get_max_reserve_days: raise Exception
            if not target_user.check_expertise(res): raise Exception
            
        if target_user.check_duplicate_cart(res, start_time, end_time): raise Exception

        # Check Resource Availability
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
            lit.get_resource.process_reserve(lit.get_amount, lit.get_reserved_time)

            from resource_class import Material
            if isinstance(lit.get_resource, Material): purchase_list.append(lit)
            else: reserve_list.append(lit)

        # make reservation
        from transaction_class import Reservation
        user.add_reservation(Reservation(user, reserve_list))

        total = 0
        if purchase_list:
            # loop calculate total cost
            for item in purchase_list:
                total += item.get_resource.calculate_fee(user, item.get_amount, None)

            # make invoice
            user.create_invoice(InvoiceType.RESOURCE, "Purchased Material", total)

        # clear line item
        user.clear_line_item()

        return f'✅ Reserve Done, total cost {total}$'

    except:
        return '⛔ Reserve Failed'

# http://127.0.0.1:8000/event/create?admin_id=3308&topic=""&detail=""&start_time=20/03/2026,10:00&end_time=20/03/2026,16:00&instructor_id=4244&space_id=SPA-MEET-001&max_attender=10&join_fee=0
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

        sys.add_event(Event(topic, detail, t, ins, sp, None, max_attender, float(join_fee) + ins.get_fee, ins.get_expertise))

        return '✅ Create Event Success'
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

        return f'✅ Join Event Success, fee = {fee}$'

    except:
        return '⛔ Join Event Failed'

@app.put("/event/add")
def add_equipment_to_event(user_id, event_id):
    try:
        ins = sys.search_instructor_by_id(user_id)
        if not ins: raise Exception

        event = sys.search_event_by_id(event_id)
        if not event: raise Exception

        if event.get_instructor != ins: raise Exception

        lit_list = ins.get_line_item
        if not lit_list: raise Exception
        
        for lit in lit_list:
            if not lit.get_resource.check_reservable(lit.get_reserved_time.get_start_time, lit.get_reserved_time.get_end_time, lit.get_amount): raise Exception
            lit.get_resource.process_reserve(lit.get_amount, lit.get_reserved_time)
        
        event.add_eq(lit_list)

        ins.clear_line_item()

        return '✅ Add to Event Success'
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

            user.create_invoice(InvoiceType.FEE, "Check Out Late Fine", total_fine)
            return f'⚠️ Fine : {total_fine:.2f}$'
        else:
            from enum_class import ResourceStatus, LineItemStatus
            space.update_status(ResourceStatus.IN_USE)
            lit.update_status(LineItemStatus.CHECKED_IN)

            # Check in update status in other 

            lit.set_start_time = now

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

        fee = space.calculate_fee(user, lit.get_amount, lit.get_reserved_time.get_duration)

        lit.update_status(LineItemStatus.COMPLETED)

        user.create_invoice(InvoiceType.RESOURCE, "Check Out", fee)

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

        if lit.get_status != LineItemStatus.CHECKED_IN: raise Exception

        lit.set_end_time = datetime.now()

        fee = eq.calculate_fee(user, lit.get_amount, lit.get_reserved_time.get_duration)

        lit.update_status(LineItemStatus.COMPLETED)

        user.create_invoice(InvoiceType.RESOURCE, "Check Out", fee)

        return f'✅ Return Success, cost = {fee}$'
    except: return '⛔ Return Failed'

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

# Running Section
def run_api():
    uvicorn.run("api_demo:app", host="127.0.0.1", port=8000, reload=True)

if __name__ == "__main__":
    run_api()