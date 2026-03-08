from controller import system_init

from fastapi import FastAPI
import uvicorn

sys = system_init()

''' API Goes Here '''
app = FastAPI()

@app.get("/")
def test_route():
    return {"message": "Test Route"}

@app.post("/reserve/{user_id}")
def reserve_api(user_id: str):
    result = sys.reserve(user_id)
    return {
        "message": result["message"]
    }

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
