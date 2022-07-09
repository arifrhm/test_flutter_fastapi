from optparse import Option
from pydantic import BaseModel
from typing import Optional

class Transaksi(BaseModel):
    stocks_id : int # Dari front end
    barang_id : int # Dari front end
    jenis_barang_id : int # Dari front end
    nama_barang : str # Dari barang_id
    # stock : int
    jumlah_terjual : int # input manual
    jenis_barang : str # Dari barang_id lalu
    tanggal_transaksi : Optional[str]