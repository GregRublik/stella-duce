from pydantic import BaseModel, EmailStr, field_validator
from pydantic_extra_types.phone_numbers import PhoneNumber
from typing import Literal
import re

class UserEmail(BaseModel):
    email: EmailStr

class UserPhone(BaseModel):
    phone: PhoneNumber

class UserCreate(UserEmail):
    password: str | bytes

    @field_validator('password')
    def validate_password(cls, v):
        if isinstance(v, bytes):
            password = v.decode('utf-8')
        else:
            password = v

        errors = []

        # Проверка минимальной длины
        if len(password) < 8:
            errors.append("password length must be at least 8 characters")

        # Проверка наличия заглавных букв
        if not re.search(r'[A-ZА-Я]', password):
            errors.append("password must contain at least one capital letter")

        # Проверка наличия строчных букв
        if not re.search(r'[a-zа-я]', password):
            errors.append("password must contain at least one lowercase letter")

        # Проверка наличия цифр
        if not re.search(r'\d', password):
            errors.append("password must contain at least one digit")

        if errors:
            raise ValueError("; ".join(errors))

        return v

class UserLogin(UserEmail):
    password: str

class UserLoginOtp(UserEmail):
    pass

class UserVerifyEmailOtp(UserEmail):
    otp_code: str
    type: Literal["email", "sms"]

class UserVerifySmsOtp(UserPhone):
    otp_code: str
    type: Literal["email", "sms"]
