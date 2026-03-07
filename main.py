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

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/ping")
def ping():
    return {"status": "ok", "message": "pong"}

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
    result = maker.process_return(request.user_id, request.reservation_id, request.item_ids)
    if "error" in result:
        raise HTTPException(status_code=404, detail=result["error"])
    return {
        "status": "success",
        "timestamp": datetime.now(),
        "data": {
            "id": result.get("receipt_id") or result.get("invoice_id"),
            "type": "RECEIPT" if "receipt_id" in result else "INVOICE",
            "cost": result["cost"],
            "payment_status": result["payment_status"],
            "returned_items": result.get("returned_items", request.item_ids),
            "message": result["message"],
            "currency": "THB"
        }
    }

class PayRequest(BaseModel):
    user_id: str
    invoice_ids: List[str]
    amount: float
    payment_method: str = "cash"

@app.post("/pay")
def pay_invoices_api(request: PayRequest):
    try:
        if maker is None:
            raise HTTPException(status_code=500, detail="System not initialized")

        selected_pm = None
        for pm in maker._Club__payment_method_list:
            if request.payment_method.lower() in pm.__class__.__name__.lower():
                selected_pm = pm
                break
        if not selected_pm:
            raise HTTPException(status_code=400, detail="payment_method ต้องเป็น 'cash' หรือ 'qr'")

        target_user = next(
            (u for u in maker._Club__user_list if u._User__user_id == request.user_id), None
        )
        if not target_user:
            raise HTTPException(status_code=404, detail=f"User '{request.user_id}' not found")

        result = target_user.pay_invoices(request.user_id, request.invoice_ids, request.amount, selected_pm)

        if result.get("status") == "failed":
            raise HTTPException(status_code=400, detail=result["message"])

        return {
            "status": "success",
            "receipt_ids": result["receipt_ids"],
            "total": result["total"],
            "invoice_count": len(request.invoice_ids),
            "payment_method": request.payment_method
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"{type(e).__name__}: {str(e)}")

@app.get("/debug/invoices/{user_id}")
def debug_invoices(user_id: str):
    target_user = next(
        (u for u in maker._Club__user_list if u._User__user_id == user_id), None
    )
    if not target_user:
        raise HTTPException(status_code=404, detail="User not found")
    return {
        "user_id": user_id,
        "invoices": [
            {"invoice_id": inv.get_id, "cost": inv.get_cost(), "paid": inv.is_purchased()}
            for inv in target_user._User__invoice_list
        ]
    }

if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=False)