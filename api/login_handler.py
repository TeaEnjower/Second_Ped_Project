from fastapi import APIRouter, Depends, HTTPException, status, Response
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import timedelta

from api.models import Token, UserLogin
from db.dals import UserDAL
from db.session import get_db
from hashed import Hashed
from security import create_access_token
from settings import ACCESS_TOKEN_EXPIRE_MINUTES

login_router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")


async def authenticate_user(email: str, password: str, db: AsyncSession):
    user_dal = UserDAL(db)
    user = await user_dal.get_user_by_email(email)

    if not user:
        return False

    if not Hashed.verify_password(password, user.hashed_password):
        return False

    return user


@login_router.post("/login", response_model=Token)
async def login_for_access_token(
    response: Response,
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db),
):
    user = await authenticate_user(form_data.username, form_data.password, db)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email, "user_id": str(user.user_id)},
        expires_delta=access_token_expires,
    )

    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        secure=False,
        samesite="lax",
        max_age=access_token_expires.total_seconds(),
        expires=access_token_expires.total_seconds(),
        path="/",
    )

    response.set_cookie(
        key="user_id",
        value=str(user.user_id),
        httponly=False,
        secure=False,
        samesite="lax",
        max_age=access_token_expires.total_seconds(),
        path="/",
    )

    return {"access_token": access_token, "token_type": "bearer"}


@login_router.post("/login-form", response_model=Token)
async def login_user(
    response: Response, body: UserLogin, db: AsyncSession = Depends(get_db)
):
    user = await authenticate_user(body.email, body.password, db)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email, "user_id": str(user.user_id)},
        expires_delta=access_token_expires,
    )

    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        secure=False,
        samesite="lax",
        max_age=access_token_expires.total_seconds(),
        path="/",
    )

    response.set_cookie(
        key="user_id",
        value=str(user.user_id),
        httponly=False,
        secure=False,
        samesite="lax",
        max_age=access_token_expires.total_seconds(),
        path="/",
    )

    return {"access_token": access_token, "token_type": "bearer"}


@login_router.post("/logout")
async def logout_user(response: Response):
    """
    Удаление cookie с токеном
    """
    response.delete_cookie(key="access_token")
    response.delete_cookie(key="user_id")

    return {"message": "Logged out successfully"}
