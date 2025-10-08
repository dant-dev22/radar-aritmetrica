import logging
from fastapi import APIRouter, HTTPException
from app.schemas import UserCreate, UserUpdate
import os
import pymysql

# Configure logger
logger = logging.getLogger("users_router")
logger.setLevel(logging.INFO)
if not logger.handlers:
    ch = logging.StreamHandler()
    formatter = logging.Formatter("[%(levelname)s] %(asctime)s - %(message)s")
    ch.setFormatter(formatter)
    logger.addHandler(ch)

router = APIRouter(prefix="/users", tags=["users"])

# ----------------------------
# Función interna de conexión
# ----------------------------
def get_db_connection():
    return pymysql.connect(
        host=os.getenv("DB_HOST"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        database=os.getenv("DB_NAME"),
        cursorclass=pymysql.cursors.DictCursor,  # Homogeneiza todas las consultas
    )

# ----------------------------
# Endpoints
# ----------------------------

@router.get("/users-test")
def users_test():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id, email FROM users LIMIT 1")
        result = cursor.fetchall()
        cursor.close()
        conn.close()
        logger.info("users_test executed successfully")
        return {"result": result}
    except Exception as e:
        logger.error(f"users_test error: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/ping")
def ping():
    logger.info("GET ping called")
    return "hola mundo"


@router.post("/")
def create_user(user: UserCreate):
    logger.info(f"POST /users called with email={user.email}")
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO users (email, password) VALUES (%s, %s)", (user.email, user.password))
        conn.commit()
        user_id = cursor.lastrowid
        cursor.close()
        conn.close()
        logger.info(f"User created with id={user_id}")
        return {"id": user_id, "email": user.email}
    except pymysql.err.IntegrityError:
        logger.warning(f"Failed to create user {user.email}: Email already exists")
        raise HTTPException(status_code=400, detail="Email already exists")
    except Exception as e:
        logger.error(f"Unexpected error in create_user: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/")
def get_users():
    logger.info("GET /users called")
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id, email FROM users")
        users = cursor.fetchall()
        cursor.close()
        conn.close()
        logger.info(f"Retrieved {len(users)} users")
        return {"users": users}
    except Exception as e:
        logger.error(f"Error fetching users: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/{user_id}")
def get_user(user_id: int):
    logger.info(f"GET /users/{user_id} called")
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id, email FROM users WHERE id = %s", (user_id,))
        user = cursor.fetchone()
        cursor.close()
        conn.close()
        if not user:
            logger.warning(f"User id={user_id} not found")
            raise HTTPException(status_code=404, detail="User not found")
        logger.info(f"User retrieved: {user}")
        return user
    except Exception as e:
        logger.error(f"Error fetching user {user_id}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.put("/{user_id}")
def update_user(user_id: int, user: UserUpdate):
    logger.info(f"PUT /users/{user_id} called with email={user.email}")
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        fields = []
        values = []
        if user.email:
            fields.append("email = %s")
            values.append(user.email)
        if user.password:
            fields.append("password = %s")
            values.append(user.password)
        if not fields:
            logger.warning("No fields to update")
            raise HTTPException(status_code=400, detail="No fields to update")
        sql = f"UPDATE users SET {', '.join(fields)} WHERE id = %s"
        values.append(user_id)
        cursor.execute(sql, tuple(values))
        conn.commit()
        rowcount = cursor.rowcount
        cursor.close()
        conn.close()
        if rowcount == 0:
            logger.warning(f"User id={user_id} not found")
            raise HTTPException(status_code=404, detail="User not found")
        logger.info(f"User id={user_id} updated successfully")
        return {"message": "User updated successfully"}
    except Exception as e:
        logger.error(f"Error updating user {user_id}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.delete("/{user_id}")
def delete_user(user_id: int):
    logger.info(f"DELETE /users/{user_id} called")
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM users WHERE id = %s", (user_id,))
        conn.commit()
        rowcount = cursor.rowcount
        cursor.close()
        conn.close()
        if rowcount == 0:
            logger.warning(f"User id={user_id} not found")
            raise HTTPException(status_code=404, detail="User not found")
        logger.info(f"User id={user_id} deleted successfully")
        return {"message": "User deleted successfully"}
    except Exception as e:
        logger.error(f"Error deleting user {user_id}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")
