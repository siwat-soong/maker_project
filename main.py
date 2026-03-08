from datetime import datetime
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

@app.post("/create_event")
def create_event(admin_id: str, 
                 event_id: str, 
                 event_topic: str, 
                 event_detail: str, 
                 start_time: str, 
                 end_time: str, 
                 ins_id: str, 
                 resource_id: str, 
                 max_attender: int, 
                 join_fee: float, 
                 certified_topic: str):
    try:
        # หากส่งรูปแบบวันที่มาผิด บรรทัดนี้จะเด้งไปเข้า except ValueError ทันที
        start_dt = datetime.strptime(start_time, "%d/%m/%Y,%H:%M")
        end_dt = datetime.strptime(end_time, "%d/%m/%Y,%H:%M")   

        if start_dt > end_dt: return "⚠️ เวลาเริ่มต้นมากกว่าเวลาสิ้นสุด"

        admin = sys.search_admin_by_id(admin_id)
        if not admin: return "⚠️ คุณไม่ใช่ Admin"
        
        instructor = sys.search_instructor_by_id(ins_id)
        if not instructor: raise Exception(f"ไม่พบข้อมูล Instructor ID: {ins_id}")
        
        resource = sys.search_resource_by_id(resource_id)
        if not resource: raise Exception(f"ไม่พบข้อมูล Resource ID: {resource_id}")
        
        selected_expertise = None

        for exp in Expertise:
            if exp.value == certified_topic:
                selected_expertise = exp
        if not selected_expertise: return f"⚠️ ไม่พบระดับความเชี่ยวชาญ: {certified_topic}"

        line_item_list = sys.search_all_matching_item(resource_id)
        validation = resource.validate_reservable(instructor, 1, start_dt, end_dt, line_item_list)
        
        # --- จุดที่ 1: ใส่ข้อความกำกับใน raise Exception ---
        if not validation: 
            raise Exception("ทรัพยากรไม่ว่าง หรือไม่สามารถจองได้ในช่วงเวลาดังกล่าว")
        else:
            event1 = Event(event_id, event_topic, event_detail, start_dt, end_dt, instructor, resource, max_attender, join_fee, selected_expertise)
            sys.add_event(event1)
            
            all_users = sys.get_all_users()
            for user in all_users:
                noti = Notification(user, event_topic, event_detail)
                sys.add_noti(noti)
            return "✅ create event success"
            
    # --- จุดที่ 2: ดักจับ Error กรณีแปลงวันที่ผิดรูปแบบ ---
    except ValueError:
        print("❌ เกิดข้อผิดพลาด: รูปแบบวันที่ไม่ถูกต้อง")
        return "⚠️ รูปแบบวันที่ผิดพลาด กรุณาใช้ DD/MM/YYYY,HH:MM"
        
    # --- จุดที่ 3: จับ Exception ตัวอื่นๆ และดึงข้อความมาแสดง ---
    except Exception as e:
        print(f"❌ เกิดข้อผิดพลาดในระบบ: {str(e)}") # ปริ้นลง Terminal เพื่อให้คนเขียนโค้ดเห็น
        return f"❌ create event failed: {str(e)}" # ส่งกลับไปบอกหน้าบ้าน (เช่น Postman)


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)