# Import packages
import os
import json
from datetime import datetime, timedelta
import requests
import jwt

# Login
class Login:
    def __init__(self, credentials_path, private_key_path):
        ## Save credentials into environment variable
        with open(credentials_path, mode="r") as file:
            credentials = json.loads(file.read())

        ## Generate JWT
        jwt_data = {
                    "exp": datetime.now() + timedelta(hours=1),
                    "iss":  credentials['org_id'],
                    "sub":  credentials['tech_acct_id'],
                    "https://ims-na1.adobelogin.com/s/ent_audiencemanagerplatform_sdk": True,
                    "aud": "https://ims-na1.adobelogin.com/c/{0}".format(credentials['client_id'])
                    }
        ## Save private key into environment variable
        with open(private_key_path,"rb") as file:
             private_key = file.read()

        ## Encode JWT using RS256 algorithm
        encoded_jwt = jwt.encode(jwt_data,
                                 private_key, 
                                 algorithm="RS256")

        ## Generate login headers
        login_header = {
                        "Content-Type":"application/x-www-form-urlencoded", 
                        "Cache-Control":"no-cache"
                        }

        ## Generate login ody headers
        login_body = {
                        "client_id": credentials['client_id'],
                        "client_secret": credentials['client_secret'],
                        "jwt_token": encoded_jwt
                      }

        ## This is the Adobe JWT login URL
        login_url = "https://ims-na1.adobelogin.com/ims/exchange/jwt/"

        ## POST API method call
        response = requests.post(url = login_url,
                                 data = login_body)

        ## Check for successful status code
        if response.status_code == 200:
            os.environ['aam_api_token'] = response.json()['access_token']
            print("Login Success.")
        else:
            print(response.json())