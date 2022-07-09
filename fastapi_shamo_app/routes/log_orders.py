from cmath import log
from fastapi import APIRouter, Response, Depends
from schemas.log_orders import LogOrders
from crud import log_orders_crud
from starlette import status
from utils.helpers import handle_error_code
from sqlalchemy.ext.asyncio.session import AsyncSession
from db import get_async_session

log_orders = APIRouter()

@log_orders.get(
    '/',
    summary="Get All Orders List",
    status_code=status.HTTP_200_OK
    )
async def fetch_orders(
    response : Response,
    db_session: AsyncSession = Depends(get_async_session)
    ):
    out_response = await log_orders_crud.fetch_orders(db_session=db_session)
    handle_error_code(out_response,response)
    return out_response

@log_orders.get(
    '/{id}',
    name="Get Order's Data by ID",
    status_code=status.HTTP_200_OK,
)
async def fetch_orders_by_criteria(
    id: int,
    tanggal_awal:str,
    tanggal_akhir:str,
    response:Response,
    db_session: AsyncSession = Depends(get_async_session)
    ):
    out_response = await log_orders_crud.fetch_orders_by_criteria(id=id,tanggal_awal=tanggal_awal,tanggal_akhir=tanggal_akhir,db_session=db_session)
    handle_error_code(out_response,response)
    return out_response

@log_orders.post(
    '/',
    summary="Add an order",
    status_code=status.HTTP_201_CREATED
    )
async def post_log_order(
    request: LogOrders,
    response:Response,
    db_session: AsyncSession = Depends(get_async_session)
    ):
    out_response = await log_orders_crud.post_log_order(request=request,db_session=db_session)
    handle_error_code(out_response,response)
    return out_response


@log_orders.put(
    '/{id}',  
    name="Update Order\'s Data",
    status_code=status.HTTP_200_OK,
    )
async def update_log_order(
    id: int, 
    request: LogOrders,
    response:Response,
    db_session: AsyncSession = Depends(get_async_session)
    ):
    out_response = await log_orders_crud.update_log_order(id=id, request=request, db_session=db_session )
    handle_error_code(out_response,response)
    return out_response

@log_orders.delete(
    '/{id}',
    name="Delete Order's Data by ID",
    status_code=status.HTTP_200_OK,
)
async def delete_log_order(
    id: int,
    response:Response,
    db_session: AsyncSession = Depends(get_async_session)
    ):
    out_response = await log_orders_crud.delete_log_order(id=id,db_session=db_session)
    handle_error_code(out_response,response)
    return out_response