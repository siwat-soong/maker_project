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

        new_line_item = LineItem(resource, request.amount, start_time, end_time)
        target_user.add_to_cart(new_line_item)
        return {"message": "✅ Add to Cart Success", "item_id": request.item_id, "user_id": request.user_id}

    except Exception as e:
        return f"❌ Add to Cart Failed: {e}"

if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000,reload=False)