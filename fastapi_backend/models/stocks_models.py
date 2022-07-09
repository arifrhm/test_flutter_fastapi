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

class Stocks(Base):
    __tablename__ = "stocks"

    id = Column(BigInteger, primary_key=True, index=True, autoincrement=True)
    barang_id = Column(BigInteger, ForeignKey("barang.id"))
    nama_barang = Column(String(36))
    stock = Column(BigInteger)
    modified_at = Column(
        TIMESTAMP, server_default=func.now(), onupdate=func.current_timestamp()
    )

    __mapper_args__ = {
        "eager_defaults": True,
    }