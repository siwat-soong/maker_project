from pydantic import BaseModel, Field
from fastmcp import FastMCP
from typing import Optional
from controller import system_init
from datetime import datetime
from api import *

sys = system_init()

mcp = FastMCP("MakerLab")

@mcp.tool()
def mcp_check_system_status() -> dict:
    """
    ตรวจสอบสถานะของระบบ (Root)

    เงื่อนไขการใช้งาน: ใช้เมื่อต้องการเช็คว่าระบบยังทำงานปกติหรือไม่
    รูปแบบ Input: ไม่มี
    รูปแบบการตอบกลับ: {"status": "OK"}
    """
    return root()

# ==========================================
# EVENT TOOLS
# ==========================================

@mcp.tool()
def mcp_show_event_info(event_id: str) -> dict:
    """
    ดูรายละเอียดของกิจกรรม (Event) จาก ID

    เงื่อนไขการใช้งาน: ไม่มีข้อจำกัด
    รูปแบบ Input: 
    - event_id (str): รหัสของกิจกรรมที่ต้องการค้นหา
    รูปแบบการตอบกลับ: 
    - สำเร็จ: ตารางกิจกรรมที่ตรงตามที่ส่งเข้ามา ใช้ emoji เพิ่มเพื่อให้สวยงามขึ้น
    - ผิดพลาด: {"ERROR": "ไม่พบกิจกรรมนี้"}
    """
    return show_event_info(event_id)

@mcp.tool()
def mcp_show_all_event() -> dict:
    """
    ดูรายการกิจกรรมทั้งหมดในระบบ

    เงื่อนไขการใช้งาน: ไม่มีข้อจำกัด
    รูปแบบ Input: ไม่มี
    รูปแบบการตอบกลับ: 
    - สำเร็จ: ตารางกิจกรรมทั้งหมดที่มี ใช้ emoji เพิ่มเพื่อให้สวยงามขึ้น
    - ผิดพลาด: ไม่พบกิจกรรมใด
    """
    return show_all_event()

@mcp.tool()
def mcp_show_available_event() -> dict:
    """
    ดูรายการกิจกรรมที่ยังเปิดรับสมัครหรือยังไม่จบ (SCHEDULED / OPEN)

    เงื่อนไขการใช้งาน: ไม่มีข้อจำกัด
    รูปแบบ Input: ไม่มี
    รูปแบบการตอบกลับ: 
    - สำเร็จ: ตารางกิจกรรมทั้งหมดที่สามารถเข้าร่วมได้ ใช้ emoji เพิ่มเพื่อให้สวยงามขึ้น
    - ผิดพลาด: ไม่พบกิจกรรมใด
    """
    return show_available_event()

# ==========================================
# RESOURCE TOOLS
# ==========================================

@mcp.tool()
def mcp_show_resource_info(res_id: str) -> dict:
    """
    ดูรายละเอียดของทรัพยากร (พื้นที่, อุปกรณ์, หรือวัสดุ) จาก ID

    เงื่อนไขการใช้งาน: ค้นหาครอบคลุมทั้ง Space, Equipment และ Material
    รูปแบบ Input:
    - res_id (str): รหัสของทรัพยากร
    รูปแบบการตอบกลับ: 
    - สำเร็จ: ตารางทรัพยากรทั้งหมดที่ตรงกัน ใช้ emoji เพิ่มเพื่อให้สวยงามขึ้น
    - ผิดพลาด: ไม่พบทรัพยากรใด
    """
    return show_resource_info(res_id)

@mcp.tool()
def mcp_show_all_resource() -> list:
    """
    ดึงข้อมูลทรัพยากรทั้งหมดในระบบ แยกตามประเภท (SPACE, EQUIPMENT, MATERIAL)

    รูปแบบการตอบกลับ: 
    - สำเร็จ: ตารางทั้งหมดทั้งหมดที่มี ใช้ emoji เพิ่มเพื่อให้สวยงามขึ้น
    - ผิดพลาด: ไม่พบทรัพยากรใด
    """
    return show_all_resource()

