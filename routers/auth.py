from datetime import datetime, timedelta, timezone
from typing import Annotated
from fastapi import APIRouter , Depends , HTTPException
from pydantic import BaseModel, Field
from starlette import status
from models import User
from sqlalchemy.orm import Session
from passlib.context import CryptContext
from database import SessionLocal 
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from jose import JWTError, jwt

#Feature Router
router = APIRouter(
    prefix= "/auth",
    tags= ["auth"]
)

bcrypt_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth_bearer = OAuth2PasswordBearer(tokenUrl= "auth/token")
SECRYPT_KEY = "bae7085b90e3a08dffbf0fbfa84fe82aef06a1b747f7b4e42c5c645f8efb7f54"
ALGORITHM = "HS256"
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

db_dependency = Annotated[Session, Depends(get_db)]

class CreateUserRequest(BaseModel):
    username : str = Field(min_length = 3)
    ft_name : str = Field(min_length = 3)
    lt_name : str = Field(min_length = 3)

    password : str = Field(min_length = 3 ,  max_length= 100 )
    email : str = Field(min_length = 3)
    role : str 

class Token(BaseModel):
    access_token : str
    token_type : str



@router.post("/" , status_code = status.HTTP_201_CREATED)
async def create_user(new_user : CreateUserRequest , db : db_dependency):
    user_model = User(
        username = new_user.username,
        ft_name = new_user.ft_name,
        lt_name = new_user.lt_name,
        hashed_password = bcrypt_context.hash( new_user.password),
        email = new_user.email,
        role = new_user.role,
        is_active  = True
    )

    db.add(user_model)
    db.commit()

def authenricate_user(
        username :str,
        password : str,
        db :db_dependency
):
    user = db.query(User).filter(User.username == username).first()
    if not user:
        return False
    
    if not bcrypt_context.verify(password ,user.hashed_password):
        return False
    
    return user

def create_access_token(username :str , user_id : int , expires_delta : timedelta)-> dict:
    encode = {
        'sub' : username,
        'id' : user_id
    }
    expires = datetime.now(timezone.utc) + expires_delta
    encode.update({'exp' : expires})
    return jwt.encode(encode , SECRYPT_KEY , algorithm = ALGORITHM)

async def get_current_user(token :Annotated [str, Depends(oauth_bearer)]):
    try:
        payload = jwt.decode(token , SECRYPT_KEY ,algorithms= [ALGORITHM] )
        username : str = payload.get("sub")
        user_id : int = payload.get("id")
        if username is None or user_id is None:
            raise HTTPException(status_code= status.HTTP_401_UNAUTHORIZED , detail= "Could Not validate User")
        else : 
            return {
                "username" : username,
                "user_id" : user_id
            }
        
    except  JWTError:
        raise HTTPException(status_code= status.HTTP_401_UNAUTHORIZED , detail= "Could Not validate User")


@router.post("/token" , response_model= Token)
async def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm , Depends()],
    db:db_dependency                             
):
    user = authenricate_user(form_data.username , form_data.password , db)    
    if not user:
        raise HTTPException(status_code= status.HTTP_401_UNAUTHORIZED , detail= "Could Not validate User")
    
    token = create_access_token(
        username= user.username ,
        user_id = user.id ,
        expires_delta = timedelta(minutes = 20)
    )    
    return {"access_token" : token,"token_type" : "bearer"}

