from os import environ
from sys import stderr
from oauthlib.oauth2 import WebApplicationClient
import requests
import json


GOOGLE_DISCOVERY_URL = (
        "https://accounts.google.com/.well-known/openid-configuration"
    )

def get_google_provider_cfg():
    return requests.get(GOOGLE_DISCOVERY_URL).json()

class GoogleLogin:

    # set up keys & the oauth client
    def __init__(self):
        self._CLIENT_ID = environ.get('GOOGLE_CLIENT_ID')
        self._CLIENT_SECRET = environ.get('GOOGLE_CLIENT_SECRET')
        if self._CLIENT_ID is None:
            print('Could not load keys from environment variables')
            print('Loading keys through keys.py...')
            try:
                from . import keys
                self._CLIENT_ID = keys.GOOGLE_CLIENT_ID
                self._CLIENT_SECRET = keys.GOOGLE_CLIENT_SECRET
            except Exception as e:
                print("Error: could not load secret keys!", file=stderr)
                print("Do you have keys.py in the 'server' folder?", file=stderr)
                print("More info: " + str(e))
                exit(1)

        self._oauth_cl = WebApplicationClient(self._CLIENT_ID)

    def get_login_redirect(self, request):
        # find out which URL to redirect to
        google_provider_cfg = get_google_provider_cfg()
        auth_endpoint = google_provider_cfg["authorization_endpoint"]

        request_uri = self._oauth_cl.prepare_request_uri(
            auth_endpoint,
            redirect_uri = request.base_url + "/auth",
            scope = ["openid", "email", "profile"],
        )
        return request_uri

    def authorize(self, request):
        # refer to https://realpython.com/flask-google-login/ for more info
        google_provider_cfg = get_google_provider_cfg()
        token_endpoint = google_provider_cfg["token_endpoint"]

        # get the code that google sent back to us
        code = request.args.get('code')

        # prep request to get tokens
        token_url, headers, body = self._oauth_cl.prepare_token_request(
            token_endpoint,
            authorization_response = request.url,
            redirect_url = request.base_url,
            code = code
        )
        token_response = requests.post(
            token_url,
            headers = headers,
            data = body,
            auth = (self._CLIENT_ID, self._CLIENT_SECRET),
        )

        # parse the tokens
        self._oauth_cl.parse_request_body_response(json.dumps(token_response.json()))

        # now get user info from google
        userinfo_endpoint = google_provider_cfg["userinfo_endpoint"]
        uri, headers, body = self._oauth_cl.add_token(userinfo_endpoint)
        userinfo_response = requests.get(uri, headers=headers, data=body)

        # now get all relevant user data
        info = userinfo_response.json()
        return (info['sub'], info['email'], info['name'])
