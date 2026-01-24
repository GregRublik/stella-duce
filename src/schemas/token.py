from pydantic import BaseModel
from pydantic import UUID4


class TokenUserCreate(BaseModel):
    id: str
    user_id: int
    token_hash: bytes

class TokenUserUpdate(BaseModel):
    id: str
    token_hash: str
    is_active: bool
