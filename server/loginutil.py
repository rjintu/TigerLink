import requests
from . import keys # file *not* in git containing our client id + key

GOOGLE_CLIENT_ID = keys.CL_ID
GOOGLE_CLIENT_SECRET = keys.CL_SECRET
GOOGLE_DISCOVERY_URL = (
        "https://accounts.google.com/.well-known/openid-configuration"
    )

def get_google_provider_cfg():
    return requests.get(GOOGLE_DISCOVERY_URL).json()
