from pydantic import BaseModel,Field,EmailStr

class AuthRequest(BaseModel):
    email: EmailStr
    password: str

class AuthResponse(BaseModel):
    message: str
    token: str
    refresh_token: str
    token_type: str

class RefreshTokenRequest(BaseModel):
    refresh_token: str        
    
class RefreshTokenResponse(BaseModel):
    access_token: str
    token_type: str