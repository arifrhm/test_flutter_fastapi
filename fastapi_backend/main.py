from fastapi import FastAPI
from routes.users import user
from routes.log_orders import log_orders
from routes.barang import barang
from routes.transaksi import transaksi
from fastapi.middleware.cors import CORSMiddleware
import logging.config
import logging.config

from fastapi import FastAPI
from fastapi.logger import logger
from fastapi.param_functions import Depends

from db import engine, Base
from starlette.middleware.cors import CORSMiddleware

from seeders import (
    barang_seeder,
    jenis_barang_seeder,
    stock_seeder
)
# setup loggers
logging.config.fileConfig("./logging.conf", disable_existing_loggers=False)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
@app.on_event("startup")
async def startup():
    async with engine.begin() as conn:
        # DELETE ALL TABLE
        # await conn.run_sync(Base.metadata.drop_all)

        # CREATE ALL TABLE based on imported models
        await conn.run_sync(Base.metadata.create_all)
        # migration seed
        logger.info("Migration started...")

        await jenis_barang_seeder.start(conn)
        
        await barang_seeder.start(conn)
        
        await stock_seeder.start(conn)

        logger.info("Migration finished...")
        
app.include_router(user,prefix="/users",tags=["Users"] )
app.include_router(log_orders,prefix="/log_orders",tags=["Log Orders"])
app.include_router(barang,prefix="/barang",tags=["Barang"])
app.include_router(transaksi,prefix="/transaksi",tags=["Transaksi"])