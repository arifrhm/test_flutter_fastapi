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

class Transaksi(Base):
    __tablename__ = "transaksi"

    id = Column(BigInteger, primary_key=True, index=True, autoincrement=True)
    stocks_id = Column(BigInteger, ForeignKey("stocks.id"))
    barang_id = Column(BigInteger, ForeignKey("barang.id"))
    jenis_barang_id = Column(BigInteger, ForeignKey("jenis_barang.id"))
    nama_barang = Column(String(36))
    stock = Column(BigInteger)
    jumlah_terjual = Column(BigInteger)
    jenis_barang = Column(String(36))
    tanggal_transaksi = Column(TIMESTAMP, server_default=func.now(), index=True)
    modified_at = Column(
        TIMESTAMP, server_default=func.now(), onupdate=func.current_timestamp()
    )

    __mapper_args__ = {"polymorphic_identity": "Transaksi"}