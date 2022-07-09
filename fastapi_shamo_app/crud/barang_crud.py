from datetime import datetime
import json
from models import barang_models, jenis_barang_models, stocks_models, user_models
from services.core_scheme import ResponseOutCustom
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import update, outerjoin
from sqlalchemy.exc import SQLAlchemyError
import gevent
from fastapi.logger import logger
from fastapi.encoders import jsonable_encoder

async def fetch_barang(db_session :AsyncSession) -> ResponseOutCustom:
    async with db_session as session:
        try :
            #Join semua table yang berhubungan dengan barang
            tbl_brg = barang_models.Barang
            tbl_stk = stocks_models.Stocks
            tbl_jns_brg = jenis_barang_models.JenisBarang
            j1 = outerjoin(tbl_brg,tbl_stk, tbl_stk.barang_id == tbl_brg.id)
            j2 = outerjoin(j1, tbl_jns_brg, tbl_jns_brg.id == tbl_brg.jenis_barang_id)

            query_fetch_barang = select(
                tbl_brg.id,
                tbl_brg.jenis_barang_id,
                tbl_stk.barang_id,
                tbl_brg.nama_barang,
                tbl_stk.stock,
                tbl_jns_brg.jenis_barang
                ).select_from(j2).order_by(tbl_brg.nama_barang.asc())
            logger.info(query_fetch_barang)

            proxy_rows = await session.execute(query_fetch_barang)
            # parse result as list of object
            result = proxy_rows.fetchall()#scalars().all()
            # commit the db transaction
            await session.commit()

            list_barang = []

            for barang in result:
                list_barang.append(
                    {
                        "id": jsonable_encoder(barang.id),
                        "jenis_barang_id": jsonable_encoder(barang.jenis_barang_id),
                        "stock_barang_id" :jsonable_encoder(barang.id),
                        "nama_barang": jsonable_encoder(barang.nama_barang),
                        "stock": jsonable_encoder(barang.stock),
                        "jenis_barang" : jsonable_encoder(barang.jenis_barang)
                    }
                )
        except gevent.Timeout:
            # database timeout
            await session.invalidate()
            return ResponseOutCustom(
                message_id="02",
                status="Failed, DB transaction was timed out...",
                list_data=None,
            )

        except SQLAlchemyError as e:
            logger.error(e)
            # rollback db if error
            await session.rollback()
            return ResponseOutCustom(
                message_id="02",
                status="Failed, something wrong rollback DB transaction...",
                list_data=None,
            )

        if result:
            # success
            return ResponseOutCustom(message_id="00", status="Fetch All Barang Datas Success", list_data=list_barang)
        else:
            # data not found
            return ResponseOutCustom(
                message_id="01",
                status=f"Failed, Users not found...",
                list_data=[],
            )

async def fetch_barang_by_id(id: int, db_session :AsyncSession) -> ResponseOutCustom:
    async with db_session as session:
        try:
            tbl_brg = barang_models.Barang
            tbl_stk = stocks_models.Stocks
            # Select stocks by barang_id
            query_stock = select(tbl_stk).filter(tbl_stk.barang_id==id)

            logger.info(query_stock)
            # execute query
            proxy_rows_stock = await session.execute(query_stock)
            # parse result as list of object
            result_stock = proxy_rows_stock.scalars().all()  # .scalars().first()
            # commit the db transaction
            await session.commit()
            # Test print jsonable_encoder stock
            # logger.info("jsonable_encoder(result_stock) :",jsonable_encoder(result_stock))

            # Select barang by id
            query_stmt = select(tbl_brg).filter(tbl_brg.id==id)

            logger.info(query_stmt)
            # execute query
            proxy_rows = await session.execute(query_stmt)
            # parse result as list of object
            result = proxy_rows.scalars().all()  # .scalars().first()
            # commit the db transaction
            await session.commit()
            # Test print jsonable_encoder barang
            # logger.info("jsonable_encoder(result) :", jsonable_encoder(result))

            # Select jenis_barang by jenis_barang_id
            tbl_jns_brg = jenis_barang_models.JenisBarang
            query_jns_brg = select(tbl_jns_brg).filter(tbl_jns_brg.id==jsonable_encoder(result[0].jenis_barang_id))

            logger.info(query_jns_brg)
            # execute query
            proxy_rows_query_jns_brg = await session.execute(query_jns_brg)
            # parse result as list of object
            result_jns_brg = proxy_rows_query_jns_brg.scalars().all()  # .scalars().first()
            # commit the db transaction
            await session.commit()
            # Test print jsonable_encoder barang
            # logger.info("jsonable_encoder(result_jns_brg) :",jsonable_encoder(result_jns_brg))

            # Menampilkan jenis barang dan stock
            list_barang = {
                "id": jsonable_encoder(result[0].id),
                "jenis_barang_id": jsonable_encoder(result[0].jenis_barang_id),
                "stock_barang_id" :jsonable_encoder(result_stock[0].id),
                "nama_barang": jsonable_encoder(result[0].nama_barang),
                "stock": jsonable_encoder(result_stock[0].stock),
                "jenis_barang" : jsonable_encoder(result_jns_brg[0].jenis_barang)
            }

        except gevent.Timeout:
            # database timeout
            await session.invalidate()
            # raise response to FASTAPI
            return ResponseOutCustom(message_id="02", status="Failed, DB transaction was timed out...",
                                     list_data=None)

        except SQLAlchemyError as e:
            logger.info(e)
            # rollback db if error
            await session.rollback()
            # raise response to FASTAPI
            return ResponseOutCustom(message_id="02", status="Failed, something wrong rollback DB transaction...",
                                     list_data=None)

        # result data handling
        if result:
            # success
            return ResponseOutCustom(message_id="00", status="Get Barang Data by ID success", list_data=list_barang)
        else:
            # data not found
            return ResponseOutCustom(message_id="01",
                                     status=f"Failed, Log Order with specified criteria not found...",
                                     list_data=None)