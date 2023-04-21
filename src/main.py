from model.db import add_user_to_database, get_user, get_all_transfers_from, get_all_transfers_to, get_user_id_by_email, \
    get_user_id_by_login, add_transfer, user_exists, update_user_balance, get_user_data_by_id, get_user_balance
from model.user import User
from src.validation import valid_email, valid_password

from fastapi import FastAPI, Request, Form, status
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from starlette.middleware.sessions import SessionMiddleware

app = FastAPI()
templates = Jinja2Templates(directory="src/templates")
app.add_middleware(SessionMiddleware, secret_key="test")


def comp_less(item1, item2):
    return item1[1] < item2[1]


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
    transfers = make_transfers(get_all_transfers_from(user), get_all_transfers_to(user))
    return templates.TemplateResponse(
        "main.html",
        {
            "request": request,
            "transfers": transfers
        }
    )


@app.get("/register")
def get_register_page(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})


@app.post("/register")
def register_user(request: Request, login: str = Form(""), email: str = Form(""), password: str = Form("")):
    new_user = User(login, email, password)

    if not valid_email(email):
        return {"message": "Email not valid."}
    if not valid_password(password):
        return {"message": "Password not valid."}

    if user_exists(new_user):
        return {"message": "User exists."}

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

    if not user_exists(user):
        return {"message": "User doesn't exist."}

    request.session["user"] = user.to_dict()
    return RedirectResponse("/", status_code=status.HTTP_303_SEE_OTHER)


@app.get("/logout")
def logout(request: Request):
    request.session.pop("user")
    return RedirectResponse("/")


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

    user = User.from_dict(request.session.get("user"))
    user_balance = get_user_balance(user)
    if user_balance < amount:
        return {"message": "Not enough many in your balance."}
    if not user_exists(user):
        return {"message": "User doesn't exist."}

    request.session["transfer_data"] = transfer_data
    return templates.TemplateResponse("approve-transfer.html",
                                      {"request": request, "login": login, "amount": amount})


@app.post("/transfer")
def add_transfer_(request: Request):
    transfer_data = request.session.get("transfer_data")
    user = request.session.get("user")
    from_id = get_user_id_by_email(user["email"])
    to_id = get_user_id_by_login(transfer_data["login"])
    amount = transfer_data["amount"]

    user2 = get_user_data_by_id(to_id)
    user = User.from_dict(user)
    if not user2:
        return {"message": "User doesn't exist."}
    to_user = User(user2[0], user2[1], user2[2])

    add_transfer(from_id, to_id, amount)
    update_user_balance(user, -amount)
    update_user_balance(to_user, amount)
    return RedirectResponse("/", status_code=status.HTTP_303_SEE_OTHER)
