from fastapi import APIRouter , Depends, HTTPException, Path
from starlette import status
from typing import Annotated 
from sqlalchemy.orm import Session 
from models import ToDos
from database import  SessionLocal
from pydantic import BaseModel ,Field
from .auth import get_current_user
# Create a APIRouter instance
router = APIRouter(
    prefix="/todos",
    tags=["todos"]
)

# Create a ToDo model required by Pydantic
class ToDoRequest(BaseModel):
    title : str = Field(min_length = 3)
    description : str = Field(min_length = 3 ,  max_length= 100 )
    priority : int  = Field(ge = 1, le = 5)
    completed : bool = Field(default = False)



def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

db_dependency = Annotated[Session,Depends(get_db)]
user_dependency = Annotated[dict, Depends(get_current_user)]

@router.get("/" ,status_code = status.HTTP_200_OK )
async def read_all(user : user_dependency,db : db_dependency) :
    if user is None :   
        raise HTTPException(status_code= 401 , detail= "Authorization Failed")
    return db.query(ToDos).filter(ToDos.owner_id == user.get("user_id")).all()

@router.get("/todo/{todo_id}" ,status_code = status.HTTP_200_OK )
async def read_todo(user : user_dependency, db : db_dependency , todo_id : int = Path(... , gt = 0)  ) :
    if user is None :
        raise HTTPException(status_code= 401 , detail= "Authorization Failed")
    
    todo_model =  db\
                    .query(ToDos)\
                    .filter(ToDos.id == todo_id)\
                    .filter(ToDos.owner_id == user.get("user_id"))\
                    .first()
    
    if  todo_model is not None:
        return todo_model
    raise HTTPException(status_code = 404 , detail = "todo not found")


@router.post("/todo/" ,status_code = status.HTTP_201_CREATED )
async def create_todo( user : user_dependency ,db : db_dependency,todo : ToDoRequest ) :
    if user is None :
        raise HTTPException(status_code= 401 , detail= "Authorization Failed")
    
    new_todo = ToDos(**todo.model_dump() , owner_id = user.get("user_id")) 
    db.add(new_todo)
    db.commit()
    db.refresh(new_todo)

def find_task_by_id(todo_id : int, db : db_dependency , user : user_dependency) -> ToDos:
    return db.query(ToDos).filter(ToDos.id == todo_id).filter(ToDos.owner_id == user.get("user_id")).first()

@router.put("/todo/{todo_id}" ,status_code = status.HTTP_204_NO_CONTENT )
async def update_todo(
                    user : user_dependency ,
                    db : db_dependency ,
                    new_todo : ToDoRequest ,
                    todo_id :int = Path(... , gt = 0) 
                    ):
    if user is None :   
        raise HTTPException(status_code= 401 , detail= "Authorization Failed")
    
    todo_model =  find_task_by_id(todo_id = todo_id , db = db, user = user)

    if todo_model is  None:
        raise HTTPException(status_code= 404 , detail= "Todo Not found")

    todo_model.title = new_todo.title
    todo_model.description = new_todo.description
    todo_model.completed = new_todo.completed
    todo_model.priority = new_todo.priority
    db.add(todo_model)
    db.commit()


@router.delete("/todo/{todo_id}", status_code= status.HTTP_204_NO_CONTENT)
async def delete_todo(
    user : user_dependency ,
    db: db_dependency ,
    todo_id : int = Path(... , gt = 0)
    ):
    #Body Of function ....

    t = find_task_by_id(todo_id= todo_id , db = db , user = user )
    if t is None :
        raise HTTPException(status_code= 404 ,  detail= "ToDo Not found") 
    db.delete(t)
    db.commit()