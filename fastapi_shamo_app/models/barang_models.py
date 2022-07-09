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

class Barang(Base):
    __tablename__ = "barang"

    id = Column(BigInteger, primary_key=True, index=True, autoincrement=True)
    jenis_barang_id = Column(BigInteger, ForeignKey("jenis_barang.id"))
    nama_barang = Column(String(36))
    modified_at = Column(
        TIMESTAMP, server_default=func.now(), onupdate=func.current_timestamp()
    )

    __mapper_args__ = {
        "eager_defaults": True,
    }