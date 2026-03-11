from fastmcp import FastMCP
import requests

mcp = FastMCP("maker_club_mcp")

BASE = "http://127.0.0.1:8000"

@mcp.tool()
def show_user_info(user_id: str) -> dict:
    """
    ดึงข้อมูลพื้นฐานของผู้ใช้หรือผู้สอน

    ฟังก์ชันนี้เรียกใช้งาน endpoint `/user_info` ของเซิร์ฟเวอร์
    API ภายในเครื่อง

    Parameters
    ----------
    user_id : str
        รหัสเฉพาะของผู้ใช้หรือผู้สอนที่ต้องการข้อมูล

    Returns
    -------
    dict
        ผลลัพธ์ JSON ที่แปลงแล้วจากเซิร์ฟเวอร์ ในกรณีสำเร็จจะมี
        ฟิลด์เช่น ``UID`` ``NAME`` ``TEL`` ``ROLE`` และสถานะการ
        สมัครสมาชิก หากไม่พบผู้ใช้ ผลลัพธ์อาจเป็นคำอธิบายข้อผิดพลาด

    Notes
    -----
    - ฟังก์ชันนี้ประดับด้วย ``@mcp.tool`` เพื่อให้ agent MCP
      (เช่น Claude) เรียกใช้งานผ่านโปรโตคอล ``maker_club_mcp``
    - เซิร์ฟเวอร์ API ต้องสามารถเข้าถึงได้ที่ตัวแปร ``BASE``
      (`http://127.0.0.1:8000`)
    """
    return requests.get(f"{BASE}/user_info", params={"user_id": user_id}).json()


@mcp.tool()
def subscribe(user_id: str) -> dict:
    """
    ส่งคำขอสมัครสมาชิกสำหรับผู้ใช้ประเภท Guest

    Parameters
    ----------
    user_id : str
        รหัสของผู้ใช้ Guest ที่ต้องการสมัครสมาชิก เมื่อสำเร็จ
        ผู้ใช้จะกลายเป็นสมาชิกและมีวันหมดอายุหนึ่งปีนับจากนี้

    Returns
    -------
    dict
        ผลลัพธ์ JSON จาก endpoint `/subscribe`.  ในกรณีสำเร็จจะ
        มีข้อความยืนยัน ในกรณีล้มเหลวอาจมีคำอธิบายสาเหตุ (เช่น
        เป็นสมาชิกอยู่แล้ว, มีบิลค้างชำระ, ถูกแบน)
    """
    return requests.post(f"{BASE}/subscribe", params={"user_id": user_id}).json()

