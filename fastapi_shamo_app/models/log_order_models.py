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

class LogOrders(Base):
    __tablename__ = "log_orders"

    id = Column(BigInteger, ForeignKey("transaksi.id"), primary_key = True, autoincrement = True)
    nama_barang = Column(String(50))
    stok = Column(Integer)       
    jumlah_terjual = Column(Integer)
    jenis_barang = Column(String(50))

    tanggal_transaksi = Column(TIMESTAMP, server_default=func.now(), index=True)
    
    __mapper_args__ = {"eager_defaults": True}