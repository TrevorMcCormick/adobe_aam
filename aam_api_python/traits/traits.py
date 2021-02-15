# Import packages
import os
import json
from datetime import datetime, timedelta
import requests
import jwt
import pandas as pd

from aam_api_python.helpers.headers import *
from aam_api_python.helpers.simplify import *

class Traits:
## https://experienceleague.adobe.com/docs/audience-manager/user-guide/api-and-sdk-code/rest-apis/aam-api-getting-started.html?lang=en#optional-api-query-parameters

    @classmethod
    def get_many(cls,
                 ## These are all of the Adobe arguments
                 page=None,
                 pageSize=None,
                 sortBy=None,
                 descending=None,
                 search=None,
                 folderId=None,
                 permissions=None,
                 includePermissions=None,
                 ic=None,
                 ## These are all of the custom arguments
                 condense=None
                 ):
        ## Traits endpoint
        request_url = "https://aam.adobe.io/v1/traits/"
        if ic:
            request_url += "ic:{0}".format(str(ic))
        ## Required data
        request_data = {"page":page,
                        "pageSize":pageSize,
                        "sortBy":sortBy,
                        "descending":descending,
                        "search":search,
                        "folderId":folderId,
                        "permissions":permissions,
                        "includePermissions":includePermissions}
        ## Make request 
        response = requests.get(url = request_url,
                                headers = Headers.createHeaders(),
                                params = request_data) 
        ## Print error code if get request is unsuccessful
        if response.status_code != 200:
            print(response.content)
        else:
            ## Make a dataframe out of the response.json object
            df = pd.DataFrame(response.json())
            ## Change time columns from unix time to datetime
            df['createTime'] = pd.to_datetime(df['createTime'], unit='ms')
            df['updateTime'] = pd.to_datetime(df['updateTime'], unit='ms')
            if ic:
                # Bug: permissions column gets exploded and not sure why. low priority
                df = df.drop(columns=['permissions'])
                df = df.drop_duplicates()
            ## This begins the PDM section for additional functionality
            ## Simplify: limits columns
            if condense:
                df = simplify(df)
            return df

    @classmethod
    def get_one(cls,
                ## These are all of the Adobe arguments
                sid,
                ## These are all of PDM's custom arguments
                condense=None
                ):
        ## Traits endpoint for specific trait ID
        request_url = "https://aam.adobe.io/v1/traits/{0}".format(str(sid))
        
        ## Make request 
        response = requests.get(url = request_url,
                                headers = Headers.createHeaders()) 
        
        ## Print error code if get request is unsuccessful
        if response.status_code != 200:
            print(response.content)
        else:
            ## Make a dataframe out of the response.json object
            df = pd.DataFrame.from_dict(response.json(), orient='index')
            df = df.transpose()
            ## Change time columns from unix time to datetime
            df['createTime'] = pd.to_datetime(df['createTime'], unit='ms')
            df['updateTime'] = pd.to_datetime(df['updateTime'], unit='ms')
        ## This begins the PDM section for additional functionality
        ## Simplify: limits columns
        if condense:
            df = simplify(df)
        return df

    @classmethod
    def get_limits(cls):
        ## Traits endpoint for limits
        request_url = "https://aam.adobe.io/v1/traits/limits"
        
        ## Make request 
        response = requests.get(url = request_url,
                                headers = Headers.createHeaders())
        
        ## Print error code if get request is unsuccessful
        if response.status_code != 200:
            print(response.content)
        else:
            ## Uses json_normalize function to make data prettier
            json_response = json.loads(response.content.decode('utf-8'))
            df = pd.json_normalize(json_response)
            df = df.transpose()
            return df

#   @classmethod
#   def create(cls, traits):
#     ## Required columns
#     required_columns = pd.DataFrame(columns=['traitType', 'name', 'dataSourceId', 'folderId', 'traitRule', 'ttl', 'description', 'comments'])
#     df = pd.read_csv(traits, engine='python')
#     if list(df.columns) != list(required_columns.columns):
#       required_columns.to_csv('aam_trait_create_template.csv')
#       raise Exception('Column names are incorrect. Please re-upload file with template.')
