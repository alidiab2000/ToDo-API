from fastapi import APIRouter , Depends, HTTPException, Path 
from starlette import status
from pydantic import BaseModel , Field
from models import  User
from .todos import db_dependency , user_dependency
from jose import JWTError, jwt
from passlib.context import CryptContext
# Create a APIRouter instance
router = APIRouter(
    prefix="/user",
    tags=["user"]
)

bcrypt_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
SECRYPT_KEY = "bae7085b90e3a08dffbf0fbfa84fe82aef06a1b747f7b4e42c5c645f8efb7f54"
ALGORITHM = "HS256"

class UserVerification(BaseModel):
    password : str = Field(... , min_length= 3 )
    new_password : str = Field(... , min_length= 3 )


@router.get("/" ,status_code = status.HTTP_200_OK )
async def read_all(user : user_dependency,db : db_dependency) :
    if user is None :   
        raise HTTPException(status_code= 401 , detail= "Authorization Failed")
    return db.query(User).filter(User.id == user.get("user_id")).all()

@router.put("/password" ,status_code = status.HTTP_204_NO_CONTENT )
async def change_pass(user : user_dependency , db : db_dependency ,user_verification : UserVerification) :
    if user is None :   
        raise HTTPException(status_code= 401 , detail= "Authorization Failed")

    user_model = db.query(User).filter(User.id == user.get("user_id")).first()

    if user_model is None :
        raise HTTPException(status_code= 404 , detail= "User Not found")    
    
    if not bcrypt_context.verify(user_verification.password , user_model.hashed_password):
        raise HTTPException(status_code= 404 , detail= "Invalid Password")
    if user_verification.new_password == user_verification.password:
        raise HTTPException(status_code= 404 , detail= "Invalid change to the Same Password")
    
    user_model.hashed_password = bcrypt_context.hash(user_verification.new_password)
    db.add(user_model)
    db.commit()
    db.refresh(user_model)
