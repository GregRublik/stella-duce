from datetime import datetime, timezone, timedelta

from models.user import User
from models.otp import OtpType
from repositories.otp import OTPRepository
from services.notification import NotificationService
from services.unit_of_work import UnitOfWork

from fastapi_mail import MessageSchema
from fastapi_mail.schemas import MessageType

import string
import secrets
import bcrypt
import asyncio


class OTPService:

    def __init__(self, repository: OTPRepository, uow: UnitOfWork, notification_service: NotificationService):
        self.notification_service = notification_service
        self.repository = repository
        self.uow = uow

    @staticmethod
    def _hashing_sync(hashing_string: str) -> bytes:
        salt = bcrypt.gensalt()
        pwd_bytes: bytes = hashing_string.encode()
        return bcrypt.hashpw(pwd_bytes, salt)

    async def hashing_otp(self, hashing_string: str) -> bytes:
        return await asyncio.to_thread(self._hashing_sync, hashing_string)

    @staticmethod
    def _verify_sync(otp: str, otp_hash: bytes) -> bool:
        return bcrypt.checkpw(otp.encode(), otp_hash)

    async def verify_hash(self, otp: str, otp_hash: bytes) -> bool:
        return await asyncio.to_thread(self._verify_sync, otp, otp_hash)

    @staticmethod
    async def generate_otp(length: int = 6) -> str:
        digits = string.digits
        return ''.join(secrets.choice(digits) for _ in range(length))

    async def add_otp(self, user: User, otp_type: OtpType = OtpType) -> str:

        # Деактивируем старые OTP для пользователя и типа
        await self.repository.deactivate_old_otps(self.uow.session, user.id, otp_type)

        # Генерируем новый OTP
        otp = await self.generate_otp()
        otp_hash = await self.hashing_otp(otp)

        data_otp = {
            "user_id": user.id,
            "otp_hash": otp_hash,
            "type": otp_type,
            "expires_at": datetime.now(timezone.utc) + timedelta(minutes=5)  # срок жизни OTP
        }

        await self.repository.add_one(self.uow.session, data_otp)
        return otp

    async def generate_and_send(self, user: User, otp_type: OtpType = OtpType.EMAIL_VERIFICATION):
        async with self.uow:
            new_otp = await self.add_otp(user, otp_type)

            print(new_otp)

            otp_message = MessageSchema(
                subject="Your OTP",
                recipients=[user.email],
                body=f"<b>Your OTP code: {new_otp}</b>",
                subtype=MessageType.plain
            )

            await self.notification_service.send_email_notification(otp_message)

    async def verify(self, user: User, otp_code: str) -> bool:

        otp_entity = await self.repository.get_by_user_id(
            self.uow.session,
            user.id
        )

        if not otp_entity:
            return False

        return await self.verify_hash(
            otp_code,
            otp_entity.otp_hash
        )
