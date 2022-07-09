import email
import json
from unicodedata import name
from schemas.stocks_schema import Stocks
from schemas.transaksi_scheme import Transaksi
from schemas.user import Users
from models import stocks_models, transaksi_models, user_models
from services.core_scheme import ResponseOutCustom
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import func, text, update
from sqlalchemy.exc import SQLAlchemyError
import gevent
from fastapi.logger import logger
from fastapi.encoders import jsonable_encoder
from datetime import datetime


async def fetch_transaksi(db_session :AsyncSession) -> ResponseOutCustom:
    async with db_session as session:
        try :
            tbl_trs = transaksi_models.Transaksi
            
            query_fetch_transaksi = select(tbl_trs).\
                order_by(tbl_trs.nama_barang.asc(),tbl_trs.tanggal_transaksi.desc())
            logger.info(query_fetch_transaksi)

            proxy_rows = await session.execute(query_fetch_transaksi)
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
            return ResponseOutCustom(message_id="00", status="Fetch All Data Transaksi Success", list_data=result)
        else:
            # data not found
            return ResponseOutCustom(
                message_id="01",
                status=f"Failed, Users not found...",
                list_data=[],
            )
# 3.	Buatlah backend & frontend dengan adanya fitur searching dan 
#       bisa mengurutkan data berdasarkan nama barang, tanggal transaksi
async def fetch_transaksi_by_tanggal(tanggal_awal:str, tanggal_akhir:str, db_session :AsyncSession) -> ResponseOutCustom:
    async with db_session as session:
        try :
            tbl_trs = transaksi_models.Transaksi
            
            # # Define criterias list
            filter_criterias = []

            #Conditional append criterias to filter_criterias
            if tanggal_awal != "" and tanggal_awal is not None and tanggal_akhir != "" and tanggal_akhir is not None:
                if len(tanggal_awal) and len(tanggal_akhir) > 10:
                    start = datetime.strptime(tanggal_awal, "%Y-%m-%dT%H:%M:%S")
                    end = datetime.strptime(tanggal_akhir, "%Y-%m-%dT%H:%M:%S")
                    filter_criterias.append(tbl_trs.tanggal_transaksi.between(start,end))
                if len(tanggal_awal) and len(tanggal_akhir) <= 10:
                    start = datetime.strptime(tanggal_awal, "%Y-%m-%d")
                    end = datetime.strptime(tanggal_akhir, "%Y-%m-%d")
                    filter_criterias.append(tbl_trs.tanggal_transaksi.between(start,end))

            query_fetch_transaksi = select(tbl_trs).\
                filter(*[f for f in filter_criterias]).\
                order_by(tbl_trs.nama_barang.asc(),tbl_trs.tanggal_transaksi.desc())
            logger.info(query_fetch_transaksi)

            proxy_rows = await session.execute(query_fetch_transaksi)
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
            return ResponseOutCustom(message_id="00", status="Fetch All Data Transaksi by tanggal Success", list_data=result)
        else:
            # data not found
            return ResponseOutCustom(
                message_id="01",
                status=f"Failed, Users not found...",
                list_data=[],
            )