@mcp.tool()
def pay(user_id: str, inv_id: str, cost: float, method_id: str) -> dict:
    """
    ดำเนินการชำระเงินสำหรับใบแจ้งหนี้ที่ระบุด้วยวิธีที่เลือก

    ฟังก์ชันนี้ห่อหุ้มการเรียก API `/pay`

    Parameters
    ----------
    user_id : str
        รหัสผู้ใช้ที่ทำการชำระเงิน
    inv_id : str
        รหัสใบแจ้งหนี้ที่จะชำระ
    cost : float
        จำนวนเงินที่ผู้ใช้จ่ายเข้ามา โดยบางวิธีการอาจต้องการเงิน
        พอดีหรือคืนเงินทอน
    method_id : str
        รหัสวิธีการชำระเงิน (เช่น เงินสด "C-0001", QR code
        "Q-0001")

    Returns
    -------
    dict
        ผลลัพธ์ JSON ที่แปลงแล้วจากเซิร์ฟเวอร์ ในกรณีสำเร็จจะมี
        ข้อมูลใบเสร็จ การคืนเงินทอน หรือข้อความข้อผิดพลาดหาก
        ชำระเงินล้มเหลวหรือการตรวจสอบไม่ผ่าน
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
    เพิ่มคำขอสำรองทรัพยากรลงในตะกร้าสินค้าของผู้ใช้

    วันที่ถูกส่งเป็นสตริงในรูปแบบ ``"%d/%m/%Y,%H:%M"``
    (วัน/เดือน/ปี,ชั่วโมง:นาที). ด้านหลังจะตรวจสอบการทับซ้อน,
    ความพร้อมใช้งาน, ความเชี่ยวชาญ และกฎทางธุรกิจอื่นก่อน
    ที่ผู้ใช้จะทำการชำระเงิน

    Parameters
    ----------
    user_id : str
        รหัสผู้ใช้ที่ทำการเพิ่มในตะกร้า
    item_id : str
        รหัสทรัพยากรที่ต้องการสำรอง (พื้นที่, อุปกรณ์, หรือ
        วัสดุ)
    start_time : str
        วันเริ่มต้นการจอง ตามรูปแบบที่ระบุ
    end_time : str
        วันสิ้นสุดการจอง ตามรูปแบบที่ระบุ
    amount : float, optional
        จำนวนหน่วยของทรัพยากรที่ต้องการสำรอง (ค่าเริ่มต้น 1)

    Returns
    -------
    dict
        ผลลัพธ์ JSON จาก endpoint `/add_to_cart` ซึ่งบ่งชี้ถึงความ
        สำเร็จหรือรายละเอียดข้อผิดพลาด (เช่น ขัดแย้งตารางเวลา,
        ไม่มีสิทธิ์เพียงพอ)
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
    สรุปรายการทั้งหมดที่อยู่ในตะกร้าของผู้ใช้และสร้างการ
    จองทรัพยากร

    เซิร์ฟเวอร์จะคำนวณค่าใช้จ่ายทั้งหมด, สร้างใบแจ้งหนี้สำหรับ
    วัสดุหรือบริการ และล้างตะกร้าหลังจากสำเร็จ หากมีใบแจ้งหนี้
    ค้างชำระหรือปัญหาการถูกแบน การจองจะถูกปฏิเสธ

    Parameters
    ----------
    user_id : str
        รหัสผู้ใช้ที่กำลังชำระเงิน

    Returns
    -------
    dict
        ผลลัพธ์ API ที่บ่งชี้สถานะการจอง ข้อความที่ส่งกลับจะ
        ระบุรหัสการจองใหม่และค่าใช้จ่ายวัสดุที่เกิดขึ้น
    """
    return requests.post(f"{BASE}/reserve", params={"user_id": user_id}).json()

@mcp.tool()
def cancel_reserve(user_id: str, rsv_id: str) -> dict:
    """
    ยกเลิกการจองที่มีอยู่ในนามของผู้ใช้

    Parameters
    ----------
    user_id : str
        รหัสของผู้ใช้ที่ขอยกเลิก
    rsv_id : str
        รหัสการจอง (เช่น ``REQ-0001``)

    Returns
    -------
    dict
        ผลลัพธ์ JSON จากเซิร์ฟเวอร์ ในกรณีสำเร็จจะระบุค่าธรรมเนียม
        ยกเลิก (เช่น 50$ หากภายใน 4 ชั่วโมงก่อนเริ่ม) หรือยืนยันว่าการ
        จองถูกยกเลิกแล้ว
    """
    return requests.post(f"{BASE}/cancel_reserve", params={
        "user_id": user_id,
        "rsv_id": rsv_id
    }).json()