@mcp.tool()
def mcp_show_available_resource(start_time: str, end_time: str) -> list:
    """
    ค้นหาทรัพยากรที่ว่างและพร้อมใช้งานในช่วงเวลาที่กำหนด

    เงื่อนไขการใช้งาน: 
    - ห้ามค้นหาเวลาในอดีต และเวลาเริ่มต้นต้องเกิดก่อนเวลาสิ้นสุด
    รูปแบบ Input:
    - start_time (str): เวลาเริ่มต้น Format "DD-MM-YYYY HH:MM" (เช่น "15-03-2026 10:00")
    - end_time (str): เวลาสิ้นสุด Format "DD-MM-YYYY HH:MM"
    รูปแบบการตอบกลับ: List ของทรัพยากรที่ว่างแยกตามประเภท หรือ {"ERROR": "..."}
    """
    return show_available_resource(start_time, end_time)

# ==========================================
# USER INFO TOOLS
# ==========================================

@mcp.tool()
def mcp_show_user_info(uid: str) -> dict:
    """ดูรายละเอียดข้อมูลพื้นฐานของ User"""
    return show_user_info(uid)

@mcp.tool()
def mcp_show_user_expired_date(uid: str) -> dict:
    """ดูวันหมดอายุสมาชิกของ User"""
    return show_user_expired_date(uid)

@mcp.tool()
def mcp_show_user_max_rsv(uid: str) -> dict:
    """ดูสิทธิการจองล่วงหน้าสูงสุด (จำนวนวัน) ของ User"""
    return show_user_max_rsv(uid)

@mcp.tool()
def mcp_show_user_blacklist(uid: str) -> dict:
    """ตรวจสอบสถานะว่า User ติด Blacklist หรือไม่"""
    return show_user_blacklist(uid)

@mcp.tool()
def mcp_show_user_invoice(uid: str) -> dict:
    """ดูใบแจ้งหนี้ (ค้างชำระ) ปัจจุบันของ User"""
    return show_user_invoice(uid)

@mcp.tool()
def mcp_show_user_notification(uid: str) -> dict:
    """ดูการแจ้งเตือนทั้งหมดของ User"""
    return show_user_notification(uid)

@mcp.tool()
def mcp_show_user_receipt(uid: str) -> dict:
    """ดูประวัติใบเสร็จรับเงินทั้งหมดของ User"""
    return show_user_receipt(uid)

@mcp.tool()
def mcp_show_user_cart(uid: str) -> dict:
    """ดูรายการทรัพยากรที่อยู่ในตะกร้า (Cart) ของ User"""
    return show_user_cart(uid)

@mcp.tool()
def mcp_show_user_reservation(uid: str) -> dict:
    """ดูรายการใบจอง (Reservation) ปัจจุบันของ User"""
    return show_user_reservation(uid)

# ==========================================
# USER ACTION TOOLS
# ==========================================

@mcp.tool()
def mcp_register_user(uid: str, name: str, tel: str) -> dict:
    """
    ลงทะเบียนผู้ใช้งานใหม่

    เงื่อนไขการใช้งาน: UID ต้องยังไม่เคยลงทะเบียนมาก่อน
    รูปแบบ Input:
    - uid (str): รหัสผู้ใช้
    - name (str): ชื่อผู้ใช้
    - tel (str): เบอร์โทรศัพท์
    รูปแบบการตอบกลับ: {"STATUS": "SUCCESS"} หรือ {"ERROR": "..."}
    """
    return register(uid, name, tel)

@mcp.tool()
def mcp_subscribe_user(uid: str) -> dict:
    """
    สมัครสมาชิกเพื่อรับสิทธิพิเศษ

    เงื่อนไขการใช้งาน: User ต้องไม่มีใบแจ้งหนี้ค้างชำระ และต้องไม่ติด Blacklist
    รูปแบบ Input: uid (str)
    รูปแบบการตอบกลับ: {"STATUS": "SUCCESS"} หรือ {"ERROR": "..."}
    """
    return subscribe(uid)

