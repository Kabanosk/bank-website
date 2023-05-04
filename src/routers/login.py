from src.models import User
from src.validation import valid_email, valid_password

import random

from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError
from fastapi import APIRouter, Request, HTTPException, Form, status
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
import smtplib

router = APIRouter()
templates = Jinja2Templates(directory="src/templates")


@router.get("/register")
def get_register_page(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})


@router.post("/register")
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


@router.get("/login")
def get_login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})


@router.post("/login")
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


@router.get("/logout")
def logout(request: Request):
    request.session.pop("user")
    return RedirectResponse("/login")


@router.get("/forgot-password")
def forgot_password_page(request: Request):
    return templates.TemplateResponse("forgot-password.html", {"request": request})


@router.post("/forgot-password")
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
        smtp_username = "moj.bank.ulubiony@gmail.com"
        smtp_password = "eifcjxhlipggcqua"

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


@router.post("/password-code")
def password_code(request: Request, token: str = Form("")):
    good_token = request.session.pop("token")
    if token == good_token:
        return RedirectResponse("/update-password", status_code=status.HTTP_303_SEE_OTHER)
    return {"message": "Bad token."}


@router.get("/update-password")
def update_password_page(request: Request):
    return templates.TemplateResponse("update-password.html", {"request": request})


@router.post("/update-password")
def update_password_(request: Request, new_password: str = Form("")):
    email = request.session.pop("email")
    if not valid_password(new_password):
        return {"message": "Password not valid."}
    user = User.get(email=email)
    user.update_password(new_password)
    request.session["user"] = user.to_dict()
    return RedirectResponse("/", status_code=status.HTTP_303_SEE_OTHER)
