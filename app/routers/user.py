from typing import List
from fastapi import APIRouter, Depends
from uuid import UUID
from starlette import status
from sqlalchemy.orm import Session

from services.exception import AccessDeniedError, ResourceNotFoundError
from database import get_db_context
from schemas.user import User
from models.user import UserModel, UserViewModel, UserBaseModel
from services import auth as AuthService
from services import user as UserService

router = APIRouter(prefix="/users", tags=["Users"])

@router.get("", status_code=status.HTTP_200_OK, response_model=List[UserViewModel])
async def get_users(db: Session = Depends(get_db_context)) -> List[UserViewModel]:
    return db.query(User).filter(User.is_active == True).all()

@router.get("/{user_id}", status_code=status.HTTP_200_OK, response_model=UserViewModel)
async def get_user_by_id(
    user_id: UUID,
    db: Session = Depends(get_db_context),
    loggedInUser: User = Depends(AuthService.token_interceptor)): 
      
    if not loggedInUser.is_admin:
        raise AccessDeniedError()
    
    user = UserService.get_user_by_id(db, user_id)

    if user is None:
        raise ResourceNotFoundError()

    return user


@router.post("", status_code=status.HTTP_201_CREATED, response_model=UserViewModel)
async def create_user(
    request: UserModel,
    db: Session = Depends(get_db_context),
    user: User = Depends(AuthService.token_interceptor)):
    
    if not user.is_admin:
        raise AccessDeniedError()
    
    return UserService.add_new_user(db, request)


@router.put("/{user_id}", status_code=status.HTTP_200_OK, response_model=UserViewModel)
async def update_user(
    user_id: UUID,
    request: UserModel,
    db: Session = Depends(get_db_context),
    user: User = Depends(AuthService.token_interceptor)
    ):
    
    if not user.is_admin:
        raise AccessDeniedError()
    
    return UserService.update_user(db, user_id, request)


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    user_id: UUID,
    db: Session = Depends(get_db_context),
    user: User = Depends(AuthService.token_interceptor)
    ):
    
    if not user.is_admin:
        raise AccessDeniedError()
    
    UserService.delete_user(db, user_id)