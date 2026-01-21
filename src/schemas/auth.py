from pydantic import BaseModel, EmailStr


class UserCreate(BaseModel):
    email: EmailStr
    password: str
    password_repeat: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str
