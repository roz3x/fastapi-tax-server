import hashlib
import json
import base64
from functools import wraps
from db import con
from fastapi import HTTPException


def hash_password(password: str, name: str):
    m = hashlib.sha512()
    m.update(b"SALT:::::")
    m.update(name.encode('ascii'))
    m.update(password.encode('ascii'))
    return m.hexdigest()


def authentiacte(func):
    @wraps(func)
    async def wrapper(request, **kwargs):
        try:
            user = dict(
                json.loads(
                    base64.b64decode(request.headers.get(
                        "Authorization", "")).decode("utf-8")
                )
            )

            user["password"] = hash_password(user["password"], user["name"])
            cur = con.cursor()
            cur.execute("""
            select * from users where id = ? and password = ?
            """, (user["id"], user["password"]))
            res = cur.fetchone()
            if res is None:
                raise HTTPException(403, "forbidden ")
            request.id = user["id"]
            return await func(request, **kwargs)
        except Exception as e:
            print(f"exception on authenticate {e}")
            raise HTTPException(498, "invalid creds")
    return wrapper


def authentiacte_accountant(func):
    @wraps(func)
    async def wrapper(request, **kwargs):
        try:
            user = dict(
                json.loads(
                    base64.b64decode(request.headers.get(
                        "Authorization", "")).decode("utf-8")
                )
            )

            user["password"] = hash_password(user["password"], user["name"])
            cur = con.cursor()
            cur.execute("""
            select * from users where id = ? and password = ? and type = 1
            """, (user["id"], user["password"]))
            res = cur.fetchone()
            request.id = user["id"]
            if res is None:
                raise HTTPException(403, "forbidden ")
            return await func(request, **kwargs)
        except Exception as e:
            print(f"exception {e}")
            raise HTTPException(498, "invalid creds")
    return wrapper



def authentiacte_accountant_or_admin(func):
    @wraps(func)
    async def wrapper(request, **kwargs):
        try:
            user = dict(
                json.loads(
                    base64.b64decode(request.headers.get(
                        "Authorization", "")).decode("utf-8")
                )
            )

            user["password"] = hash_password(user["password"], user["name"])
            cur = con.cursor()
            cur.execute("""
            select * from users where id = ? and password = ? and type > 0
            """, (user["id"], user["password"]))
            res = cur.fetchone()
            request.id = user["id"]
            if res is None:
                raise HTTPException(403, "forbidden ")
            return await func(request, **kwargs)
        except Exception as e:
            print(f"exception {e}")
            raise HTTPException(498, "invalid creds")
    return wrapper
