from fastapi import FastAPI
import uvicorn

app = FastAPI()

@app.get("/")
def ping():
    return {
        "status": "ok",
        "message": "pong"
    }



# Running Section
def run_api():
    uvicorn.run("api_demo:app", host="127.0.0.1", port=8000, reload=True)

if __name__ == "__main__":
    run_api()