from controller import *
from fastapi import FastAPI
import uvicorn

sys = system_init()

''' API Goes Here '''
app = FastAPI()

@app.get("/")
def test_route():
    return {"message": "Test Route"}

@app.get("/show_available_resource")
def show_available_resource_api():
    
    available_resources = sys.request_show_available_resource()
    
   
    return {
        "message": "Show Available Resource Complete",
        "data": available_resources
    }

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