@mcp.tool()
def mcp_add_to_cart(uid: str, resource_id: str, amount: float = 1, start_time: str = None, end_time: str = None, event: bool = False) -> dict:
    """
    เพิ่มทรัพยากรลงในตะกร้าของ User (สำหรับการจองหรือการซื้อ)

    เงื่อนไขการใช้งาน:
    - User ต้องไม่มีใบแจ้งหนี้ค้างชำระและไม่ติด Blacklist (ยกเว้นเข้าทาง Event)
    - วันที่จองต้องไม่เป็นอดีต และไม่เกินโควต้าวันล่วงหน้าสูงสุดของ User
    - ทรัพยากรต้องผ่านการ Validate ความพร้อมใช้งาน
    รูปแบบ Input:
    - uid (str): รหัสผู้ใช้
    - resource_id (str): รหัสทรัพยากร
    - amount (float): จำนวน (ค่าเริ่มต้น 1)
    - start_time (str): เวลาเริ่มต้น Format "DD-MM-YYYY HH:MM" (บังคับถ้าเป็นประเภทต้องจองเวลา)
    - end_time (str): เวลาสิ้นสุด Format "DD-MM-YYYY HH:MM"
    - event (bool): ถ้าทำรายการผ่านกิจกรรมให้ส่ง True (ค่าเริ่มต้น False)
    รูปแบบการตอบกลับ: {"STATUS": "SUCCESS"} หรือ {"ERROR": "..."}
    """
    return add_to_cart(uid, resource_id, amount, start_time, end_time, event)

@mcp.tool()
def mcp_remove_from_cart(uid: str, resource_id: str, start_time: str = None) -> dict:
    """
    ลบรายการทรัพยากรออกจากตะกร้า

    เงื่อนไขการใช้งาน: ต้องมีไอเทมนั้นในตะกร้า
    รูปแบบ Input:
    - uid (str), resource_id (str)
    - start_time (str): Format "DD-MM-YYYY HH:MM" (Optional ใช้ระบุตัวเจาะจงถ้ามีการจองเวลา)
    รูปแบบการตอบกลับ: {"STATUS": "SUCCESS"} หรือ {"ERROR": "..."}
    """
    return remove_from_cart(uid, resource_id, start_time)

@mcp.tool()
def mcp_reserve(uid: str) -> dict:
    """
    ยืนยันการจองทรัพยากรทั้งหมดที่อยู่ในตะกร้า (เปลี่ยนสถานะจาก Cart เป็น Reservation)

    เงื่อนไขการใช้งาน:
    - User ต้องไม่มีหนี้ค้างและไม่ติด Blacklist
    - ไอเทมในตะกร้าต้องพร้อมให้บริการ ณ เวลากดจอง
    รูปแบบ Input: uid (str)
    รูปแบบการตอบกลับ: {"STATUS": "SUCCESS"} หรือ {"ERROR": "..."}
    """
    return reserve(uid)

@mcp.tool()
def mcp_cancel_reserve(uid: str, rsv_id: str, res_id: str = None, start_time: str = None) -> dict:
    """
    ยกเลิกการจองทรัพยากร

    เงื่อนไขการใช้งาน: User ไม่มีหนี้ค้าง/Blacklist และอาจเกิดค่าปรับ (FINE) หากผิดเงื่อนไขเวลา
    รูปแบบ Input:
    - uid (str), rsv_id (str): รหัสใบจอง
    - res_id (str): รหัสทรัพยากร (Optional)
    - start_time (str): Format "DD-MM-YYYY HH:MM" (Optional)
    รูปแบบการตอบกลับ: {"STATUS": "SUCCESS", "FINE": "$..."} (หากมีค่าปรับ) หรือ {"ERROR": "..."}
    """
    return cancel_reserve(uid, rsv_id, res_id, start_time)

@mcp.tool()
def mcp_buy_items(uid: str) -> dict:
    """
    ชำระเงินซื้อทรัพยากรประเภทซื้อขาด (INSTANT_PAY) ที่อยู่ในตะกร้า

    เงื่อนไขการใช้งาน: User ต้องไม่มีหนี้ค้าง/Blacklist จะสร้าง Invoice อัตโนมัติ
    รูปแบบ Input: uid (str)
    รูปแบบการตอบกลับ: {"STATUS": "SUCCESS", "TOTAL": ยอดเงิน} หรือ {"ERROR": "..."}
    """
    return buy(uid)

