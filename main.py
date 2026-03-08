from fastapi import FastAPI, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from datetime import datetime
from typing import List
import uvicorn
from controller import *
from payment_class import Cash, QRCode
from contextlib import asynccontextmanager

maker = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    global maker
    maker = system_init()
    yield

app = FastAPI(lifespan=lifespan)

from fastapi.middleware.cors import CORSMiddleware
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

@app.get("/ping")
def ping():
    return {"status": "ok", "message": "pong"}

@app.get("/event/{event_id}/attenders")
def get_event_attenders(event_id: str, requester_id: str):
    # เช็ค permission
    is_admin = any(a.get_id == requester_id for a in maker._Club__admin_list)
    is_instructor = any(i.get_id == requester_id for i in maker._Club__instructor_list)
    if not is_admin and not is_instructor:
        raise HTTPException(status_code=403, detail="Permission denied: Admin or Instructor only")

    event = maker.search_event_by_id(event_id)
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")

    return {
        "event_id": event_id,
        "status": event._Event__status.value,
        "attenders": event.get_attenders(),
        "count": len(event._Event__attenders)
    }

class ReturnRequest(BaseModel):
    user_id: str
    reservation_id: str
    item_ids: List[str]

class CloseEventRequest(BaseModel):
    instructor_id: str
    event_id: str
    expired_days: int = None  # None = ไม่มีวันหมดอายุ

@app.post("/event/close")
def end_event_api(request: CloseEventRequest):
    result = maker.close_event(
        request.instructor_id,
        request.event_id,
        request.expired_days
    )
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    return result

@app.post("/return")
def return_resource_api(request: ReturnRequest):
    try:
        result = maker.process_return(request.user_id, request.reservation_id, request.item_ids)

        if "error" in result:
            return f"⚠️ {result['error']}"

        return result

    except Exception as e:
        return f"❌ Return Failed: {e}"
    
class PayRequest(BaseModel):
    user_id: str
    invoice_ids: List[str]
    amount: float
    payment_method: str

@app.post("/pay_invoice")
def pay_invoice_api(request: PayRequest):
    try:
        selected_pm = maker.search_payment_method_by_name(request.payment_method)
        if not selected_pm:
            return "⚠️ payment_method need to be 'cash' or 'qr'"

        target_user = maker.search_user_by_id(request.user_id)
        if not target_user:
            return f"⚠️ User not found: '{request.user_id}'"

        return target_user.pay_invoice(request.user_id, request.invoice_ids, request.amount, selected_pm)

    except Exception as e:
        print(f"ERROR: {e}")
        return f"❌ Pay Invoices Failed: {e}"
    
@app.get("/show/reservations")
def show_reserve_history(user_id:str):
    try:
        target_user = maker.search_user_by_id(user_id)
        if not target_user:
            return f"⚠️ User not found: '{user_id}'"
        result = target_user.list_reserve_history()
        return result
    except Exception as e:
        print(f"ERROR: {e}")
        return f"❌ Not found: {e}"
    
@app.get("/show/event")
def show_reserve_history(admin_id:str, event_id:str):
    try:
        target_admin = maker.search_admin_by_id(admin_id)
        if not target_admin:
            return f"⚠️ You are not admin: '{admin_id}'"
        result = maker.show_event_attenders(event_id)
        return result
    except Exception as e:
        print(f"ERROR: {e}")
        return f"❌ Not found: {e}"

class CancelRequest(BaseModel):
    user_id: str
    reservation_id: str

@app.post("/cancel")
def cancel_reservation(request: CancelRequest):
    try:
        target_user = maker.search_user_by_id(request.user_id)
        if not target_user:
            return f"⚠️ User not found: '{request.user_id}'"
        result = target_user.cancel_reservation(request.reservation_id)
        return result
    except Exception as e:
        print(f"ERROR: {e}")
        return f"❌ Not found: {e}"
    
class ReserveRequest(BaseModel):
    user_id: str
    due_date: str  # format: YYYY-MM-DD HH:MM

@app.post("/reserve")
def reserve_resource_api(request: ReserveRequest):
    try:
        due_date = datetime.strptime(request.due_date, "%Y-%m-%d %H:%M")
    except ValueError:
        raise HTTPException(status_code=400, detail="due_date format must be YYYY-MM-DD HH:MM")

    result = maker.reserve(request.user_id, due_date)

    if isinstance(result, dict) and "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    return result

class CartRequest(BaseModel):
    user_id: str
    item_id: str
    start_time: str  # DD/MM/YYYY,HH:MM
    end_time: str
    amount: int = 1

