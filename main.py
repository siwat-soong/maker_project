from controller import *
from fastapi import FastAPI
import uvicorn

sys = system_init()

''' API Goes Here '''
app = FastAPI()

@app.get("/")
def test_route():
    return {"message": "Test Route"}

@app.post("/check-out")
def check_out(user_id, reservation_id, space_id, check_out_time, damage_item_id_list=None):
    try:
        check_out_time = datetime.strptime(check_out_time, "%d/%m/%Y,%H:%M")
        
        dmg_item_list = []
        if damage_item_id_list is not None: 
            dmg_item_list = damage_item_id_list.split(",")

        user = sys.search_user_by_id(user_id)
        res = user.search_reservation_by_id(reservation_id)
        if (res.get_status != ReserveStatus.CHECKED_IN): raise Exception("Invalid Status")

        space = sys.search_space_by_id(space_id)

        lit = res.search_line_item_by_resource(space)

        if lit is None: raise Exception()
        else:
            cost = int(res.calculate_check_out_cost(lit, check_out_time, dmg_item_list))
            inv = Invoice(user, None, None, res, cost)
            user.add_invoice(inv)
            res.update_status(ReserveStatus.COMPLETED)
            return f"✅ Check Out success | total cost = {cost}$"


    except Exception as e:
        return f"❌ Check Out Failed {e}"

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