@mcp.tool()
def check_in(user_id: str, rsv_id: str, space_id: str, start_time: str) -> dict:
    """
    บันทึกการเริ่มต้นช่วงเวลาจองสำหรับผู้ใช้

    endpoint นี้ใช้เมื่อผู้ใช้มาถึงเพื่อใช้พื้นที่ที่จองไว้จริง

    Parameters
    ----------
    user_id : str
        รหัสผู้ใช้ที่เช็คอิน
    rsv_id : str
        รหัสการจองที่เกี่ยวข้องกับพื้นที่
    space_id : str
        รหัสทรัพยากรพื้นที่ที่กำลังใช้งาน
    start_time : str
        เวลาจริงที่เริ่มใช้งาน (``"%d/%m/%Y,%H:%M"``)

    Returns
    -------
    dict
        ผลลัพธ์ JSON จากเซิร์ฟเวอร์ โดยปกติจะยืนยันการเช็คอินหรือ
        ให้ข้อผิดพลาดหากไม่พบการจองหรืไม่ถูกต้อง
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
    บันทึกการสิ้นสุดการใช้งานพื้นที่ที่จองไว้และสรุปค่าธรรมเนียม

    Parameters
    ----------
    user_id : str
        รหัสผู้ใช้ที่เช็คเอาท์
    rsv_id : str
        รหัสการจอง
    space_id : str
        รหัสพื้นที่ที่กำลังย้ายออก
    start_time : str
        เวลาที่เริ่มกระบวนการเช็คเอาท์ (รูปแบบเดียวกับเช็คอิน)

    Returns
    -------
    dict
        วัตถุ JSON ที่ส่งกลับจาก API `/checkout` อาจมีข้อมูลใบ
        แจ้งหนี้ที่ปรับปรุงหรือยืนยันการเสร็จสิ้น
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
    จัดการการคืนอุปกรณ์ที่เป็นส่วนหนึ่งของการจอง

    Parameters
    ----------
    user_id : str
        ผู้ใช้ที่ทำการคืนอุปกรณ์
    rsv_id : str
        รหัสการจองที่เกี่ยวข้อง
    equipment_id : str
        รหัสทรัพยากรของอุปกรณ์ที่คืน
    start_time : str
        เวลาเมื่ออุปกรณ์ถูกคืน

    Returns
    -------
    dict
        ตอบกลับจากเซิร์ฟเวอร์ที่ระบุความสำเร็จหรือรายละเอียดของ
        ค่าปรับหรือปัญหาในการประมวลผลการคืน
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
    สร้างเวิร์กช็อป/กิจกรรมใหม่ในระบบ maker club

    การดำเนินการนี้ต้องทำโดยผู้ดูแลระบบ เหตุการณ์จะเกี่ยวข้อง
    กับผู้สอนและจัดขึ้นในพื้นที่ที่กำหนด

    Parameters
    ----------
    admin_id : str
        รหัสผู้ดูแลระบบที่สร้างกิจกรรม
    topic : str
        หัวข้อหรือชื่อกิจกรรม
    detail : str
        คำอธิบายหรือข้อมูลเพิ่มเติมเกี่ยวกับกิจกรรม
    start_time : str
        เวลาที่วางแผนจะเริ่ม (``"%d/%m/%Y,%H:%M"``)
    end_time : str
        เวลาที่วางแผนจะสิ้นสุด (รูปแบบเดียวกัน)
    instructor_id : str
        รหัสผู้สอนที่จะเป็นผู้นำกิจกรรม
    space_id : str
        ทรัพยากรพื้นที่ที่จะจัดกิจกรรม
    max_attender : int
        จำนวนผู้เข้าร่วมสูงสุดที่อนุญาต
    join_fee : float
        ค่าธรรมเนียมที่เรียกเก็บจากผู้เข้าร่วมเมื่อเข้าร่วม

    Returns
    -------
    dict
        ผลลัพธ์ JSON จาก `/event/create` ในกรณีสำเร็จมักจะมีรหัส
        กิจกรรมใหม่และข้อความยืนยัน ข้อผิดพลาดอาจเกิดขึ้นหาก
        ตารางเวลาชนกันหรือผู้สอน/พื้นที่ไม่ว่าง
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
    ลงทะเบียนผู้ใช้เป็นผู้เข้าร่วมกิจกรรมที่กำหนด

    ฝั่งหลังบ้านจะตรวจสอบว่ากิจกรรมเปิดรับและยังไม่เต็มก่อน
    เพิ่มผู้ใช้

    Parameters
    ----------
    user_id : str
        รหัสของผู้ใช้ที่ต้องการเข้าร่วม
    event_id : str
        รหัสเอกลักษณ์ของกิจกรรม (เช่น ``WS-0001``)

    Returns
    -------
    dict
        ข้อความ JSON ที่ประกอบด้วยการยืนยันความสำเร็จหรือ
        คำอธิบายข้อผิดพลาด (เช่น กิจกรรมเต็ม, เข้าร่วมแล้ว,
        เงินไม่พอ)
    """
    return requests.post(f"{BASE}/event/join", params={
        "user_id": user_id,
        "event_id": event_id
    }).json()

