from fastapi import APIRouter, HTTPException
from app.schemas import UserCreate, UserUpdate
from app import crud

router = APIRouter(prefix="/users", tags=["users"])

@router.post("/")
def create_user(user: UserCreate):
    try:
        user_id = crud.create_user_in_db(user.email, user.password)
        return {"id": user_id, "email": user.email}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/")
def get_users():
    return {"users": crud.get_all_users()}

@router.get("/{user_id}")
def get_user(user_id: int):
    user = crud.get_user_by_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@router.put("/{user_id}")
def update_user(user_id: int, user: UserUpdate):
    rowcount = crud.update_user_in_db(user_id, user.email, user.password)
    if rowcount == 0:
        raise HTTPException(status_code=404, detail="User not found or no fields to update")
    return {"message": "User updated successfully"}

@router.delete("/{user_id}")
def delete_user(user_id: int):
    rowcount = crud.delete_user_in_db(user_id)
    if rowcount == 0:
        raise HTTPException(status_code=404, detail="User not found")
    return {"message": "User deleted successfully"}
