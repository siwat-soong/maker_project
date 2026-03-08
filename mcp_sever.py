from fastmcp import FastMCP
import requests

mcp = FastMCP("oop-project")

BASE = "http://127.0.0.1:8000"


# ──────────────────────────────────────────────
# SYSTEM
# ──────────────────────────────────────────────

@mcp.tool()
def ping() -> dict:
    """ตรวจสอบว่า MakerClub server ทำงานอยู่หรือไม่

    ตัวอย่าง: "เช็คว่า server ทำงานอยู่ไหม"
    """
    return requests.get(f"{BASE}/ping").json()


# ──────────────────────────────────────────────
# CART & RESERVE
# ──────────────────────────────────────────────

@mcp.tool()
def add_to_cart_api(user_id: str, item_id: str, start_time: str, end_time: str, amount: int = 1) -> dict:
    """เพิ่มอุปกรณ์เข้าตะกร้าของ user

    Args:
        user_id: รหัส user เช่น USE-001
        item_id: รหัสอุปกรณ์ เช่น TOOL-001, LSC-001, 3DP-001
        start_time: วันเวลาเริ่ม รูปแบบ DD/MM/YYYY,HH:MM เช่น 20/03/2026,10:00
        end_time: วันเวลาสิ้นสุด รูปแบบ DD/MM/YYYY,HH:MM เช่น 23/03/2026,10:00
        amount: จำนวน (default 1)

    ตัวอย่าง: "เพิ่ม laser cutter เข้าตะกร้าของ Jane ตั้งแต่ 20 ถึง 23 มีนาคม"
    """
    return requests.post(f"{BASE}/add_to_cart", json={
        "user_id": user_id,
        "item_id": item_id,
        "start_time": start_time,
        "end_time": end_time,
        "amount": amount
    }).json()


@mcp.tool()
def reserve_resource_api(user_id: str, due_date: str) -> dict:
    """ยืนยันการจองจาก cart ของ user (ต้อง add_to_cart ก่อน)

    Args:
        user_id: รหัส user เช่น USE-001
        due_date: วันคืน รูปแบบ YYYY-MM-DD HH:MM เช่น 2026-03-23 10:00

    ตัวอย่าง: "ยืนยันการจองของ Jane ให้คืนวันที่ 23 มีนาคม"
    """
    return requests.post(f"{BASE}/reserve", json={
        "user_id": user_id,
        "due_date": due_date
    }).json()


@mcp.tool()
def cancel_reservation(user_id: str, reservation_id: str) -> dict:
    """ยกเลิก reservation ที่มีสถานะ CONFIRMED

    Args:
        user_id: รหัส user เช่น USE-001
        reservation_id: รหัสการจอง เช่น REV-JANE-001

    ตัวอย่าง: "ยกเลิกการจอง REV-JANE-001 ของ Jane"
    """
    return requests.post(f"{BASE}/cancel", json={
        "user_id": user_id,
        "reservation_id": reservation_id
    }).json()


@mcp.tool()
def show_reserve_history(user_id: str) -> dict:
    """ดูประวัติการจองทั้งหมดของ user

    Args:
        user_id: รหัส user เช่น USE-001, USE-002

    ตัวอย่าง: "ดูการจองทั้งหมดของ Jira"
    """
    return requests.get(f"{BASE}/show/reservations", params={"user_id": user_id}).json()


# ──────────────────────────────────────────────
# RETURN & PAY
# ──────────────────────────────────────────────

@mcp.tool()
def return_resource_api(user_id: str, reservation_id: str, item_ids: list) -> dict:
    """คืนอุปกรณ์ — ถ้าไม่มีค่าปรับได้ Receipt ทันที ถ้ามีได้ Invoice

    Args:
        user_id: รหัส user เช่น USE-002
        reservation_id: รหัสการจอง เช่น REV-JIRA-001
        item_ids: รายการ item ที่จะคืน เช่น ["LSC-001"]

    ตัวอย่าง: "คืน laser cutter ของ Jira จาก REV-JIRA-001"
    """
    return requests.post(f"{BASE}/return", json={
        "user_id": user_id,
        "reservation_id": reservation_id,
        "item_ids": item_ids
    }).json()


@mcp.tool()
def pay_invoice_api(user_id: str, invoice_ids: list, amount: float, payment_method: str = "cash") -> dict:
    """จ่ายค่าปรับ (ต้องมี invoice_id จาก return_item ก่อน)

    Args:
        user_id: รหัส user เช่น USE-002
        invoice_ids: รายการ invoice ที่จะจ่าย เช่น ["INV-1234567890"]
        amount: จำนวนเงิน เช่น 100.0
        payment_method: วิธีชำระ "cash" หรือ "qr" (default: cash)

    ตัวอย่าง: "จ่ายค่าปรับ 100 บาท ด้วยเงินสดของ Jira"
    """
    return requests.post(f"{BASE}/pay_invoice", json={
        "user_id": user_id,
        "invoice_ids": invoice_ids,
        "amount": amount,
        "payment_method": payment_method
    }).json()


