from datetime import datetime
from controller import *
from fastapi import FastAPI
import uvicorn

sys = system_init()

''' API Goes Here '''
app = FastAPI()

@app.get("/")
def test_route():
    return {"message": "Test Route"}

@app.post("/add_to_cart")
def add_to_cart(user_id, item_id, start_time, end_time, amount):
    try:
        start_time = datetime.strptime(start_time, "%d/%m/%Y,%H:%M")
        end_time = datetime.strptime(end_time, "%d/%m/%Y,%H:%M")

        if start_time > end_time: return "⚠️ เวลาเริ่มต้นมากกว่าเวลาสิ้นสุด"

        target_user = sys.search_user_by_id(user_id)
        resource = sys.search_resource_by_id(item_id)

        # Validate duplicate cart added
        res = list()
        for item in target_user.get_user_item_list:
            if item.get_resource.get_id == item_id and item.get_resource.check_overlap_date_time(start_time, item.get_start_date_time, end_time, item.get_end_date_time):
                return "⚠️ คุณเคยเพิ่มสินค้าที่มีรายละเอียดเดียวกันแล้ว"

        # Validate all confirm reservation
        line_item_list = sys.search_all_matching_item(item_id)

        validation = resource.validate_reservable(target_user, amount, start_time, end_time, line_item_list)

        if not validation: raise Exception
        else:
            new_line_item = LineItem(resource, amount, start_time, end_time)
            target_user.add_item_list(new_line_item)
            return "✅ Add to Cart Success"
    except: return "❌ Add to Cart Failed"

if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
