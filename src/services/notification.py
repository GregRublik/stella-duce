from typing import Literal

from models.user import User


class NotificationService:

    async def send_notification(
            self,
            subject: User,
            message: str,
            type_notification: Literal["email", "sms"] = "email",
    ):
        pass
