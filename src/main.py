from fastapi import FastAPI
import uvicorn
from config import settings
from api.v1.endpoints import auth, goal


app = FastAPI()

app.include_router(auth.router)
app.include_router(goal.router, prefix="/editor")

if __name__ == "__main__":
    uvicorn.run(
        app,
        host=settings.host,
        port=settings.port
    )
