from pydantic import BaseModel

class LogOrders(BaseModel):
    nama_barang : str
    stok : int     
    jumlah_terjual : int
    jenis_barang : str