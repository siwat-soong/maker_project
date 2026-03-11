from fastmcp import FastMCP
import requests

mcp = FastMCP("maker_club_mcp")

BASE = "http://127.0.0.1:8000"

@mcp.tool()
def show_user_info(user_id: str) -> dict:
    """
    ดูข้อมูลส่วนตัวของสมาชิก (User/Instructor/Admin)
    ใช้เมื่อต้องการตรวจสอบข้อมูลโปรไฟล์ สิทธิ์ ทรัพยากรในตะกร้า หรือใบแจ้งหนี้ของ User
    """
    return requests.get(f"{BASE}/user_info", params={"user_id": user_id}).json()

@mcp.tool()
def show_notifications(user_id: str) -> dict:
    """
    ดึงรายการข้อความแจ้งเตือน (Notifications) ทั้งหมดของ User
    """
    result = requests.get(f"{BASE}/notifications", params={"user_id": user_id}).json()
    if isinstance(result, list):
        return {"notifications": result}
    return result

@mcp.tool()
def subscribe(user_id: str) -> dict:
    """
    ใช้สำหรับสมัครสมาชิกรายปีให้ User
    ระบบจะสร้างใบแจ้งหนี้ (Invoice) ค่าสมัครสมาชิก 100 บาท (ต้องนำรหัสบิลไปชำระเงินต่อ)
    """
    return requests.post(f"{BASE}/subscribe", params={"user_id": user_id}).json()

@mcp.tool()
def pay(user_id: str, inv_id: str, cost: float, method_id: str) -> dict:
    """
    ใช้สำหรับชำระเงินบิล (Invoice) ต่างๆ
    - inv_id: รหัสใบแจ้งหนี้ (เช่น INV-xxxx)
    - cost: จำนวนเงินที่จ่ายเข้ามา
    - method_id: รหัสวิธีชำระเงิน (เช่น C-0001 สำหรับเงินสด)
    """
    return requests.post(f"{BASE}/pay", params={
        "user_id": user_id,
        "inv_id": inv_id,
        "cost": cost,
        "method_id": method_id
    }).json()

@mcp.tool()
def add_to_cart(user_id: str, item_id: str, start_time: str, end_time: str, amount: float = 1) -> dict:
    """
    นำทรัพยากร (สถานที่/อุปกรณ์/วัสดุ) เข้าตะกร้า (Cart) ก่อนทำการจอง
    !!! สำคัญ: เวลา start_time และ end_time ต้องอยู่ในรูปแบบ "dd/mm/yyyy,HH:MM" เท่านั้น (เช่น "11/03/2026,15:00")
    ห้ามมีเว้นวรรคหลังเครื่องหมายลูกน้ำเด็ดขาด
    """
    return requests.post(f"{BASE}/add_to_cart", params={
        "user_id": user_id,
        "item_id": item_id,
        "start_time": start_time,
        "end_time": end_time,
        "amount": amount
    }).json()

@mcp.tool()
def reserve(user_id: str) -> dict:
    """
    ยืนยันการจองทรัพยากรทั้งหมดที่อยู่ในตะกร้า (Cart) ของ User
    หากสำเร็จจะได้รหัสการจอง (Reservation ID) กลับมา
    """
    return requests.post(f"{BASE}/reserve", params={"user_id": user_id}).json()

@mcp.tool()
def cancel_reserve(user_id: str, rsv_id: str) -> dict:
    """
    ยกเลิกการจองทรัพยากร
    - rsv_id: รหัสการจอง (เช่น RSV-xxxx)
    """
    return requests.post(f"{BASE}/cancel_reserve", params={
        "user_id": user_id,
        "rsv_id": rsv_id
    }).json()

@mcp.tool()
def check_in(user_id: str, rsv_id: str, space_id: str, start_time: str) -> dict:
    """
    Check-in เข้าใช้พื้นที่ที่ได้ทำการจองไว้
    !!! สำคัญ: เวลา start_time ต้องอยู่ในรูปแบบ "dd/mm/yyyy,HH:MM" เท่านั้น (เช่น "11/03/2026,15:00")
    """
    return requests.post(f"{BASE}/checkin", params={
        "user_id": user_id,
        "rsv_id": rsv_id,
        "space_id": space_id,
        "start_time": start_time
    }).json()

@mcp.tool()
def check_out(user_id: str, rsv_id: str, space_id: str, start_time: str) -> dict:
    """
    Check-out คืนพื้นที่ที่ใช้งานเสร็จแล้ว
    !!! สำคัญ: เวลา start_time ตอนแรกที่เข้าใช้ ต้องอยู่ในรูปแบบ "dd/mm/yyyy,HH:MM" เท่านั้น (เช่น "11/03/2026,15:00")
    """
    return requests.post(f"{BASE}/checkout", params={
        "user_id": user_id,
        "rsv_id": rsv_id,
        "space_id": space_id,
        "start_time": start_time
    }).json()

