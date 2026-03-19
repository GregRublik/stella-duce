from typing import Annotated

from fastapi import APIRouter, Request, Depends
from config import templates
from dependencies.user import get_current_user
from models.user import User

router = APIRouter(tags=["/web"])

@router.get("/",)
async def index(
        request: Request
):
    return templates.TemplateResponse(request, name="index.html")

@router.get("/register",)
async def register(
        request: Request
):
    return templates.TemplateResponse(request, name="register.html")

@router.get("/login",)
async def register(
        request: Request
):
    return templates.TemplateResponse(request, name="login.html")

@router.get("/otp")
async def otp(
    request: Request
):
    return templates.TemplateResponse(request, name="otp.html")

@router.get("/goals")
async def goals(
        request: Request,
        user: Annotated[User, Depends(get_current_user)],
):
    return templates.TemplateResponse(
        request,
        name="goals.html",
        context={"user": user}
    )

@router.get("/stages")
async def stages(
        request: Request,
        user: Annotated[User, Depends(get_current_user)],
):
    return templates.TemplateResponse(
        request,
        name="stages.html",
        context={"user": user}
    )