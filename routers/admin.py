from fastapi import APIRouter , Depends, HTTPException, Path
from starlette import status
from typing import Annotated 
from sqlalchemy.orm import Session 
from models import ToDos
from database import  SessionLocal
from pydantic import BaseModel ,Field
from .auth import get_current_user
from .todos import find_task_by_id
# Create a APIRouter instance
router = APIRouter(
    prefix="/admin",
    tags=["admin"]
)

# Create a ToDo model required by Pydantic



def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

db_dependency = Annotated[Session,Depends(get_db)]
user_dependency = Annotated[dict, Depends(get_current_user)]



@router.get("/todo" ,status_code = status.HTTP_200_OK ) 
async def read_all(db : db_dependency , user : user_dependency ) :
    if user is None or user.get("role") != "Admin" :
        raise HTTPException(status_code= 401 , detail= "Authenication Failed")
    
    return db.query(ToDos).all()

@router.delete("/todo/{todo_id}", status_code= status.HTTP_204_NO_CONTENT)
async def delete_todo(db : db_dependency ,user : user_dependency, todo_id : int = Path(... , gt = 0) ) :
    if user is None or user.get("role") != "Admin" :
        raise HTTPException(status_code= 401 , detail= "Authenication Failed")

    todo_model : ToDos = find_task_by_id(todo_id= todo_id , db = db ,  user= user)
    if todo_model is None :
        raise HTTPException(status_code= 404 ,  detail= "ToDo Not found")

    db.delete(todo_model)
    db.commit()