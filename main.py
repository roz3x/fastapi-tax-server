
from fastapi import FastAPI, Request, HTTPException
from pydantic import BaseModel
import time
import uvicorn
from db import con
from auth_wrappers import authentiacte, authentiacte_accountant, hash_password, authentiacte_accountant_or_admin


# dockerfile
#  X DB
#  X auth is based on passwords
#  X view for listing the taxs


app = FastAPI()


class User(BaseModel):
    name: str
    password: str
    type: int
    tax: int
    ut_citizen: bool


@app.post("/create")
async def create_user(user: User):
    user.password = hash_password(user.password, user.name)
    cur = con.cursor()
    cur.execute("""
                insert into users (name, password, type, tax , ut_citizen) values(?, ? , ? , ? , ?) returning *;
                """, (user.name, user.password, user.type, user.tax, user.ut_citizen))
    return cur.fetchone()["id"]


class AddAccountantModel(BaseModel):
    accountant_id: int


@app.post("/add-accountant")
@authentiacte
async def add_manager(request: Request, user: AddAccountantModel):

    cur = con.cursor()
    cur.execute("""
    select name from users where type = 1  and id = ?;
    """)
    if cur.fetchone() is None:
        raise HTTPException(498, "not account found")
    cur.execute("""
    insert into managed_by (accountant_id, user_id) values(? , ? );
    """, (user.accountant_id, request.id))


class AddTaxModel(BaseModel):
    ammount: int
    user_id: int


@app.post("/add-tax")
@authentiacte_accountant
async def add_tax(request: Request, a: AddTaxModel):
    # we need to check if the user_id is managed by the current accountant
    cur = con.cursor()
    cur.execute("""
    select * from managed_by where accountant_id = ? and user_id = ? ;
    """, (request.id, a.user_id))
    if cur.fetchone() is None:
        raise HTTPException(403, "user is not managed by this accountant")

    # check if user if ut_citizen
    cur.execute("""
        select ut_citizen from users where id = ?;
    """, (a.user_id, ))

    # considering the state_tax is const
    state_tax = 5
    if not cur.fetchone()['ut_citizen']:
        a.ammount += a.ammount * state_tax // 100

    cur.execute("""
    update users set tax = tax + ? where id = ? ;
    """, (a.ammount, a.user_id))

    cur.execute("""
    insert into taxes(user_id, ammount, time, paid) values (? , ? , ?, ? ) returning * ;
    """, (a.user_id, a.ammount, int(time.time()), False))
    return cur.fetchone()["id"]


class MarkTaxPaid(BaseModel):
    tax_id: int


@app.post("/mark-tax-paid")
@authentiacte_accountant
async def mark_tax_paid(request, a: MarkTaxPaid):
    # we need to check if the user_id is managed by the current accountant
    cur = con.cursor()
    cur.execute("""
    select * from managed_by where accountant_id = ? and user_id = ?
    """, (request.id, a.user_id))
    if cur.fetchone() is None:
        raise HTTPException(403, "user is not managed by this accountant")

    cur.execute(""""
    update taxes set tax_paid = 1 where id = ?  returning *;
    """, (a.tax_id))

    ammount = cur.fetchone()["ammount"]
    cur.execute("""
    update users set tax = tax - ? where id = ? ;
    """, (ammount, a.user_id))

    pass


class ViewAllTableModel(BaseModel):
    tax_paid: int


class VeiwAllTableModelResponse(BaseModel):
    name: str
    tax: int
    ammount: int
    ut_citizen: bool


@app.post("/view-all-table")
@authentiacte_accountant_or_admin
async def view_all_table(request: Request):
    cur = con.cursor()

    cur.execute("""
    select * from users join taxes on taxes.user_id = users.id;
    """)

    return [VeiwAllTableModelResponse(**i) for i in cur.fetchall()]


class ViewUserTaxesModel(BaseModel):
    user_id: int


@app.post("/view-user-taxes")
@authentiacte_accountant_or_admin
async def view_user_taxes(request: Request, a: ViewUserTaxesModel):
    cur = con.cursor()
    cur.execute("""
    select users.name , taxes.ammount, taxes.time, taxes.paid from taxes  join users  on taxes.user_id = users.id where user_id = ?; 
    """, (a.user_id, ))

    return cur.fetchall()

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        reload=True,
        port=5000,
    )