@mcp.tool()
def cancel_join_event(user_id: str, event_id: str) -> dict:
    """
    นำผู้ใช้ออกจากกิจกรรมที่เคยเข้าร่วมไว้ก่อนหน้านี้

    Parameters
    ----------
    user_id : str
        รหัสของผู้ใช้ที่ยกเลิกการเข้าร่วม
    event_id : str
        รหัสกิจกรรม

    Returns
    -------
    dict
        ผลลัพธ์ JSON ที่แสดงว่าการยกเลิกสำเร็จหรือมีข้อผิดพลาด
        (เช่น ไม่พบผู้ใช้ในรายการผู้เข้าร่วม)
    """
    return requests.post(f"{BASE}/event/cancel_join", params={
        "user_id": user_id,
        "event_id": event_id
    }).json()

@mcp.tool()
def cancel_event(instructor_id: str, event_id: str) -> dict:
    """
    อนุญาตให้ผู้สอนยกเลิกกิจกรรมที่ตนเองกำหนดไว้

    Parameters
    ----------
    instructor_id : str
        รหัสผู้สอนที่ทำการยกเลิก
    event_id : str
        รหัสกิจกรรมที่จะยกเลิก

    Returns
    -------
    dict
        ตอบกลับจากเซิร์ฟเวอร์ที่อาจมีรายละเอียดเกี่ยวกับการ
        คืนเงินหรือการแจ้งเตือนส่งไปยังผู้เข้าร่วม
    """
    return requests.post(f"{BASE}/event/cancel_event", params={
        "instructor_id": instructor_id,
        "event_id": event_id
    }).json()

@mcp.tool()
def add_equipment_to_event(user_id: str, event_id: str) -> dict:
    """
    แนบอุปกรณ์ที่มีอยู่ในตะกร้าของผู้ใช้เข้ากับการจองกิจกรรม
    เฉพาะรายการหนึ่ง

    นี่เป็นการ PUT เพื่อย้ายทรัพยากรจากตะกร้าไปยังรายการของ
    กิจกรรม ซึ่งอาจส่งผลต่อค่าธรรมเนียมหรือความพร้อมใช้งาน

    Parameters
    ----------
    user_id : str
        ผู้ใช้ที่ขอเพิ่มอุปกรณ์
    event_id : str
        รหัสกิจกรรมเป้าหมาย

    Returns
    -------
    dict
        ข้อความ JSON อธิบายความสำเร็จหรือความล้มเหลว รวมถึง
        การปรับค่าใช้จ่ายใดๆ
    """
    return requests.put(f"{BASE}/event/add", params={
        "user_id": user_id,
        "event_id": event_id
    }).json()