async def post_transaksi(request: Transaksi, db_session: AsyncSession) -> ResponseOutCustom:
    
    async with db_session as session:
        try:
            # Jumlah order tidak boleh nol atau negatif 
            if request.jumlah_terjual < 1:
                return ResponseOutCustom(
                    message_id="01",
                    status=f"Failed, silahkan lakukan order setidak-tidaknya sejumlah 1 buah",
                    list_data=[],
                )
            # cek jumlah stock
            tbl_stk = stocks_models.Stocks

            query_stock = select(tbl_stk).filter(
                tbl_stk.id == request.stocks_id
            )

            logger.info(query_stock)
            # execute query
            proxy_rows = await session.execute(query_stock)
            # parse result as list of object
            result_stock = proxy_rows.scalars().all()  # .scalars().first()
            # commit the db transaction
            await session.commit()
            # Encode from json untuk jumlah stock dan nama_barang dari table stocks
            jumlah_stock = jsonable_encoder(result_stock[0].stock)
            
            #Cek stok
            if jumlah_stock == 0:
                # Stock kosong
                return ResponseOutCustom(message_id="01",
                                        status=f"Failed, Stock kosong...",
                                        list_data=[])
            # Cek kesesuaian jumlah order dengan jumlah stock saat ini
            if (jumlah_stock - request.jumlah_terjual) < 0:
                return ResponseOutCustom(
                    message_id="01",
                    status=f"Failed, Invalid operation jumlah order melebihi jumlah stock saat ini",
                    list_data=[],
                )

            nama_barang = jsonable_encoder(result_stock[0].nama_barang)

            new_transaksi = transaksi_models.Transaksi(
                stocks_id = request.stocks_id,
                barang_id = request.barang_id,
                jenis_barang_id = request.jenis_barang_id,
                nama_barang = nama_barang,
                stock = jumlah_stock,
                jumlah_terjual = request.jumlah_terjual,
                jenis_barang = request.jenis_barang,
            )
            session.add(new_transaksi)
            await session.commit()
            await session.refresh(new_transaksi)
            logger.info("Mencoba menambahkan data transaksi")
            #update stocks
            logger.info("Update Stock dari Transaksi yang terjadi")

             # PUT : update table from database with query and async session
            # select query
            stk_tbl = stocks_models.Stocks
            query_stck_updt = select(stk_tbl).where(
                stk_tbl.id == request.stocks_id
            )
            logger.info(query_stck_updt)
            # execute query
            proxy_row_query_stck_updt = await session.execute(query_stck_updt)
            # parse result as list of object
            result_updt_stocks = proxy_row_query_stck_updt.scalars().first()

            # first check
            if not result_updt_stocks:
                return ResponseOutCustom(
                    message_id="01",
                    status=f"Failed, data with id:{id} not found...",
                    list_data=[],
                )
            if (jumlah_stock - request.jumlah_terjual) < 0:
                return ResponseOutCustom(
                    message_id="01",
                    status=f"Failed, Invalid operation jumlah order melebihi jumlah stock saat ini",
                    list_data=[],
                )

            # update query
            update_stocks_data = (
                update(stk_tbl)
                .where(stk_tbl.id==request.stocks_id)
                .values(
                    stock = (jumlah_stock - request.jumlah_terjual)
                )
            )

            # execute query
            await session.execute(update_stocks_data)
            await session.commit()
            # get new data
            await session.refresh(result_updt_stocks)
            
            list_regis_transaksi = [{
                "stocks_id" : request.stocks_id,
                "barang_id" : request.barang_id,
                "jenis_barang_id" : request.jenis_barang_id,
                "nama_barang" : nama_barang,
                "stock" : jumlah_stock,
                "jumlah_terjual" : request.jumlah_terjual,
                "jenis_barang" : request.jenis_barang,
            }]

            return ResponseOutCustom(message_id="00", status="Registrasi Transaksi Berhasil", list_data=list_regis_transaksi)
        
        except gevent.Timeout:
            # database timeout
            await session.invalidate()
            return ResponseOutCustom(message_id="02", status="Failed on " + transaksi_models.Transaksi.__tablename__ + ", DB transaction was timed out...",
                                     list_data=None)

        except SQLAlchemyError as e:
            logger.error(e)
            # rollback db if error
            await session.rollback()
            return ResponseOutCustom(message_id="02", status="Failed on " + transaksi_models.Transaksi.__tablename__  + ", something wrong rollback DB transaction...",
                                     list_data={'msg': str(e)})

# 4.	Buatlah backend & frontend untuk membandingkan jenis barang dengan 
#       menampilkan data transaksi terbanyak terjual atau terendah

