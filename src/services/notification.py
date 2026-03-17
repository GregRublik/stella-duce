from fastapi_mail import FastMail, MessageSchema, ConnectionConfig
from pydantic import SecretStr, EmailStr


class NotificationService:

    def __init__(
            self,
            mail_username: str,
            mail_password: SecretStr,
            mail_from: EmailStr,
            mail_port: int,
            mail_server: str,
    ):
        self.conf = ConnectionConfig(
            MAIL_USERNAME=mail_username,
            MAIL_PASSWORD=mail_password,
            MAIL_FROM=mail_from,
            MAIL_PORT=mail_port,
            MAIL_SERVER=mail_server,
            MAIL_STARTTLS=False,
            MAIL_SSL_TLS=True
        )
        self.fm = FastMail(self.conf)

    async def send_email_notification(
            self,
            message: MessageSchema,
    ):
        await self.fm.send_message(message)


    async def send_sms_notification(self):
        pass
