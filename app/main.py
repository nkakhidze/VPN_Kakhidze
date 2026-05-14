from fastapi import FastAPI
from app.api.users import router as users_router
from app.api.subscription_reminders import router as subscription_reminders_router
from app.api.payments import router as payments_router

app = FastAPI()
app.include_router(users_router)
app.include_router(subscription_reminders_router)
app.include_router(payments_router)

@app.get("/")
def hello():
    return {
        "message": "Hello, FastAPI!"
    }


