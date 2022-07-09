import email
from unicodedata import name
from schemas.user import Users
from models import user_models
from services.core_scheme import ResponseOutCustom
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import update
from sqlalchemy.exc import SQLAlchemyError
import gevent
from fastapi.logger import logger

async def fetch_users(db_session :AsyncSession) -> ResponseOutCustom:
    async with db_session as session:
        try :
            query_fetch_users = select(user_models.Users)
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

async def post_user(request: Users, db_session: AsyncSession) -> ResponseOutCustom:
    new_user_registration = user_models.Users(
        name = request.name,
        email = request.email,
        password = request.password
    )
    async with db_session as session:
        try:
            session.add(new_user_registration)
            await session.commit()
            await session.refresh(new_user_registration)

            return ResponseOutCustom(message_id="00", status="Registrasi User Berhasil", list_data=request)
        except gevent.Timeout:
            # database timeout
            await session.invalidate()
            return ResponseOutCustom(message_id="02", status="Failed on " + user_models.Users.__tablename__ + ", DB transaction was timed out...",
                                     list_data=None)

        except SQLAlchemyError as e:
            logger.error(e)
            # rollback db if error
            await session.rollback()
            return ResponseOutCustom(message_id="02", status="Failed on " + user_models.Users.__tablename__  + ", something wrong rollback DB transaction...",
                                     list_data={'msg': str(e)})

        
async def update_user(id: int, request: Users, db_session: AsyncSession) -> ResponseOutCustom:
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
                    name=request.name,
                    email=request.email,
                    password=request.password,
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

async def delete_user(id: int, db_session:AsyncSession) -> ResponseOutCustom:
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
                    status=f"Failed, Product Code with id:{id} not found...",
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