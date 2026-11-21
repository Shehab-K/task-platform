from sqlalchemy import Column,Integer,String,Text
from database import Base

class Task(Base):
    __tablename__ ="tasks"

    id=Column(Integer,primary_key=True,index=True)
    title=Column(String,nullable=False)
    description=Column(Text,nullable=True)
    status=Column(String,default="pending")
    retry_count=Column(Integer,default=0,nullable=False)
    error_message=Column(Text,nullable=True)