@mcp.tool()
def mcp_check_in(uid: str, rsv_id: str, res_id: str, start_time: str, check_in_time: str = None) -> dict:
    """
    เช็คอินเพื่อเข้าใช้งานทรัพยากรที่จองไว้

    เงื่อนไขการใช้งาน:
    - เช็คอินก่อนเวลาได้ไม่เกิน 15 นาที
    - หากเช็คอินสายเกิน 15 นาที จะถูกยกเลิกการจองและเสียค่าปรับนาทีละ $10
    รูปแบบ Input:
    - uid (str), rsv_id (str), res_id (str)
    - start_time (str): Format "DD-MM-YYYY HH:MM"
    - check_in_time (str): ระบุเวลาเช็คอิน (Optional, ไม่ระบุคือเวลาปัจจุบัน)
    รูปแบบการตอบกลับ: {"STATUS": "SUCCESS"} หรือ {"ERROR": "..."}
    """
    return check_in(uid, rsv_id, res_id, start_time, check_in_time)

@mcp.tool()
def mcp_check_out(uid: str, rsv_id: str, res_id: str, check_out_time: str = None) -> dict:
    """
    เช็คเอาท์ออกจากการใช้งานทรัพยากร

    เงื่อนไขการใช้งาน: ระบบจะคำนวณค่าธรรมเนียมหรือค่าปรับส่วนเกินและออกเป็น Invoice
    รูปแบบ Input: uid, rsv_id, res_id, check_out_time (Format "DD-MM-YYYY HH:MM", Optional)
    รูปแบบการตอบกลับ: {"STATUS": "SUCCESS", "TOTAL_FEE": "$..."}
    """
    return check_out(uid, rsv_id, res_id, check_out_time)

@mcp.tool()
def mcp_join_event(uid: str, event_id: str) -> dict:
    """
    ลงทะเบียนเข้าร่วมกิจกรรม

    เงื่อนไขการใช้งาน: User ไม่มีหนี้ค้าง/Blacklist ระบบจะคำนวณส่วนลดและสร้าง Invoice ค่าเข้า
    รูปแบบ Input: uid (str), event_id (str)
    รูปแบบการตอบกลับ: {"STATUS": "SUCCESS", "TOTAL_FEE": "$..."}
    """
    return join(uid, event_id)

@mcp.tool()
def mcp_unjoin_event(uid: str, event_id: str, time: str) -> dict:
    """
    ยกเลิกการเข้าร่วมกิจกรรม

    เงื่อนไขการใช้งาน: ระบบจะพิจารณาเวลาที่ขอยกเลิกเพื่อคืนเงิน (Refund)
    รูปแบบ Input: 
    - uid, event_id
    - time (str): เวลาที่กดยกเลิก Format "DD-MM-YYYY HH:MM"
    รูปแบบการตอบกลับ: {"STATUS": "SUCCESS", "REFUND": "$..."}
    """
    return unjoin(uid, event_id, time)

@mcp.tool()
def mcp_pay_invoice(uid: str, cost: float, method: str) -> dict:
    """
    ชำระเงินใบแจ้งหนี้ (Invoice)

    เงื่อนไขการใช้งาน: 
    - ต้องมีใบแจ้งหนี้คงค้างในระบบ และจำนวนเงิน (cost) ต้องมากกว่าหรือเท่ากับยอดรวม
    - Method ต้องเป็นระบบที่รองรับ (เช่น "QRCODE", "CASH")
    รูปแบบ Input:
    - uid (str)
    - cost (float): จำนวนเงินที่จ่าย
    - method (str): วิธีการชำระเงิน
    รูปแบบการตอบกลับ: {"STATUS": "SUCCESS", "CHANGE": "$เงินทอน"}
    """
    return pay(uid, cost, method)

