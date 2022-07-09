from datetime import datetime
from distutils import log
from schemas.log_orders import LogOrders
from models import log_order_models, user_models
from services.core_scheme import ResponseOutCustom
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import update
from sqlalchemy.exc import SQLAlchemyError
import gevent
from fastapi.logger import logger

async def fetch_orders(db_session :AsyncSession) -> ResponseOutCustom:
    async with db_session as session:
        try :
            query_fetch_users = select(log_order_models.LogOrders)
            logger.info(query_fetch_users)

            proxy_rows = await session.execute(query_fetch_users)
            # parse result as list of object
            result = proxy_rows.scalars().all()
            # commit the db transaction
            await session.commit()

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
            return ResponseOutCustom(message_id="00", status="Success", list_data=result)
        else:
            # data not found
            return ResponseOutCustom(
                message_id="01",
                status=f"Failed, Users not found...",
                list_data=[],
            )

async def fetch_orders_by_criteria(id: int,tanggal_awal:str,tanggal_akhir:str, db_session :AsyncSession) -> ResponseOutCustom:
    async with db_session as session:
        try:
            if tanggal_awal != "" and tanggal_awal is not None and tanggal_akhir != "" and tanggal_akhir is not None:
                if len(tanggal_awal) and len(tanggal_akhir) > 10:
                    start = datetime.strptime(tanggal_awal, "%Y-%m-%dT%H:%M:%S")
                    end = datetime.strptime(tanggal_akhir, "%Y-%m-%dT%H:%M:%S")
                if len(tanggal_awal) and len(tanggal_akhir) <= 10:
                    start = datetime.strptime(tanggal_awal, "%Y-%m-%d")
                    end = datetime.strptime(tanggal_akhir, "%Y-%m-%d")
            lom = log_order_models.LogOrders
            query_stmt = select(lom).filter(
                lom.id == id,
                lom.tanggal_transaksi.between(start,end)
            ).order_by(lom.tanggal_transaksi.desc())

            logger.info(query_stmt)
            # execute query
            proxy_rows = await session.execute(query_stmt)
            # parse result as list of object
            result = proxy_rows.scalars().all()  # .scalars().first()
            # commit the db transaction
            await session.commit()

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
            return ResponseOutCustom(message_id="00", status="Get Log Order\'s data by ID success", list_data=result)
        else:
            # data not found
            return ResponseOutCustom(message_id="01",
                                     status=f"Failed, Log Order with specified criteria not found...",
                                     list_data=None)

async def post_log_order(request: LogOrders, db_session: AsyncSession) -> ResponseOutCustom:
    new_log_orders = log_order_models.LogOrders(
        nama_barang= request.nama_barang,
        stok =request.stok,    
        jumlah_terjual = request.jumlah_terjual,
        jenis_barang = request.jenis_barang
    )
    async with db_session as session:
        try:
            session.add(new_log_orders)
            await session.commit()
            await session.refresh(new_log_orders)

            return ResponseOutCustom(message_id="00", status="Insert Log Order Berhasil", list_data=request)
        except gevent.Timeout:
            # database timeout
            await session.invalidate()
            return ResponseOutCustom(message_id="02", status="Failed on " + log_order_models.LogOrders.__tablename__ + ", DB transaction was timed out...",
                                     list_data=None)

        except SQLAlchemyError as e:
            logger.error(e)
            # rollback db if error
            await session.rollback()
            return ResponseOutCustom(message_id="02", status="Failed on " + log_order_models.LogOrders.__tablename__  + ", something wrong rollback DB transaction...",
                                     list_data={'msg': str(e)})

        
async def update_transactions(id: int, request: LogOrders, db_session: AsyncSession) -> ResponseOutCustom:
    async with db_session as session:
        try:
            # PUT : update table from database with query and async session
            # select query
            query_stmt = select(user_models.Users).where(
                user_models.Users.id == id
            )
            logger.info(query_stmt)
            # execute query
            proxy_row = await session.execute(query_stmt)
            # parse result as list of object
            result = proxy_row.scalars().first()

            # first check
            if not result:
                return ResponseOutCustom(
                    message_id="01",
                    status=f"Failed, data with id:{id} not found...",
                    list_data=result,
                )

            # update query
            update_users_data = (
                update(user_models.Users)
                .where(user_models.Users)
                .values(
                    nama_barang= request.nama_barang,
                    stok =request.stok,    
                    jumlah_terjual = request.jumlah_terjual,
                    jenis_barang = request.jenis_barang
                )
            )

            # execute query
            await session.execute(update_users_data)
            await session.commit()
            # get new data
            await session.refresh(result)

            # return the result as custom response
            return ResponseOutCustom(
                message_id="00",
                status="Success",
                list_data=result,
            )

        except gevent.Timeout:
            # database timeout
            await session.invalidate()
            # raise response to FASTAPI
            return ResponseOutCustom(
                message_id="02",
                status="Failed, DB transaction was timed out...",
                list_data=None,
            )

        except SQLAlchemyError as e:
            logger.info(e)
            # rollback db if error
            await session.rollback()
            # raise response to FASTAPI
            return ResponseOutCustom(
                message_id="02",
                status="Failed, something wrong rollback DB transaction...",
                list_data=None,
            )

async def delete_log_order(id: int, db_session:AsyncSession) -> ResponseOutCustom:
    async with db_session as session:
        try:
            query_stmt = select(user_models.Users).where(
                user_models.Users.id == id
            )
            proxy_rows = await session.execute(query_stmt)

            # parse result as list of object
            result = proxy_rows.scalars().all()

            if not result:
                return ResponseOutCustom(
                    message_id="01",
                    status=f"Failed, Log Order with id:{id} not found...",
                    list_data=result,
                )

            await session.delete(result[0])

            await session.commit()

            return ResponseOutCustom(
                message_id="00",
                status=f"success",
                list_data=None,
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
                list_data=result,
            )