@app.post("/add_to_cart")
def add_to_cart_api(request: CartRequest):
    try:
        start_time = datetime.strptime(request.start_time, "%d/%m/%Y,%H:%M")
        end_time = datetime.strptime(request.end_time, "%d/%m/%Y,%H:%M")

        if start_time >= end_time:
            return "⚠️ start_time ต้องน้อยกว่า end_time"

        target_user = maker.search_user_by_id(request.user_id)
        if not target_user:
            return f"⚠️ User not found: '{request.user_id}'"

        resource = maker.search_resource_by_id(request.item_id)
        if not resource:
            return f"⚠️ Resource not found: '{request.item_id}'"

        # เช็ค certificate ถ้า resource ต้องการ
        if isinstance(resource, Equipment):
            required_cert = resource.get_required_cert
            if required_cert and not target_user.check_certified(required_cert):
                return {
                    "error": f"⚠️ ไม่มีใบ Certificate ที่จำเป็น",
                    "required_cert": required_cert.value,
                    "item_id": request.item_id
                }

        new_line_item = LineItem(resource, request.amount, start_time, end_time)
        target_user.add_to_cart(new_line_item)
        return {"message": "✅ Add to Cart Success", "item_id": request.item_id, "user_id": request.user_id}

    except Exception as e:
        return f"❌ Add to Cart Failed: {e}"

@app.get("/events")
def list_events(user_id: str = None):
    events = []
    for event in maker._Club__event_list:
        events.append({
            "event_id": event.get_id,
            "status": event._Event__status.value,
            "topic": event._Event__event_topic,
            "detail": event._Event__event_detail,
            "start_time": event._Event__start_time.strftime("%d/%m/%Y %H:%M"),
            "end_time": event._Event__end_time.strftime("%d/%m/%Y %H:%M"),
            "join_fee": event.join_fee,
            "attenders": len(event._Event__attenders),
            "max_attender": event._Event__max_attender,
            "certified_topic": event._Event__certified_topic.value,
            "already_joined": event.check_attender(user_id) if user_id else None
        })
    return events

class JoinEventRequest(BaseModel):
    user_id: str
    event_id: str

@app.post("/event/join")
def join_event(request: JoinEventRequest):
    target_user = maker.search_user_by_id(request.user_id)
    if not target_user:
        raise HTTPException(status_code=404, detail=f"User not found: {request.user_id}")

    event = maker.search_event_by_id(request.event_id)
    if not event:
        raise HTTPException(status_code=404, detail=f"Event not found: {request.event_id}")

    if not event.check_availability():
        raise HTTPException(status_code=400, detail=f"Event is not open (status: {event._Event__status.value})")

    if event.check_attender(request.user_id):
        raise HTTPException(status_code=400, detail="Already joined this event")

    try:
        event.join(target_user)
    except SystemError as e:
        raise HTTPException(status_code=400, detail=str(e))

    return {
        "message": "✅ Joined event successfully",
        "event_id": request.event_id,
        "user_id": request.user_id,
        "attenders": len(event._Event__attenders),
        "max_attender": event._Event__max_attender
    }

class CreateEventRequest(BaseModel):
    admin_id: str
    event_id: str
    event_topic: str
    event_detail: str
    start_time: str   # DD/MM/YYYY,HH:MM
    end_time: str     # DD/MM/YYYY,HH:MM
    ins_id: str
    resource_id: str
    max_attender: int
    join_fee: float
    certified_topic: str  # ค่าจาก Expertise enum เช่น BASIC, ADVANCE, LASER_CUTTER

@app.post("/create_event")
def create_event(request: CreateEventRequest):
    try:
        start_dt = datetime.strptime(request.start_time, "%d/%m/%Y,%H:%M")
        end_dt = datetime.strptime(request.end_time, "%d/%m/%Y,%H:%M")
    except ValueError:
        raise HTTPException(status_code=400, detail="รูปแบบวันที่ผิด กรุณาใช้ DD/MM/YYYY,HH:MM")

    if start_dt >= end_dt:
        raise HTTPException(status_code=400, detail="⚠️ start_time ต้องน้อยกว่า end_time")

    admin = maker.search_admin_by_id(request.admin_id)
    if not admin:
        raise HTTPException(status_code=403, detail="⚠️ คุณไม่ใช่ Admin")

    instructor = maker.search_instructor_by_id(request.ins_id)
    if not instructor:
        raise HTTPException(status_code=404, detail=f"ไม่พบ Instructor ID: {request.ins_id}")

    resource = maker.search_resource_by_id(request.resource_id)
    if not resource:
        raise HTTPException(status_code=404, detail=f"ไม่พบ Resource ID: {request.resource_id}")

    from enum_class import Expertise
    selected_expertise = next((e for e in Expertise if e.value == request.certified_topic), None)
    if not selected_expertise:
        raise HTTPException(status_code=400, detail=f"⚠️ ไม่พบ Expertise: {request.certified_topic}")

    line_item_list = maker.search_all_matching_item(request.resource_id)
    if not resource.validate_reservable(instructor, 1, start_dt, end_dt, line_item_list):
        raise HTTPException(status_code=400, detail="ทรัพยากรไม่ว่างในช่วงเวลาดังกล่าว")

    event = Event(request.event_id, request.event_topic, request.event_detail,
                  start_dt, end_dt, instructor, resource,
                  request.max_attender, request.join_fee, selected_expertise)
    maker.add_event(event)

    # แจ้งเตือน users ทุกคน
    for user in maker.get_all_users():
        noti = Notification(user, request.event_topic, request.event_detail)
        maker.add_notification(noti)

    return {
        "message": "✅ create event success",
        "event_id": request.event_id,
        "event_topic": request.event_topic,
        "start_time": request.start_time,
        "end_time": request.end_time,
        "instructor": request.ins_id,
        "max_attender": request.max_attender
    }

if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000,reload=False)