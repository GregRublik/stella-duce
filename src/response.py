# core/response.py
from schemas.response import APIResponse

def ok(data):
    return APIResponse(success=True, data=data)
