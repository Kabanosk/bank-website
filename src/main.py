from model.db import add_user_to_database, get_user, get_all_transfers_from, get_all_transfers_to
from model.user import User

from fastapi import FastAPI, Request, Form, status
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from starlette.middleware.sessions import SessionMiddleware

app = FastAPI()
templates = Jinja2Templates(directory="src/templates")
app.add_middleware(SessionMiddleware, secret_key="test")

# CRUD -> Create read update delete
# GET       Read
# POST      create
# DELETE    delete
# PUT       update


@app.get("/")
def get_main_page(request: Request):
    user = request.session.get("user")
    if user is None:
        return RedirectResponse("/login")
    return templates.TemplateResponse(
        "main.html",
        {
            "request": request,
            "transfers_from": get_all_transfers_from(User.from_dict(user)),
            "transfers_to": get_all_transfers_to(User.from_dict(user))
        }
    )


@app.get("/register")
def get_register_page(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})


@app.post("/register")
def register_user(request: Request, login: str = Form(""), email: str = Form(""), password: str = Form("")):
    new_user = User(login, email, password)
    add_user_to_database(new_user)
    request.session["user"] = new_user.to_dict()
    return RedirectResponse("/", status_code=status.HTTP_303_SEE_OTHER)


@app.get("/login")
def get_login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})


@app.post("/login")
def login_user(request: Request, login: str = Form(""), password: str = Form("")):
    user_data = get_user(login, password)
    user = User(*user_data)
    request.session["user"] = user.to_dict()
    return RedirectResponse("/", status_code=status.HTTP_303_SEE_OTHER)


@app.get("/forgot-password")
def forgot_password_page(request: Request):
    pass  # TODO: forgot password page