# ──────────────────────────────────────────────
# EVENT
# ──────────────────────────────────────────────

@mcp.tool()
def list_events(user_id: str = None) -> list:
    """ดูรายการ event ทั้งหมด พร้อมเช็คว่า user join แล้วหรือยัง

    Args:
        user_id: รหัส user (optional) เช่น USE-001 — ถ้าใส่จะบอกว่า already_joined หรือเปล่า

    ตัวอย่าง: "ดู event ทั้งหมด" หรือ "Jane เข้าร่วม event ไหนไปแล้วบ้าง"
    """
    params = {}
    if user_id:
        params["user_id"] = user_id
    return requests.get(f"{BASE}/events", params=params).json()


@mcp.tool()
def join_event(user_id: str, event_id: str) -> dict:
    """เข้าร่วม event (event ต้องมีสถานะ OPEN)

    Args:
        user_id: รหัส user เช่น USE-001
        event_id: รหัส event เช่น EV-001

    ตัวอย่าง: "ให้ Jane เข้าร่วม EV-001"
    """
    return requests.post(f"{BASE}/event/join", json={
        "user_id": user_id,
        "event_id": event_id
    }).json()


@mcp.tool()
def create_event(admin_id: str, event_id: str, event_topic: str, event_detail: str,
                 start_time: str, end_time: str, ins_id: str, resource_id: str,
                 max_attender: int, join_fee: float, certified_topic: str) -> dict:
    """สร้าง event ใหม่ (Admin เท่านั้น)

    Args:
        admin_id: รหัส admin เช่น ADM-001
        event_id: รหัส event ใหม่ เช่น EV-002
        event_topic: ชื่อ event เช่น "Laser Cutting Basics"
        event_detail: รายละเอียด เช่น "เรียนรู้การใช้ laser cutter"
        start_time: รูปแบบ DD/MM/YYYY,HH:MM เช่น 20/03/2026,10:00
        end_time: รูปแบบ DD/MM/YYYY,HH:MM เช่น 20/03/2026,13:00
        ins_id: รหัส instructor เช่น INS-001
        resource_id: รหัสห้องที่ใช้ เช่น LAB-001
        max_attender: จำนวนที่รับสูงสุด เช่น 10
        join_fee: ค่าสมัคร เช่น 100.0
        certified_topic: ระดับ cert ที่ได้รับ: BASIC, ADVANCE, THREE_D_PRINTER, LASER_CUTTER

    ตัวอย่าง: "สร้าง event Laser Cutting วันที่ 20 มีนา สำหรับ 10 คน ค่าสมัคร 100 บาท"
    """
    return requests.post(f"{BASE}/create_event", json={
        "admin_id": admin_id,
        "event_id": event_id,
        "event_topic": event_topic,
        "event_detail": event_detail,
        "start_time": start_time,
        "end_time": end_time,
        "ins_id": ins_id,
        "resource_id": resource_id,
        "max_attender": max_attender,
        "join_fee": join_fee,
        "certified_topic": certified_topic
    }).json()


@mcp.tool()
def end_event_api(instructor_id: str, event_id: str, expired_days: int = None) -> dict:
    """ปิด event และออก Certificate ให้ผู้เข้าร่วมทุกคน

    Args:
        instructor_id: รหัส instructor เช่น INS-002
        event_id: รหัส event เช่น EV-001
        expired_days: อายุ cert (วัน) เช่น 365 — ถ้าไม่ใส่ = ไม่มีวันหมดอายุ

    ตัวอย่าง: "ปิด EV-001 และออก cert อายุ 1 ปี"
    """
    return requests.post(f"{BASE}/event/close", json={
        "instructor_id": instructor_id,
        "event_id": event_id,
        "expired_days": expired_days
    }).json()


@mcp.tool()
def get_event_attenders(event_id: str, requester_id: str) -> dict:
    """ดูรายชื่อผู้เข้าร่วม event (Admin หรือ Instructor เท่านั้น)

    Args:
        event_id: รหัส event เช่น EV-001
        requester_id: รหัส admin/instructor เช่น ADM-001, INS-001

    ตัวอย่าง: "ดูรายชื่อคนใน EV-001 โดย Tom"
    """
    return requests.get(f"{BASE}/event/{event_id}/attenders",
                        params={"requester_id": requester_id}).json()


@mcp.tool()
def show_reserve_history_event(admin_id: str, event_id: str) -> dict:
    """ดูรายชื่อผู้เข้าร่วม event ผ่าน admin (ใช้ /show/event)

    Args:
        admin_id: รหัส admin เช่น ADM-001
        event_id: รหัส event เช่น EV-001

    ตัวอย่าง: "Tom ขอดูรายชื่อคนใน EV-001"
    """
    return requests.get(f"{BASE}/show/event",
                        params={"admin_id": admin_id, "event_id": event_id}).json()


if __name__ == "__main__":
    mcp.run()