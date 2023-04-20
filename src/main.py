from model.db import add_user_to_database, get_user, get_all_transfers_from, get_all_transfers_to, get_user_id, \
    get_user_id_by_login, add_transfer
from model.user import User

from fastapi import FastAPI, Request, Form, status, Query
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from starlette.middleware.sessions import SessionMiddleware


import uvicorn

app = FastAPI()
templates = Jinja2Templates(directory="src/templates")
app.add_middleware(SessionMiddleware, secret_key="test")


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


@app.get("/transfer")
def get_transfer_page(request: Request):
    return templates.TemplateResponse("transfer.html", {"request": request})


@app.post("/approve-transfer")
def get_approve_transfer_page(request: Request, login: str = Form(""), amount: int = Form("")):
    transfer_data = {
        "login": login,
        "amount": amount
    }
    request.session["transfer_data"] = transfer_data
    return templates.TemplateResponse("approve-transfer.html",
                                      {"request": request, "login": login, "amount": amount})


@app.post("/transfer")
def add_transfer_(request: Request):
    transfer_data = request.session.get("transfer_data")
    user = request.session.get("user")
    from_id = get_user_id(user["email"])
    to_id = get_user_id_by_login(transfer_data["login"])
    amount = transfer_data["amount"]
    add_transfer(from_id, to_id, amount)
    return RedirectResponse("/", status_code=status.HTTP_303_SEE_OTHER)


if __name__ == "__main__":
    uvicorn.run("main:app", port=5000, log_level="info")
