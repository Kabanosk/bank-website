from fastapi import APIRouter, Request, Form, status
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates

from src.models import User
from src.models import Transfer

router = APIRouter()
templates = Jinja2Templates(directory="src/templates")


@router.get("/transfer")
def get_transfer_page(request: Request):
    return templates.TemplateResponse("transfer.html", {"request": request})


@router.post("/approve-transfer")
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

    user_dict = request.session.get("user")
    if user_dict is None:
        return {"message": "User must be logged in."}
    user = User.from_dict(user_dict)
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


@router.post("/transfer")
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