# ==========================================
# RESOURCE MANAGEMENT (USER/ADMIN)
# ==========================================

@mcp.tool()
def mcp_use_equipment(eq_id: str, amount: float = None) -> dict:
    """ลดจำนวนการใช้งานอุปกรณ์ (Use)"""
    return use(eq_id, amount)

@mcp.tool()
def mcp_add_own_material(eq_id: str) -> dict:
    """อนุญาตให้ใช้วัสดุส่วนตัวเพิ่มเข้าไปในอุปกรณ์ (ถ้าอุปกรณ์นั้นรองรับ)"""
    return add_own(eq_id)

@mcp.tool()
def mcp_report_breakdown(eq_id: str) -> dict:
    """แจ้งอุปกรณ์ชำรุด (เปลี่ยนสถานะเป็น MAINTENANCE)"""
    return breakdown(eq_id)

# ==========================================
# ADMIN TOOLS
# ==========================================

@mcp.tool()
def mcp_admin_repair_equipment(admin_id: str, eq_id: str) -> dict:
    """
    (สำหรับ Admin) อนุมัติการซ่อมแซมอุปกรณ์

    เงื่อนไขการใช้งาน: Admin เป็นผู้ทำรายการ และสถานะอุปกรณ์ต้องเป็น MAINTENANCE
    รูปแบบ Input: admin_id (str), eq_id (str)
    รูปแบบการตอบกลับ: {"STATUS": "SUCCESS"} หรือ {"ERROR": "..."}
    """
    return repair(admin_id, eq_id)

@mcp.tool()
def mcp_admin_restock_material(uid: str, mat_id: str, amount: float) -> dict:
    """(สำหรับ Admin) เติมสต๊อกวัสดุ"""
    return restock(uid, mat_id, amount)

@mcp.tool()
def mcp_admin_blacklist_user(admin_id: str, uid: str) -> dict:
    """(สำหรับ Admin) สั่งระงับการใช้งาน User (Blacklist)"""
    return blacklist(admin_id, uid)

@mcp.tool()
def mcp_admin_unblacklist_user(admin_id: str, uid: str) -> dict:
    """(สำหรับ Admin) ปลดล็อคระงับการใช้งาน User (Unblacklist)"""
    return unblacklist(admin_id, uid)

@mcp.tool()
def mcp_admin_create_event(uid: str, topic: str, detail: str, start_time: str, end_time: str, ins_id: str, space_id: str, max_attender: float, join_fee: float) -> dict:
    """
    (สำหรับ Admin) สร้างกิจกรรมใหม่ในระบบ

    เงื่อนไขการใช้งาน:
    - เวลาต้องถูกต้องและไม่ซ้อนทับตารางของวิทยากร (Instructor)
    - จำนวนคนต้องไม่เกินความจุของพื้นที่จัดงาน (Space Capacity)
    รูปแบบ Input:
    - uid (str): Admin ID
    - topic (str), detail (str)
    - start_time, end_time (str): Format "DD-MM-YYYY HH:MM"
    - ins_id (str): ID วิทยากร
    - space_id (str): ID สถานที่
    - max_attender (float): จำนวนคนสูงสุด
    - join_fee (float): ค่าเข้าร่วม
    รูปแบบการตอบกลับ: {"STATUS": "SUCCESS"} หรือ {"ERROR": "..."}
    """
    return create_event(uid, topic, detail, start_time, end_time, ins_id, space_id, max_attender, join_fee)

@mcp.tool()
def mcp_admin_open_event(uid: str, event_id: str) -> dict:
    """(สำหรับ Admin) เปิดรับสมัครกิจกรรม"""
    # หมายเหตุ: ในโค้ดเดิม def ใช้ชื่อ unjoin แต่รับ endpoint /event/open (เรียก event.open_event())
    # ผมสร้าง wrapper ข้ามไปหา endpoint ให้ตรงตาม logic ต้นฉบับครับ
    return app.routes[[r.path for r in app.routes].index('/event/open')].endpoint(uid, event_id)

