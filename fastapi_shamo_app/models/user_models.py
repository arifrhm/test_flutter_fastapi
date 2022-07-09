from sqlalchemy import Table, Column
from sqlalchemy.sql.sqltypes import Integer, String
from db import Base
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy import (
    Column,
    Integer,
    String,
    BigInteger,
    ForeignKey,
    Date,
    DateTime,
    Numeric,
    Text,
    TIMESTAMP,
)
from sqlalchemy.sql import func
import uuid

class Users(Base):
    __tablename__ = "users"

    id = Column( Integer, primary_key = True, index = True, autoincrement = True)
    name = Column(String(255))
    email = Column(String(255))       
    password = Column(String(255))
    created_at = Column(TIMESTAMP, server_default=func.now(), index=True)
    
    __mapper_args__ = {"eager_defaults": True}