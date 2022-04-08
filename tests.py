import requests
import base64
import json
url = "http://localhost:5000"


def pprint(a):
    print(json.dumps(json.loads(a), indent=2))


a_id = int(requests.post(url + "/create", json={
    "name": "u1",
    "password": "something",
    "type": 1,
    "tax": 0, "ut_citizen": False
}).content)

a_id_2 = int(requests.post(url + "/create", json={
    "name": "u4",
    "password": "something",
    "type": 1,
    "tax": 0, "ut_citizen": False
}).content)

u_id_2 = int(requests.post(url + "/create", json={
    "name": "u2",
    "password": "something",
    "type": 0,
    "tax": 0, "ut_citizen": False
}).content)

u_id = int(requests.post(url + "/create", json={
    "name": "u3",
    "password": "something",
    "type": 0,
    "tax": 0, "ut_citizen": True
}).content)

u_id_header = base64.b64encode(json.dumps(
    {"id": u_id, "password": "something", "name": "u3"}).encode('utf-8')
)
u_id_2_header = base64.b64encode(json.dumps(
    {"id": u_id_2, "password": "something", "name": "u2"}).encode('utf-8')
)

a_id_header = base64.b64encode(json.dumps(
    {"id": a_id, "password": "something", "name": "u1"}).encode('utf-8'))

a_id_2_header = base64.b64encode(json.dumps(
    {"id": a_id, "password": "something", "name": "u4"}).encode('utf-8'))


def test_basic_auth():
    res = requests.post(url+"/add-accountant", headers={
        "Authorization": "invalid string"
    }, json={"accountant_id": a_id})

    assert(res.status_code == 498)


def test_add_wrong_accountant():
    res = requests.post(url+"/add-accountant", headers={
        "Authorization": u_id_header
    }, json={"accountant_id": u_id_2})

    assert(res.status_code == 498)


def test_add_tax():
    res = requests.post(url+"/add-tax", headers={
        "Authorization": a_id_2_header
    }, json={"accountant_id": u_id_2})

    assert(res.status_code == 422)


requests.post(url+"/add-accountant", headers={
    "Authorization": u_id_header
}, json={"accountant_id": a_id})

requests.post(url+"/add-accountant", headers={
    "Authorization": u_id_2_header
}, json={"accountant_id": a_id})

# add tax for u1
requests.post(url+"/add-tax", headers={
    "Authorization": a_id_header
}, json={"ammount": 100, "user_id": u_id})

requests.post(url+"/add-tax", headers={
    "Authorization": a_id_header
}, json={"ammount": 10, "user_id": u_id})

requests.post(url+"/add-tax", headers={
    "Authorization": a_id_header
}, json={"ammount": 133, "user_id": u_id})


# add tax for u2
requests.post(url+"/add-tax", headers={
    "Authorization": a_id_header
}, json={"ammount": 100, "user_id": u_id_2})

requests.post(url+"/add-tax", headers={
    "Authorization": a_id_header
}, json={"ammount": 10, "user_id": u_id_2})

requests.post(url+"/add-tax", headers={
    "Authorization": a_id_header
}, json={"ammount": 133, "user_id": u_id_2})


def test_view_all_table():
    res = requests.post(url+"/view-all-table", headers={
        "Authorization": a_id_header
    }, json={"tax_paid": 0})
    assert(res.status_code == 200)
    


pprint(requests.post(url+"/view-user-taxes", headers={
    "Authorization": a_id_header
}, json={"user_id": u_id}).content.decode('utf-8'))
