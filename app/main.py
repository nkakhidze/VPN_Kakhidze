from fastapi import FastAPI

app = FastAPI()


@app.get("/")
def hello():
    return {
        "message": "Hello, FastAPI!"
    }

@app.get("/users/{user_id}")
def get_user(user_id: int):
    return {
        "user_id": user_id,
        "name": "Nikolay"
    }