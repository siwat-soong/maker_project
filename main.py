from controller import *
from fastapi import FastAPI
import uvicorn

sys = system_init()

''' API Goes Here '''
app = FastAPI()

@app.get("/")
def test_route():
    return {"message": "Test Route"}

@app.get("/show_available_event")
def show_available_event():

    available_events = []
    for event in sys.event_list:
        status = event.get_status()
        if status == EventStatus.OPEN: 
            detail = event.show_detail()
            available_events.append(detail)
    return {
        "message": "Show Available Event Complete",
        "data": available_events
    }

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
