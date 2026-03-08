from fastapi import FastAPI, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from datetime import datetime
from typing import List
import uvicorn
from controller import *
from payment_class import Cash, QRCode

maker = None
app = FastAPI()

@app.on_event("startup")
def startup_event():
    global maker
    maker = system_init()

class ReturnRequest(BaseModel):
    user_id: str
    reservation_id: str
    item_ids: List[str]

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
            return "⚠️ payment_method ต้องเป็น 'cash' หรือ 'qr'"

        target_user = maker.search_user_by_id(request.user_id)
        if not target_user:
            return f"⚠️ ไม่พบ User '{request.user_id}'"

        return target_user.pay_invoice(request.user_id, request.invoice_ids, request.amount, selected_pm)

    except Exception as e:
        print(f"ERROR: {e}")
        return f"❌ Pay Invoices Failed: {e}"

if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)