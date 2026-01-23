# from typing import Union
#
# from sqlalchemy.exc import NoResultFound
# from sqlalchemy.ext.asyncio import AsyncSession
# import bcrypt
#
# from exceptions import TokenUserNoFoundException, TokenUserAlreadyExistsException, ModelAlreadyExistsException
# from models.user import TokenUser
# from repositories.base import SQLAlchemyRepository
# from repositories.token import TokenUserRepository
# from schemas.token import TokenUserCreate, TokenUserUpdate
#
#
# class TokenService:
#
#     def __init__(self, repository: Union[SQLAlchemyRepository, TokenUserRepository], session: AsyncSession):
#         self.repository = repository
#         self.session = session
#
#     @staticmethod
#     def hashing_token(
#             token: str,
#     ) -> bytes:
#         salt = bcrypt.gensalt()
#         pwd_bytes: bytes = token.encode()
#         return bcrypt.hashpw(pwd_bytes, salt)
#
#     async def validate_refresh_token(self, token: str, user_id: int) -> bool:
#         try:
#
#             token_db = await self.repository.get_by_user_id(self.session, user_id)
#             if token_db.token_hash == self.hashing_token(token):
#                 return True
#             return False
#
#         except TokenUserNoFoundException:
#             return False
#
#     async def add_token_user(self, token: TokenUserCreate) -> TokenUser:
#         try:
#             return await self.repository.add_one(self.session, token.model_dump())
#         except ModelAlreadyExistsException:
#             raise TokenUserAlreadyExistsException
#
#
#     async def update_by_id(self, token: TokenUserUpdate) -> TokenUser:
#         try:
#             return await self.repository.update_by_id(self.session, token)
#         except NoResultFound:
#             raise TokenUserNoFoundException
#
#
