from database import Base
from sqlalchemy import Column, ForeignKey , Integer, String , Boolean 

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer , primary_key=True , index=True)
    ft_name = Column(String)
    lt_name = Column(String)
    username = Column(String , unique=True)
    hashed_password = Column(String)
    email = Column(String , unique=True)
    role = Column(String)
    is_active  = Column(Boolean , default=True)

class ToDos(Base):
    __tablename__ = "todos"
    
    id = Column(Integer , primary_key=True , index=True) 
    title = Column(String)
    description = Column(String)
    priority = Column(Integer)
    completed = Column(Boolean , default=False)
    owner_id = Column(Integer , ForeignKey("users.id"))
