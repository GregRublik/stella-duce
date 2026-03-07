from fastapi import FastAPI
import uvicorn
from config import settings
from api.v1.endpoints import auth, goal, goal_stage
from exceptions import APIException
from exception_handlers import api_exception_handler


app = FastAPI()

app.include_router(auth.router)
app.include_router(goal.router, prefix="/editor")
app.include_router(goal_stage.router, prefix="/editor")

app.add_exception_handler(APIException, api_exception_handler)

if __name__ == "__main__":
    uvicorn.run(
        app,
        host=settings.host,
        port=settings.port
    )
