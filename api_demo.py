from fastapi import FastAPI
import uvicorn
from controller import system_init
from enum_class import InvoiceType
from datetime import datetime

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
            return '✅ Pay Success'
        else: raise Exception
    except:
        return f'⛔ Pay Failed'

# Running Section
def run_api():
    uvicorn.run("api_demo:app", host="127.0.0.1", port=8000, reload=True)

if __name__ == "__main__":
    run_api()