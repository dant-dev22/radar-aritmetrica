from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import users
from mangum import Mangum

app = FastAPI(title="Radar API")

# Configuración CORS
origins = [
    "*"  # Reemplaza con tu dominio en producción
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(users.router)

handler = Mangum(app)
