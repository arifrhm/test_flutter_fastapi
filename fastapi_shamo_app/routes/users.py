from fastapi import APIRouter, Response, Depends
from schemas.user import Users
from crud import users_crud
from starlette import status
from utils.helpers import handle_error_code
from sqlalchemy.ext.asyncio.session import AsyncSession
from db import get_async_session

user = APIRouter()

@user.get(
    '/',
    summary="Get All Users List",
    status_code=status.HTTP_200_OK
    )
async def fetch_users(
    response : Response,
    db_session: AsyncSession = Depends(get_async_session)
    ):
    out_response = await users_crud.fetch_users(db_session=db_session)
    handle_error_code(out_response,response)
    return out_response


@user.post(
    '/',
    summary="Add a user",
    status_code=status.HTTP_201_CREATED
    )
async def post_user(
    request: Users,
    response:Response,
    db_session: AsyncSession = Depends(get_async_session)
    ):
    out_response = await users_crud.post_user(request=request,db_session=db_session)
    handle_error_code(out_response,response)
    return out_response


@user.put(
    '/{id}',
    name="Update User's Data",
    status_code=status.HTTP_200_OK,
    )
async def update_user(
    id: int, 
    request: Users,
    response:Response,
    db_session: AsyncSession = Depends(get_async_session)
    ):
    out_response = await users_crud.update_user(id=id, request=request, db_session=db_session )
    handle_error_code(out_response,response)
    return out_response

@user.delete(
    '/{id}',
    name="Delete User's Data by ID",
    status_code=status.HTTP_200_OK,
)
async def delete_user(
    id: int,
    response:Response,
    db_session: AsyncSession = Depends(get_async_session)
    ):
    out_response = await users_crud.delete_user(id=id,db_session=db_session)
    handle_error_code(out_response,response)
    return out_response