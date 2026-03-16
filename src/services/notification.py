from typing import Literal


class NotificationService:

    async def send_notification(self, subject, type_notification: Literal["email", "sms"] = "email", ):
        pass

    async def send_otp_notification(self, subject, otp: int, type_notification: Literal["email", "sms"] = "email"):
        pass



