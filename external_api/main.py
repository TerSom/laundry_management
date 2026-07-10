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