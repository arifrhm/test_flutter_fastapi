from typing import Optional
from fastapi import APIRouter, Response, Depends
from schemas.transaksi_scheme import Transaksi
from schemas.user import Users
from crud import transaksi_crud, users_crud
from starlette import status
from utils.helpers import handle_error_code
from sqlalchemy.ext.asyncio.session import AsyncSession
from db import get_async_session

transaksi = APIRouter()

@transaksi.get(
    '/',
    summary="Get All Transaksi List",
    status_code=status.HTTP_200_OK
    )
async def fetch_transaksi(
    response : Response,
    db_session: AsyncSession = Depends(get_async_session)
    ):
    out_response = await transaksi_crud.fetch_transaksi(db_session=db_session)
    handle_error_code(out_response,response)
    return out_response

@transaksi.get(
    '/tanggal',
    name="Get Data Transaksi by tanggal transaksi",
    status_code=status.HTTP_200_OK,
)
async def fetch_transaksi_by_tanggal(
    tanggal_awal:str,
    tanggal_akhir:str,
    response:Response,
    db_session: AsyncSession = Depends(get_async_session)
    ):
    out_response = await transaksi_crud.fetch_transaksi_by_tanggal(tanggal_awal=tanggal_awal,tanggal_akhir=tanggal_akhir,db_session=db_session)
    handle_error_code(out_response,response)
    return out_response

@transaksi.get(
    '/jenis-barang-terbanyak',
    name="Get Jenis Barang Terbanyak Data by tanggal transaksi",
    status_code=status.HTTP_200_OK,
)
async def fetch_jenis_barang_transaksi_by_criteria(
    tanggal_awal:str,
    tanggal_akhir:str,
    response:Response,
    db_session: AsyncSession = Depends(get_async_session)
    ):
    out_response = await transaksi_crud.fetch_jenis_barang_transaksi_by_criteria(tanggal_awal=tanggal_awal,tanggal_akhir=tanggal_akhir,db_session=db_session)
    handle_error_code(out_response,response)
    return out_response

# @transaksi.get(
#     '/{id}',
#     name="Get Order's Data by ID",
#     status_code=status.HTTP_200_OK,
# )
# async def fetch_transaksi_by_criteria(
#     id: int,
#     response:Response,
#     tanggal_awal:Optional[str]=None,
#     tanggal_akhir:Optional[str]=None,
#     db_session: AsyncSession = Depends(get_async_session)
#     ):
#     out_response = await transaksi_crud.fetch_transaksi_by_criteria(id=id,tanggal_awal=tanggal_awal,tanggal_akhir=tanggal_akhir,db_session=db_session)
#     handle_error_code(out_response,response)
#     return out_response

@transaksi.post(
    '/',
    summary="Add a Transaksi",
    status_code=status.HTTP_201_CREATED
    )
async def post_transaksi(
    request: Transaksi,
    response:Response,
    db_session: AsyncSession = Depends(get_async_session)
    ):
    out_response = await transaksi_crud.post_transaksi(request=request,db_session=db_session)
    handle_error_code(out_response,response)
    return out_response



# @transaksi.put(
#     '/{id}',
#     name="Update Transaksi's Data",
#     status_code=status.HTTP_200_OK,
#     )
# async def update_transaksi(
#     id: int, 
#     request: Users,
#     response:Response,
#     db_session: AsyncSession = Depends(get_async_session)
#     ):
#     out_response = await transaksi_crud(id=id, request=request, db_session=db_session )
#     handle_error_code(out_response,response)
#     return out_response

# @transaksi.delete(
#     '/{id}',
#     name="Delete Transaksi's Data by ID",
#     status_code=status.HTTP_200_OK,
# )
# async def delete_transaksi(
#     id: int,
#     response:Response,
#     db_session: AsyncSession = Depends(get_async_session)
#     ):
#     out_response = await transaksi_crud.delete_user(id=id,db_session=db_session)
#     handle_error_code(out_response,response)
#     return out_response