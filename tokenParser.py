import jwt
import requests
import re

def get_api_key():
    res = requests.get('https://myvisit.com/bundles/plugins?v=3591605')
    pattern = "ApplicationAPIKey: '.+',"
    return re.findall(pattern, res.text)[0].split("'")[1]
# token = ''
# print(jwt.decode(token, options={"verify_signature": False}))
print(get_api_key())