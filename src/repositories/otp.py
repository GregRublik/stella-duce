from repositories.base import SQLAlchemyRepository
from models.otp import OtpCode


class OTPRepository(SQLAlchemyRepository):
    model = OtpCode

