from fastmcp import FastMCP
import requests

mcp = FastMCP("maker_club_mcp")

BASE = "http://127.0.0.1:8000"

@mcp.tool()
def show_user_info(user_id: str) -> dict:
    return requests.get(f"{BASE}/user_info", params={"user_id": user_id}).json()


@mcp.tool()
def show_notifications(user_id: str) -> dict:
    result = requests.get(f"{BASE}/notifications", params={"user_id": user_id}).json()
    # wrap list ให้เป็น dict
    if isinstance(result, list):
        return {"notifications": result}
    return result


@mcp.tool()
def subscribe(user_id: str) -> dict:
    return requests.post(f"{BASE}/subscribe", params={"user_id": user_id}).json()


@mcp.tool()
def pay(user_id: str, inv_id: str, cost: float, method_id: str) -> dict:
    return requests.post(f"{BASE}/pay", params={
        "user_id": user_id,
        "inv_id": inv_id,
        "cost": cost,
        "method_id": method_id
    }).json()


@mcp.tool()
def add_to_cart(user_id: str, item_id: str, start_time: str, end_time: str, amount: float = 1) -> dict:
    return requests.post(f"{BASE}/add_to_cart", params={
        "user_id": user_id,
        "item_id": item_id,
        "start_time": start_time,
        "end_time": end_time,
        "amount": amount
    }).json()


@mcp.tool()
def reserve(user_id: str) -> dict:
    return requests.post(f"{BASE}/reserve", params={"user_id": user_id}).json()


@mcp.tool()
def create_event(admin_id: str, topic: str, detail: str, start_time: str, end_time: str,
                 instructor_id: str, space_id: str, max_attender: int, join_fee: float) -> dict:
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
    return requests.post(f"{BASE}/event/join", params={
        "user_id": user_id,
        "event_id": event_id
    }).json()


@mcp.tool()
def add_equipment_to_event(user_id: str, event_id: str) -> dict:
    return requests.put(f"{BASE}/event/add", params={
        "user_id": user_id,
        "event_id": event_id
    }).json()


@mcp.tool()
def check_in(user_id: str, rsv_id: str, space_id: str, start_time: str) -> dict:
    return requests.post(f"{BASE}/checkin", params={
        "user_id": user_id,
        "rsv_id": rsv_id,
        "space_id": space_id,
        "start_time": start_time
    }).json()


@mcp.tool()
def check_out(user_id: str, rsv_id: str, space_id: str, start_time: str) -> dict:
    return requests.post(f"{BASE}/checkout", params={
        "user_id": user_id,
        "rsv_id": rsv_id,
        "space_id": space_id,
        "start_time": start_time
    }).json()


@mcp.tool()
def return_equipment(user_id: str, rsv_id: str, equipment_id: str, start_time: str) -> dict:
    return requests.post(f"{BASE}/return_eq", params={
        "user_id": user_id,
        "rsv_id": rsv_id,
        "equipment_id": equipment_id,
        "start_time": start_time
    }).json()

@mcp.tool()
def cancel_reserve(user_id: str, rsv_id: str) -> dict:
    return requests.post(f"{BASE}/cancel_reserve", params={
        "user_id": user_id,
        "rsv_id": rsv_id
    }).json()

@mcp.tool()
def add_certificate(instructor_id: str, event_id: str, user_id: str, score: float) -> dict:
    return requests.post(f"{BASE}/event/certificate", params={
        "instructor_id": instructor_id,
        "event_id": event_id,
        "user_id": user_id,
        "score": score
    }).json()


@mcp.tool()
def show_event_attenders(instructor_id: str, event_id: str) -> dict:
    return requests.post(f"{BASE}/show_event_attenders", params={
        "instructor_id": instructor_id,
        "event_id": event_id
    }).json()


@mcp.tool()
def show_available_resource() -> dict:
    return requests.get(f"{BASE}/show_available_resource").json()


@mcp.tool()
def show_all_resource() -> dict:
    return requests.get(f"{BASE}/show_all_resource").json()

if __name__ == "__main__":
    mcp.run()