@mcp.tool()
def add_certificate(instructor_id: str, event_id: str, user_id: str, score: float) -> dict:
    """
    ออกใบประกาศนียบัตรให้ผู้ใช้หลังจบกิจกรรม

    การกระทำนี้ทำได้เฉพาะผู้สอนที่เกี่ยวข้องกับกิจกรรมนั้น
เท่านั้น

    Parameters
    ----------
    instructor_id : str
        รหัสผู้สอนที่ให้ใบประกาศนียบัตร
    event_id : str
        รหัสกิจกรรม
    user_id : str
        ผู้ใช้ที่ได้รับใบประกาศนียบัตร
    score : float
        คะแนนตัวเลขหรือเกรดที่ให้; เก็บไว้สำหรับการตรวจสอบ
        ความเชี่ยวชาญในอนาคต

    Returns
    -------
    dict
        ตอบกลับจาก `/event/certificate` ที่บ่งชี้ความสำเร็จหรือ
        ข้อผิดพลาดในการตรวจสอบ
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
    ดึงรายชื่อผู้ใช้ที่เข้าร่วมกิจกรรมหนึ่ง

    endpoint นี้มีไว้สำหรับผู้สอนดูรายชื่อผู้เข้าร่วมคลาส

    Parameters
    ----------
    instructor_id : str
        รหัสผู้สอนที่ร้องขอรายการ
    event_id : str
        รหัสกิจกรรม

    Returns
    -------
    dict
        ตอบกลับ JSON ที่มีรายการรหัสผู้ใช้ผู้เข้าร่วมและอาจมี
        เมตาดาต้าเพิ่มเติม
    """
    return requests.post(f"{BASE}/show_event_attenders", params={
        "instructor_id": instructor_id,
        "event_id": event_id
    }).json()

@mcp.tool()
def show_all_events() -> dict:
    """
    ส่งคืนข้อมูลเกี่ยวกับกิจกรรมทั้งหมดที่ระบบกำหนดไว้

    เป็นคำขออ่านอย่างเดียวที่มีประโยชน์สำหรับการแสดงหรือ
    การวางแผนกิจกรรม

    Returns
    -------
    dict
        payload JSON ที่แทนกิจกรรมทั้งหมด, เวลา, สถานะ และรายละเอียด
        ที่เกี่ยวข้องอื่นๆ
    """
    return requests.get(f"{BASE}/show_all_events").json()

@mcp.tool()
def show_available_resource() -> dict:
    """
    ค้นหาเซิร์ฟเวอร์สำหรับทรัพยากรทั้งหมดที่ขณะนี้พร้อมใช้งาน
    สำหรับการจอง

    ไม่รวมทรัพยากรที่กำลังใช้งานหรืออยู่ระหว่างบำรุงรักษา

    Returns
    -------
    dict
        วัตถุ JSON ที่แสดงรายการพื้นที่, อุปกรณ์, และวัสดุที่
        พร้อมใช้งานพร้อมสถานะของแต่ละรายการ
    """
    return requests.get(f"{BASE}/show_available_resource").json()

@mcp.tool()
def show_all_resource() -> dict:
    """
    ดึงสินค้าคงคลังทรัพยากรทั้งหมดที่ระบบจัดการ โดยไม่คำนึงถึง
    ความพร้อมใช้งานปัจจุบัน

    มีประโยชน์สำหรับภาพรวมของผู้ดูแลระบบหรือการรายงาน

    Returns
    -------
    dict
        JSON ที่มีพื้นที่ทั้งหมด, อุปกรณ์, วัสดุ, สถานะ, และเมตา
        ดาต้าที่เกี่ยวข้อง
    """
    return requests.get(f"{BASE}/show_all_resource").json()

@mcp.tool()
def show_notifications(user_id: str) -> dict:
    """
    ดึงคิวการแจ้งเตือนสำหรับผู้ใช้เฉพาะ

    Parameters
    ----------
    user_id : str
        รหัสของผู้ใช้ที่ต้องการดึงการแจ้งเตือน

    Returns
    -------
    dict
        API โดยปกติจะส่งคืนรายการวัตถุการแจ้งเตือน ฟังก์ชันช่วย
        นี้ปรับให้ออกมาเป็นพจนานุกรมที่มีคีย์ ``"notifications"``
        ซึ่งประกอบด้วยรายการนั้น หากเซิร์ฟเวอร์ส่งสตริงข้อ
        ผิดพลาดกลับมา จะส่งค่านั้นโดยตรง
    """
    result = requests.get(f"{BASE}/notifications", params={"user_id": user_id}).json()
    if isinstance(result, list):
        return {"notifications": result}
    return result

if __name__ == "__main__":
    mcp.run()