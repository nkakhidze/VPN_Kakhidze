from fastapi import FastAPI

app = FastAPI()


@app.get("/")
def hello():
    return {
        "message": "Hello, FastAPI!"
    }

@app.get("/users")
def get_users():
    return [
        {
            "id": 1,
            "email": "test@test.com",
            "name": "Nikolay"
        },
        {
            "id": 2,
            "email": "admin@test.com",
            "name": "Admin"
        }
    ]