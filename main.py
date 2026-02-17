from controller import *
from fastapi import FastAPI
import uvicorn

system_init()

''' API Goes Here '''
app = FastAPI()

@app.get("/")
def test_route():
    return {"message": "Test Route"}

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
