import random

from model import User
from model import Transfer
from src.validation import valid_email, valid_password

from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError
from fastapi import FastAPI, Request, HTTPException, Form, status
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from starlette.middleware.sessions import SessionMiddleware
import smtplib


import uvicorn

app = FastAPI()
templates = Jinja2Templates(directory="src/templates")
app.add_middleware(SessionMiddleware, secret_key="test")


def comp_less(item1, item2):
    return item1[3] > item2[3]


def make_transfers(t_from: list, t_to: list):
    i, j = 0, 0
    n, m = len(t_from), len(t_to)
    res = []
    while i < n and j < m:
        if comp_less(t_from[i], t_to[j]):
            res.append(t_from[i] + (1, ))
            i += 1
        else:
            res.append(t_to[j] + (0, ))
            j += 1
    if i != n:
        for x in t_from[i:]:
            res.append(x + (1, ))
    if j != m:
        for x in t_to[j:]:
            res.append(x + (0, ))
    return res


@app.get("/")
def get_main_page(request: Request):
    user = request.session.get("user")
    if user is None:
        return RedirectResponse("/login")

    user = User.from_dict(user)
    transfers = make_transfers(Transfer.all_from(user), Transfer.all_to(user))

    return templates.TemplateResponse(
        "main.html",
        {
            "request": request,
            "transfers": transfers
        }
    )


@app.get("/all-transfers")
def get_all_transfers_page(request: Request):
    user = request.session.get("user")
    if user is None:
        return RedirectResponse("/login")
    user = User.from_dict(user)
    transfers = make_transfers(Transfer.all_from(user, all_=True), Transfer.all_to(user, all_=True))
    return templates.TemplateResponse(
        "main.html",
        {
            "request": request,
            "transfers": transfers,
            "all_": True
        }
    )


@app.get("/register")
def get_register_page(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})


@app.post("/register")
def register_user(request: Request, login: str = Form(""), email: str = Form(""), password: str = Form("")):
    new_user = User.get(login=login)

    if not valid_email(email):
        return {"message": "Email not valid."}
    if not valid_password(password):
        return {"message": "Password not valid."}

    if new_user is not None:
        return {"message": "User exists."}

    new_user = User(-1, login, email, password, 0)
    new_user.add_to_db()
    new_user = User.get(login=new_user.login)
    request.session["user"] = new_user.to_dict()
    return RedirectResponse("/", status_code=status.HTTP_303_SEE_OTHER)


@app.get("/login")
def get_login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})


@app.post("/login")
def login_user(request: Request, login: str = Form(""), password: str = Form("")):
    user = User.get(login=login)
    if not user:
        return {"message": "User not found."}

    ph = PasswordHasher()
    h_pass = user.password

    try:
        ph.verify(h_pass, password)
    except VerifyMismatchError:
        return {"message": "Bad password"}

    request.session["user"] = user.to_dict()
    return RedirectResponse("/", status_code=status.HTTP_303_SEE_OTHER)


@app.get("/logout")
def logout(request: Request):
    request.session.pop("user")
    return RedirectResponse("/login")


@app.get("/forgot-password")
def forgot_password_page(request: Request):
    return templates.TemplateResponse("forgot-password.html", {"request": request})


@app.post("/forgot-password")
def forgot_password(request: Request, email: str = Form("")):
    if not valid_email(email):
        return {"message": "Email not valid."}
    try:
        user = User.get(email=email)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        reset_token = "".join([str(random.randint(0, 9)) for _ in range(10)])
        request.session["token"] = reset_token
        request.session["email"] = email

        smtp_server = "smtp.gmail.com"
        smtp_port = 465
        smtp_username = "bank.moj.ulubiony@gmail.com"
        smtp_password = "mgcuexptvlwoczdk"

        body = f"Subject: Password Reset Request\n\n" \
               f"Hi {user.login},\n\n" \
               f"We received a request to reset the password for your account. This is your special code: " \
               f"\n\n{reset_token}\nIf you did not request a password reset, please ignore this " \
               f"email.\n\nThanks,\nThe MojWspanialyBank Team"

        with smtplib.SMTP_SSL(smtp_server, smtp_port) as server:
            server.login(smtp_username, smtp_password)
            server.sendmail(smtp_username, user.email, body)

        return templates.TemplateResponse("approve-password.html", {"request": request})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/password-code")
def password_code(request: Request, token: str = Form("")):
    good_token = request.session.pop("token")
    if token == good_token:
        return RedirectResponse("/update-password", status_code=status.HTTP_303_SEE_OTHER)
    return {"message": "Bad token."}


@app.get("/update-password")
def update_password_page(request: Request):
    return templates.TemplateResponse("update-password.html", {"request": request})


@app.post("/update-password")
def update_password_(request: Request, new_password: str = Form("")):
    email = request.session.pop("email")
    if not valid_password(new_password):
        return {"message": "Password not valid."}
    user = User.get(email=email)
    user.update_password(new_password)
    request.session["user"] = user.to_dict()
    return RedirectResponse("/", status_code=status.HTTP_303_SEE_OTHER)


@app.get("/transfer")
def get_transfer_page(request: Request):
    return templates.TemplateResponse("transfer.html", {"request": request})


@app.post("/approve-transfer")
def get_approve_transfer_page(
        request: Request,
        login: str = Form(""),
        title: str = Form(""),
        description: str = Form(""),
        amount: int = Form(0)
):
    transfer_data = {
        "login": login,
        "title": title,
        "description": description,
        "amount": amount
    }

    if amount <= 0:
        return {"message": "Transaction amount must be positive"}

    user = User.from_dict(request.session.get("user"))
    if user.balance < amount:
        return {"message": "Not enough many in your balance."}
    if not user.exists():
        return {"message": "User doesn't exist."}

    request.session["transfer_data"] = transfer_data
    return templates.TemplateResponse(
        "approve-transfer.html",
        {
            "request": request,
            "login": login,
            "title": title,
            "description": description,
            "amount": amount
        })


@app.post("/transfer")
def add_transfer_(request: Request):
    transfer_data = request.session.pop("transfer_data")
    user = request.session.get("user")
    title = transfer_data["title"]
    desc = transfer_data["description"]
    amount = transfer_data["amount"]

    user = User.from_dict(user)
    user2 = User.get(login=transfer_data["login"])
    if not user2.exists():
        return {"message": "User doesn't exist."}

    transfer = Transfer(user.id_, user2.id_, title, desc, amount)
    transfer.add_to_db()

    user.update_balance(-amount)
    user2.update_balance(amount)
    return RedirectResponse("/", status_code=status.HTTP_303_SEE_OTHER)
