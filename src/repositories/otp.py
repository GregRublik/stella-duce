from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import NoResultFound
from sqlalchemy import select, update

from repositories.base import SQLAlchemyRepository
from models.otp import OtpCode, OtpType

from exceptions import OtpCodeNoFoundException


class OTPRepository(SQLAlchemyRepository):
    model = OtpCode

    async def get_by_user_id(self, session: AsyncSession, user_id: int) -> OtpCode:
        stmt = (
            select(self.model)
            .where(self.model.user_id == user_id)
            .limit(1)
        )
        try:
            res = await session.execute(stmt)
            return res.scalar_one()
        except NoResultFound:
            raise OtpCodeNoFoundException


    async def get_active_by_user_id(self, session, user_id: int, otp_type: OtpType):
        stmt = (
            select(self.model)
            .where(
                self.model.user_id == user_id,
                self.model.type == otp_type,
                self.model.used == False
            )
            .order_by(self.model.created_at.desc())
            .limit(1)
        )
        res = await session.execute(stmt)
        return res.scalar_one_or_none()

    async def deactivate_old_otps(self, session, user_id: int, otp_type: OtpType): # noqa
        stmt = (
            update(self.model)
            .where(
                self.model.user_id == user_id,
                self.model.type == otp_type,
                self.model.used == False
            )
            .values(used=True)
        )
        await session.execute(stmt)
