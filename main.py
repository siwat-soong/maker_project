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
def check_out(user_id, reservation_id, space_id, check_out_time, damage_item_id_list):
    try:
        dmg_item_list = damage_item_id_list.split(",")

        user = sys.search_user_by_id(user_id)
        res = user.search_reservation_by_id(reservation_id)

        space = sys.search_space_by_id(space_id)

        lit = res.search_line_item_by_resource(space)
        if lit is None: raise Exception

        return lit
    except:
        return "❌ Check Out Failed"

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
