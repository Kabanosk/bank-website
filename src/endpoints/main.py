from model import User
from model import Transfer

from fastapi import APIRouter, Request
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates


router = APIRouter()
templates = Jinja2Templates(directory="src/templates")


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


@router.get("/")
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


@router.get("/all-transfers")
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
