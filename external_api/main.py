from dotenv import load_dotenv
import os
import xmlrpc.client

load_dotenv()

url = os.getenv("URL")
db = os.getenv("DB")
username = os.getenv("USERNAME")
password = os.getenv("PASSWORD")

common = xmlrpc.client.ServerProxy(
    f"{url}/xmlrpc/2/common"
)

version = common.version()
print(version)

uid = common.authenticate(
    db,
    username,
    password,
    {}
)
print(uid)

models = xmlrpc.client.ServerProxy(
    f"{url}/xmlrpc/2/object"
)
print(models)

models.execute_kw(db,uid,password,'res.partner','name_search',['foo'],{'limit' : 10})

partner_ids = models.execute_kw(db,uid,password,'res.partner','search',[[['is_company','=', True]]], {'offset': 2, 'limit' : 10})

count = models.execute_kw(db,uid,password,'res.partner','search_count',[[['is_company','=', True]]])
