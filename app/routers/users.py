import logging
from fastapi import APIRouter, HTTPException
from app.schemas import UserCreate, UserUpdate
from app import crud
import pymysql

# Configure logger
logger = logging.getLogger("users_router")
logger.setLevel(logging.INFO)

router = APIRouter(prefix="/users", tags=["users"])

@router.get("/users-test")
def users_test():
    conn = pymysql.connect(
        host=os.getenv("DB_HOST"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        database=os.getenv("DB_NAME"),
    )
    cursor = conn.cursor()
    cursor.execute("SELECT id, email FROM users LIMIT 1")
    result = cursor.fetchall()
    cursor.close()
    conn.close()
    return {"result": result}


@router.get("/ping")
def ping():
    logger.info("GET ping called")
    return "hola mundo"

@router.post("/")
def create_user(user: UserCreate):
    logger.info(f"POST /users called with email={user.email}")
    try:
        user_id = crud.create_user_in_db(user.email, user.password)
        logger.info(f"User created with id={user_id}")
        return {"id": user_id, "email": user.email}
    except ValueError as e:
        logger.warning(f"Failed to create user {user.email}: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error in create_user: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/")
def get_users():
    logger.info("GET /users called")
    try:
        users = crud.get_all_users()
        logger.info(f"Retrieved {len(users)} users")
        return {"users": users}
    except Exception as e:
        logger.error(f"Error fetching users: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/{user_id}")
def get_user(user_id: int):
    logger.info(f"GET /users/{user_id} called")
    try:
        user = crud.get_user_by_id(user_id)
        if not user:
            logger.warning(f"User id={user_id} not found")
            raise HTTPException(status_code=404, detail="User not found")
        return user
    except Exception as e:
        logger.error(f"Error fetching user {user_id}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.put("/{user_id}")
def update_user(user_id: int, user: UserUpdate):
    logger.info(f"PUT /users/{user_id} called with email={user.email}")
    try:
        rowcount = crud.update_user_in_db(user_id, user.email, user.password)
        if rowcount == 0:
            logger.warning(f"User id={user_id} not found or no fields to update")
            raise HTTPException(status_code=404, detail="User not found or no fields to update")
        logger.info(f"User id={user_id} updated successfully")
        return {"message": "User updated successfully"}
    except Exception as e:
        logger.error(f"Error updating user {user_id}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.delete("/{user_id}")
def delete_user(user_id: int):
    logger.info(f"DELETE /users/{user_id} called")
    try:
        rowcount = crud.delete_user_in_db(user_id)
        if rowcount == 0:
            logger.warning(f"User id={user_id} not found")
            raise HTTPException(status_code=404, detail="User not found")
        logger.info(f"User id={user_id} deleted successfully")
        return {"message": "User deleted successfully"}
    except Exception as e:
        logger.error(f"Error deleting user {user_id}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")
