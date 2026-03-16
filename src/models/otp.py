import enum
import uuid
from datetime import datetime, timezone

from sqlalchemy import Column, DateTime, ForeignKey, Enum, Integer, LargeBinary, UUID, Boolean
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from db.database import Base



class OtpType(enum.Enum):
    EMAIL_VERIFICATION = "email_verification"
    PASSWORD_RESET = "password_reset"
    LOGIN = "login"


class OtpCode(Base):
    __tablename__ = "otp_codes"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)

    otp_hash = Column(LargeBinary, nullable=False)

    type = Column(
        Enum(OtpType, name="otp_type"),
        nullable=False
    )

    attempts = Column(Integer, default=0, nullable=False)
    max_attempts = Column(Integer, default=5, nullable=False)

    used = Column(Boolean, default=False, nullable=False)

    created_at = Column(DateTime, server_default=func.now(), nullable=False)

    expires_at = Column(DateTime(timezone=True), nullable=False, index=True)

    user = relationship("User", backref="otp_codes")

    @property
    def is_expired(self) -> bool:
        return datetime.now(timezone.utc) >= self.expires_at