@mcp.tool()
def mcp_admin_close_event(uid: str, event_id: str, end_time: str) -> dict:
    """
    (สำหรับ Admin) ปิดกิจกรรม

    เงื่อนไขการใช้งาน: คืนตารางเวลาและคืนทรัพยากร ระบบจะพิจารณาว่าต้อง Refund หรือไม่ถ้าปิดก่อนกำหนด
    รูปแบบ Input: uid, event_id, end_time (Format "DD-MM-YYYY HH:MM")
    รูปแบบการตอบกลับ: {"STATUS": "SUCCESS", "REFUND": bool} หรือ {"ERROR": "..."}
    """
    return close_event(uid, event_id, end_time)

# ==========================================
# INSTRUCTOR TOOLS
# ==========================================

@mcp.tool()
def mcp_instructor_add_resource_to_event(uid: str, event_id: str) -> dict:
    """
    (สำหรับ วิทยากร) นำทรัพยากรที่อยู่ในตะกร้าของวิทยากรเพิ่มเข้าไปใช้ในกิจกรรม

    เงื่อนไขการใช้งาน: ผู้เรียกต้องเป็น Instructor ของงานนั้น และต้องมีทรัพยากรในตะกร้า
    รูปแบบ Input: uid (str ของวิทยากร), event_id (str)
    รูปแบบการตอบกลับ: {"STATUS": "SUCCESS"} หรือ {"ERROR": "..."}
    """
    return add_resource_to_event(uid, event_id)

@mcp.tool()
def mcp_instructor_grade_event(ins_id: str, event_id: str, uid: str, score: float) -> dict:
    """
    (สำหรับ วิทยากร) ให้คะแนนผู้เข้าร่วมและมอบเกียรติบัตร (Certificate)

    เงื่อนไขการใช้งาน: User ต้องเข้าร่วมกิจกรรมนั้นจริง
    รูปแบบ Input:
    - ins_id (str): รหัสวิทยากร
    - event_id (str): รหัสกิจกรรม
    - uid (str): รหัสผู้เข้าร่วม
    - score (float): คะแนนที่ได้ (ใช้ตัดเกรด A >75, B >50, C >25, D >0)
    รูปแบบการตอบกลับ: {"STATUS": "SUCCESS"} หรือ {"ERROR": "..."}
    """
    return grade_event(ins_id, event_id, uid, score)

@mcp.tool()
def mcp_show_all_instructor() -> list | dict:
    """
    ดูรายการข้อมูลวิทยากร (Instructor) ทั้งหมดในระบบ

    เงื่อนไขการใช้งาน: ไม่มีข้อจำกัด
    รูปแบบ Input: ไม่มี
    รูปแบบการตอบกลับ: 
    - สำเร็จ: List ที่เก็บข้อมูลรายละเอียดของวิทยากรแต่ละท่าน
    - ผิดพลาด: {"ERROR": "ข้อความแจ้งเตือนความผิดพลาด"}
    """
    return show_all_instructor()

@mcp.tool()
def mcp_show_available_instructor(start_time: str, end_time: str) -> list | dict:
    """
    ดูรายการวิทยากร (Instructor) ที่มีคิวว่างและพร้อมบรรยายในช่วงเวลาที่กำหนด

    เงื่อนไขการใช้งาน:
    - ห้ามค้นหาเวลาในอดีต
    - เวลาเริ่มต้นต้องเกิดก่อนเวลาสิ้นสุด และห้ามเป็นเวลาเดียวกัน
    รูปแบบ Input:
    - start_time (str): เวลาเริ่มต้น Format "DD-MM-YYYY HH:MM" (เช่น "15-03-2026 10:00")
    - end_time (str): เวลาสิ้นสุด Format "DD-MM-YYYY HH:MM"
    รูปแบบการตอบกลับ: 
    - สำเร็จ: List ที่เก็บข้อมูลรายละเอียดของวิทยากรที่ตารางว่างพร้อมรับงาน
    - ผิดพลาด: {"ERROR": "ข้อความแจ้งเตือนความผิดพลาด"}
    """
    return show_available_instructor(start_time, end_time)

if __name__ == "__main__":
    mcp.run()