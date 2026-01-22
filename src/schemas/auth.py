from pydantic import BaseModel, EmailStr, field_validator
import re


class UserCreate(BaseModel):
    email: EmailStr
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

class UserLogin(BaseModel):
    email: EmailStr
    password: str
