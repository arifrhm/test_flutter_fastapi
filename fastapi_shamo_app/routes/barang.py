from fastapi import APIRouter, Response, Depends
from crud import barang_crud
from starlette import status
from utils.helpers import handle_error_code
from sqlalchemy.ext.asyncio.session import AsyncSession
from db import get_async_session

barang = APIRouter()

@barang.get(
    '/',
    summary="Get All Barang List",
    status_code=status.HTTP_200_OK
    )
async def fetch_barang(
    response : Response,
    db_session: AsyncSession = Depends(get_async_session)
    ):
    out_response = await barang_crud.fetch_barang(db_session=db_session)
    handle_error_code(out_response,response)
    return out_response

@barang.get(
    '/{id}',
    name="Get Barang's Data by ID",
    status_code=status.HTTP_200_OK,
)
async def fetch_barang_by_id(
    id: int,
    response:Response,
    db_session: AsyncSession = Depends(get_async_session)
    ):
    out_response = await barang_crud.fetch_barang_by_id(id=id,db_session=db_session)
    handle_error_code(out_response,response)
    return out_response

# @barang.post(
#     '/',
#     summary="Add a Barang",
#     status_code=status.HTTP_201_CREATED
#     )
# async def post_barang(
#     request: barang,
#     response:Response,
#     db_session: AsyncSession = Depends(get_async_session)
#     ):
#     out_response = await barang_crud.post_barang(request=request,db_session=db_session)
#     handle_error_code(out_response,response)
#     return out_response


# @barang.put(
#     '/{id}',
#     name="Update Barang's Data",
#     status_code=status.HTTP_200_OK,
#     )
# async def update_user(
#     id: int, 
#     request: Users,
#     response:Response,
#     db_session: AsyncSession = Depends(get_async_session)
#     ):
#     out_response = await users_crud.update_user(id=id, request=request, db_session=db_session )
#     handle_error_code(out_response,response)
#     return out_response

# @barang.delete(
#     '/{id}',
#     name="Delete Barang's Data by ID",
#     status_code=status.HTTP_200_OK,
# )
# async def delete_user(
#     id: int,
#     response:Response,
#     db_session: AsyncSession = Depends(get_async_session)
#     ):
#     out_response = await users_crud.delete_user(id=id,db_session=db_session)
#     handle_error_code(out_response,response)
#     return out_response