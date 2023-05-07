from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.middleware.sessions import SessionMiddleware

from src.routers.login import router as login_router
from src.routers.main import router as main_page_router
from src.routers.transfer import router as transfer_router

app = FastAPI()
templates = Jinja2Templates(directory="src/templates")
app.mount("/static/", StaticFiles(directory="static"), name="static")
app.add_middleware(SessionMiddleware, secret_key="test")

app.include_router(main_page_router)
app.include_router(login_router)
app.include_router(transfer_router)
