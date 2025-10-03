from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import pymysql
import os
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

DB_CONFIG = {
    "host": os.getenv("DB_HOST"),
    "user": os.getenv("DB_USER"),
    "password": os.getenv("DB_PASSWORD"),
    "database": os.getenv("DB_NAME"),
    "port": int(os.getenv("DB_PORT", 3306))
}

app = FastAPI(title="Rappers API")

# Modelo de datos para el request
class UserCreate(BaseModel):
    email: str
    password: str  # recuerda que en producción debería ir hashed

# Función para conectar a la DB
def get_db_connection():
    return pymysql.connect(**DB_CONFIG)

# Endpoint para crear un usuario
@app.post("/users")
def create_user(user: UserCreate):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Query de inserción
        sql = "INSERT INTO users (email, password) VALUES (%s, %s)"
        cursor.execute(sql, (user.email, user.password))
        conn.commit()
        user_id = cursor.lastrowid

        cursor.close()
        conn.close()
        return {"id": user_id, "email": user.email}

    except pymysql.err.IntegrityError as e:
        raise HTTPException(status_code=400, detail="Email already exists")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
