from models.user import User
from repositories.otp import OTPRepository
from services.unit_of_work import UnitOfWork

import string
import secrets


class OTPService:

    def __init__(self, repository: OTPRepository, uow: UnitOfWork):
        self.repository = repository
        self.uow = uow


    @staticmethod
    def hashing_otp(
            hashing_string: str,
    ) -> bytes:
        salt = bcrypt.gensalt()
        pwd_bytes: bytes = hashing_string.encode()
        return bcrypt.hashpw(pwd_bytes, salt)

    async def generate_otp(self, ) -> str:

        return ""

    async def add_otp(self, user: User):

        otp = await self.generate_otp()

        data_otp = {
            "user_id": user.id,
            "otp_hash": await self.hashing_otp(otp),
        }

        await self.repository.add_one(self.uow.session, data_otp)

    async def verify(self, user: User, otp_code: str):
        pass

