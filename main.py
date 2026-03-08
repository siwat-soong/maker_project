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
def show_available_event_api():
    result_events = sys.request_show_available_event()
    return {
        "message": "Show Available Event Complete",
        "data": result_events
    }

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