# 5.	Buatlah filter terhadap soal 4 untuk memilih rentang waktu tertentu
async def fetch_jenis_barang_transaksi_by_criteria(tanggal_awal:str,tanggal_akhir:str, db_session :AsyncSession) -> ResponseOutCustom:
    async with db_session as session:
        try:
            #  # Define var for Transaksi table
            tbl_trs = transaksi_models.Transaksi
            # # Define criterias list
            filter_criterias = []

            #Conditional append criterias to filter_criterias
            if tanggal_awal != "" and tanggal_awal is not None and tanggal_akhir != "" and tanggal_akhir is not None:
                if len(tanggal_awal) and len(tanggal_akhir) > 10:
                    start = datetime.strptime(tanggal_awal, "%Y-%m-%dT%H:%M:%S")
                    end = datetime.strptime(tanggal_akhir, "%Y-%m-%dT%H:%M:%S")
                    filter_criterias.append(tbl_trs.tanggal_transaksi.between(start,end))
                if len(tanggal_awal) and len(tanggal_akhir) <= 10:
                    start = datetime.strptime(tanggal_awal, "%Y-%m-%d")
                    end = datetime.strptime(tanggal_akhir, "%Y-%m-%d")
                    filter_criterias.append(tbl_trs.tanggal_transaksi.between(start,end))

            # Select by criterias raw sql
            query_stmt = text(f"""select  t.jenis_barang, sum(t.jumlah_terjual) as total_terjual from transaksi t 
                        where t.tanggal_transaksi between '{start}' and '{end}'
                        group by t.jenis_barang
                        order by total_terjual desc ;""")

            logger.info(query_stmt)
            # execute query
            proxy_rows = await session.execute(query_stmt)
            # parse result as list of object
            result = proxy_rows.fetchall()# .scalars().all()
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
            return ResponseOutCustom(message_id="00", status="Get Transaksi data by tanggal transaksi success", list_data=result)
        else:
            # data not found
            return ResponseOutCustom(message_id="01",
                                     status=f"Failed, Transaksi with specified criteria not found...",
                                     list_data=[])






# async def update_stocks_from_transaksi(id: int, stock_from_transaksi: int, db_session: AsyncSession) -> ResponseOutCustom:
#     async with db_session as session:
#         try:
#             # PUT : update table from database with query and async session
#             # select query
#             stk_tbl = stocks_models.Stocks
#             query_stmt = select(stk_tbl).where(
#                 stk_tbl.id == id
#             )
#             logger.info(query_stmt)
#             # execute query
#             proxy_row = await session.execute(query_stmt)
#             # parse result as list of object
#             result = proxy_row.scalars().first()

#             # first check
#             if not result:
#                 return ResponseOutCustom(
#                     message_id="01",
#                     status=f"Failed, data with id:{id} not found...",
#                     list_data=result,
#                 )

#             # update query
#             update_stocks_data = (
#                 update(stk_tbl)
#                 .where(stk_tbl.id==id)
#                 .values(
#                     stock = stock_from_transaksi
#                 )
#             )

#             # execute query
#             await session.execute(update_stocks_data)
#             await session.commit()
#             # get new data
#             await session.refresh(result)

#             # return the result as custom response
#             return ResponseOutCustom(
#                 message_id="00",
#                 status="Update Stock dari Transaksi Success",
#                 list_data=result,
#             )

#         except gevent.Timeout:
#             # database timeout
#             await session.invalidate()
#             # raise response to FASTAPI
#             return ResponseOutCustom(
#                 message_id="02",
#                 status="Failed, DB transaction was timed out...",
#                 list_data=None,
#             )

#         except SQLAlchemyError as e:
#             logger.info(e)
#             # rollback db if error
#             await session.rollback()
#             # raise response to FASTAPI
#             return ResponseOutCustom(
#                 message_id="02",
#                 status="Failed, something wrong rollback DB transaction...",
#                 list_data=None,
#             )

# async def delete_user(id: int, db_session:AsyncSession) -> ResponseOutCustom:
#     async with db_session as session:
#         try:
#             query_stmt = select(user_models.Users).where(
#                 user_models.Users.id == id
#             )
#             proxy_rows = await session.execute(query_stmt)

#             # parse result as list of object
#             result = proxy_rows.scalars().all()

#             if not result:
#                 return ResponseOutCustom(
#                     message_id="01",
#                     status=f"Failed, Product Code with id:{id} not found...",
#                     list_data=result,
#                 )

#             await session.delete(result[0])

#             await session.commit()

#             return ResponseOutCustom(
#                 message_id="00",
#                 status=f"success",
#                 list_data=None,
#             )

#         except gevent.Timeout:
#             # database timeout
#             await session.invalidate()
#             return ResponseOutCustom(
#                 message_id="02",
#                 status="Failed, DB transaction was timed out...",
#                 list_data=None,
#             )

#         except SQLAlchemyError as e:
#             logger.error(e)
#             # rollback db if error
#             await session.rollback()
#             return ResponseOutCustom(
#                 message_id="02",
#                 status="Failed, something wrong rollback DB transaction...",
#                 list_data=result,
#             )