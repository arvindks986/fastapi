from fastapi import APIRouter, Depends,Response,Cookie
from sqlalchemy.orm import Session
from dbconnection import get_db
from models.registration import Registration
from security import hash_password,verify_password,rate_limit
from security import create_access_token, create_refresh_token
import jwt
import os
from dotenv import load_dotenv
load_dotenv()
from schemas.auth import (
    AuthRequest,
    AuthResponse
)
from schemas.auth import (
    RefreshTokenRequest,
    RefreshTokenResponse
)

router = APIRouter(
    prefix="/auth",
    tags=["Authentication"]
)

@router.post("/login", response_model=AuthResponse)
def login(auth_request: AuthRequest, db: Session = Depends(get_db), response: Response = None):
    user = db.query(Registration).filter(
        Registration.email == auth_request.email
    ).first()

    if not user:
        raise HTTPException(
            status_code=401,
            detail="Invalid email or password"
        )

    if not verify_password(auth_request.password, user.password):
        raise HTTPException(
            status_code=401,
            detail="Invalid email or password"
        )
         # 4. Create tokens
    access_token = create_access_token(user.id)
    refresh_token = create_refresh_token(user.id)
    #token = create_access_token({"sub": user.email})
    #token = "212dsdanbff1212"

     # Save refresh token in browser cookie
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        secure=True,       # False for local HTTP development
        samesite="lax",
        max_age=7 * 24 * 60 * 60
    )

    return AuthResponse(message="Login successful",
     token=access_token, 
     refresh_token=refresh_token,
     token_type="bearer"
     )

@router.post("/refresh", response_model=RefreshTokenResponse)
def refresh_token(
    refresh_token: str | None = Cookie(default=None)
):
    if not refresh_token:
        raise HTTPException(
            status_code=401,
            detail="Refresh token missing"
        )

    SECRET_KEY = os.getenv("SECRET_KEY")
    ALGORITHM = os.getenv("ALGORITHM")

    try:
        payload = jwt.decode(
            refresh_token,
            SECRET_KEY,
            algorithms=[ALGORITHM]
        )

        user_id = int(payload.get("sub"))

        new_access_token = create_access_token(user_id)

        return {
            "access_token": new_access_token,
            "token_type": "bearer"
        }

    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=401,
            detail="Refresh token expired"
        )

    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=401,
            detail="Invalid refresh token"
        )