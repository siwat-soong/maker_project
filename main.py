from fastapi import FastAPI, Form, HTTPException
from pydantic import BaseModel
from datetime import datetime, timedelta
import uvicorn
from controller import *
from payment_class import Cash
from payment_class import QRCode

maker = None
app = FastAPI()

# 2. ใช้ Startup Event เพื่อให้รัน system_init() แค่ 1 รอบตอนเปิดเซิร์ฟเวอร์
@app.on_event("startup")
def startup_event():
    global maker
    maker = system_init()

class ReceiptDetail(BaseModel):
    receipt_id: str
    cost: float
    payment_status: str
    currency: str = "THB"

class ReturnResponse(BaseModel):
    status: str
    message: str
    timestamp: datetime
    data: ReceiptDetail

@app.post("/return", response_model=ReturnResponse)
def return_resource_api(
    user_id: str = Form(...),
    reservation_id: str = Form(...),
    item_id: str = Form(...)
):
    result = maker.process_return(user_id,reservation_id,item_id)
    
    if "error" in result:
        raise HTTPException(status_code=404, detail=result["error"])
    
    return {
        "status": "success",
        "message": f"Process Complete. ({result['message']}:{item_id})",
        "timestamp": datetime.now(),
        "data": {
            "invoice_id": result["invoice_id"],
            "cost": result["cost"],
            "payment_status": result["payment_status"]
        }
    }

class PayReceiptRequest(BaseModel):
    user_id: str
    receipt_id: str
    amount: float

@app.post("/pay")
def pay_receipt(request: PayReceiptRequest):
    target_user = next((u for u in maker.get_user_list() if u.get_id == request.user_id), None)
    
    if not target_user:
        raise HTTPException(status_code=404, detail="User not found")

    result = target_user.pay_receipt(request.receipt_id, request.amount)
    
    if result["status"] == "failed":
        raise HTTPException(status_code=400, detail=result["message"])
        
    return result

if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000,reload=True)