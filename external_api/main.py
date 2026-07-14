from dotenv import load_dotenv
import os
import xmlrpc.client
import json

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

partner_ids = models.execute_kw(db,uid,password,'res.partner','search',[[['is_company','=', True]]], {'offset': 0, 'limit' : 1})

count = models.execute_kw(db,uid,password,'res.partner','search_count',[[['is_company','=', True]]])

record = models.execute_kw(db, uid, password, 'res.partner', 'read', [partner_ids], {'fields': ['name', 'country_id', 'comment']})

field_get = models.execute_kw(db,uid,password,'gold.price','fields_get',[],{'attributes' : ['string','help','type']})

search_read = models.execute_kw(db,uid,password,'res.partner','search_read',[[['is_company','=',True]]], {'fields' : ['name', 'country_id', 'comment'], 'limit' : 5})

id = models.execute_kw(db,uid,password,'res.partner','create',[{'name' : "new partner gg"}])

models.execute_kw(db,uid,password,'res.partner','write',[[id],{'name' : "Kocak"}])
read = models.execute_kw(db, uid, password, 'res.partner', 'read', [[id], ['display_name']])

models.execute_kw(db, uid, password, 'res.partner', 'unlink', [[id]])
search = models.execute_kw(db, uid, password, 'res.partner', 'search', [[['id', '=', id]]])
print(search)
