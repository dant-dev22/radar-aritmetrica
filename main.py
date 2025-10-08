from fastapi import FastAPI
from app.routers import users
from mangum import Mangum


app = FastAPI(title="Radar API")

app.include_router(users.router)

handler = Mangum(app)