@mcp.tool()
def return_equipment(user_id: str, rsv_id: str, equipment_id: str, start_time: str) -> dict:
    """
    คืนอุปกรณ์ (Equipment) ที่ได้ทำการจองและนำไปใช้งาน
    !!! สำคัญ: เวลา start_time ตอนแรกที่เข้าใช้ ต้องอยู่ในรูปแบบ "dd/mm/yyyy,HH:MM" เท่านั้น (เช่น "11/03/2026,15:00")
    """
    return requests.post(f"{BASE}/return_eq", params={
        "user_id": user_id,
        "rsv_id": rsv_id,
        "equipment_id": equipment_id,
        "start_time": start_time
    }).json()

@mcp.tool()
def create_event(admin_id: str, topic: str, detail: str, start_time: str, end_time: str,
                 instructor_id: str, space_id: str, max_attender: int, join_fee: float) -> dict:
    """
    สร้างกิจกรรมหรือ Workshop (เฉพาะ Admin)
    !!! สำคัญ: เวลา start_time และ end_time ต้องอยู่ในรูปแบบ "dd/mm/yyyy,HH:MM" เท่านั้น (เช่น "15/03/2026,13:00")
    """
    return requests.post(f"{BASE}/event/create", params={
        "admin_id": admin_id,
        "topic": topic,
        "detail": detail,
        "start_time": start_time,
        "end_time": end_time,
        "instructor_id": instructor_id,
        "space_id": space_id,
        "max_attender": max_attender,
        "join_fee": join_fee
    }).json()

@mcp.tool()
def join_event(user_id: str, event_id: str) -> dict:
    """
    ใช้สำหรับให้ผู้ใช้งาน (User) สมัครเข้าร่วมกิจกรรม (Event)
    """
    return requests.post(f"{BASE}/event/join", params={
        "user_id": user_id,
        "event_id": event_id
    }).json()

@mcp.tool()
def cancel_join_event(user_id: str, event_id: str) -> dict:
    """
    ใช้สำหรับให้ผู้ใช้งาน (User) ยกเลิกการเข้าร่วมกิจกรรม (Event) ที่เคยสมัครไว้
    """
    return requests.post(f"{BASE}/event/cancel_join", params={
        "user_id": user_id,
        "event_id": event_id
    }).json()

@mcp.tool()
def cancel_event(instructor_id: str, event_id: str) -> dict:
    """
    ใช้สำหรับยกเลิกกิจกรรม (Event) ทั้งงาน โดยผู้สอน (Instructor)
    """
    return requests.post(f"{BASE}/event/cancel_event", params={
        "instructor_id": instructor_id,
        "event_id": event_id
    }).json()

@mcp.tool()
def add_equipment_to_event(user_id: str, event_id: str) -> dict:
    """
    ใช้สำหรับผู้สอนดึงอุปกรณ์/วัสดุที่อยู่ในตะกร้า (Cart) ของตนเอง เข้าไปผูกติดกับกิจกรรม (Event)
    """
    return requests.put(f"{BASE}/event/add", params={
        "user_id": user_id,
        "event_id": event_id
    }).json()

@mcp.tool()
def add_certificate(instructor_id: str, event_id: str, user_id: str, score: float) -> dict:
    """
    ใช้สำหรับผู้สอนให้คะแนนและมอบเกียรติบัตร (Certificate) ให้กับผู้เข้าร่วมกิจกรรม
    - หาก score >= 50 จะได้ผลประเมิน PASS
    """
    return requests.post(f"{BASE}/event/certificate", params={
        "instructor_id": instructor_id,
        "event_id": event_id,
        "user_id": user_id,
        "score": score
    }).json()

@mcp.tool()
def show_event_attenders(instructor_id: str, event_id: str) -> dict:
    """
    ใช้สำหรับดูรายชื่อผู้ที่เข้าร่วมกิจกรรม (Attendants) ทั้งหมดใน Event นั้น
    """
    return requests.post(f"{BASE}/show_event_attenders", params={
        "instructor_id": instructor_id,
        "event_id": event_id
    }).json()

@mcp.tool()
def show_all_events() -> dict:
    """
    ดึงรายชื่อกิจกรรม (Events) หรือ Workshop ทั้งหมดที่มีในระบบ
    """
    return requests.get(f"{BASE}/show_all_events").json()

@mcp.tool()
def show_available_resource() -> dict:
    """
    ดึงรายการทรัพยากร (สถานที่/อุปกรณ์/วัสดุ) เฉพาะที่สถานะว่างพร้อมใช้งาน (AVAILABLE) เท่านั้น
    """
    return requests.get(f"{BASE}/show_available_resource").json()

@mcp.tool()
def show_all_resource() -> dict:
    """
    ดึงรายการทรัพยากรทั้งหมดที่มีในศูนย์ Maker Space (รวมทั้งที่ว่างและไม่ว่าง)
    """
    return requests.get(f"{BASE}/show_all_resource").json()

if __name__ == "__main__":
    mcp.run()