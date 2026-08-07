from pydantic import BaseModel,Field,EmailStr


class RegistrationRequest(BaseModel):
    name: str = Field(min_length=3, max_length=100)
    email: EmailStr
    mobile: str = Field(min_length=10, max_length=10)
    password: str

#model is
class RegistrationResponseget(BaseModel):
    id: int
    name: str
    email: str
    mobile: str
    photo: str | None = None
    

class RegistrationResponse(BaseModel):
    message: str
    id: int