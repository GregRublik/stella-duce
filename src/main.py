from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
import uvicorn

from config import settings

from api.v1.endpoints import auth, goal, goal_stage, web
from exceptions import APIException, DatabaseUnavailableException
from exception_handlers import api_exception_handler, db_handler


app = FastAPI()

app.include_router(web.router)
app.include_router(auth.router, prefix="/auth")
app.include_router(goal.router, prefix="/editor")
app.include_router(goal_stage.router, prefix="/editor")

app.mount("/static", StaticFiles(directory="src/static"), name="static")


app.add_exception_handler(APIException, api_exception_handler)
app.add_exception_handler(DatabaseUnavailableException, db_handler)

if __name__ == "__main__":
    uvicorn.run(
        app,
        host=settings.host,
        port=settings.port
    )
