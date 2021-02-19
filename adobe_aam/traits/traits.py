# Import packages
import os
import json
from datetime import datetime, timedelta
import requests
import jwt
import pandas as pd

from adobe_aam.helpers.headers import *
from adobe_aam.helpers.simplify import *

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

    @classmethod
    def create_from_csv(cls, file_path):
        ## Traits endpoint for create is old demdex URL
        request_url = "https://api.demdex.com/v1/traits/"
        ## Required columns for API call
        reqd_cols = pd.DataFrame(columns=['traitType', 'name', 'dataSourceId', 'folderId', 'traitRule', 'ttl', 'description', 'comments'])
        ## Load csv into pandas df
        if file_path.endswith('.csv'):
            df = pd.read_csv(file_path, engine='python')
        else:
            raise Exception('File type is not csv.')
        ## Check for reqd cols
        if list(df.columns) != list(reqd_cols.columns):
            reqd_cols.to_csv('aam_trait_create_template.csv', index=False)
            raise Exception('Column names are incorrect. Please re-upload file with template.')
        traits_as_dict = df.to_dict(orient='records')
        
        ## Declare counter vars
        num_traits_in_file = len(traits_as_dict)
        num_successful_traits = 0
        
        ## Handle for bad traits
        unsuccessful_traits = pd.DataFrame(columns=['traitType', 'name', 'dataSourceId', 'folderId', 'traitRule', 'ttl', 'description', 'comments'])
               
        for trait in traits_as_dict:
            trait_json = json.dumps(trait)
            response = requests.post(url = request_url,
                                    headers = Headers.createHeaders(traitCreate=True),
                                    data=trait_json)
            ## Print error code if get request is unsuccessful
            if response.status_code != 201:
                print("Attempt to create trait {0} was unsuccessful. \nError code {1}. \nReason: {2}".format(trait['name'], response.status_code, response.content.decode('utf-8')))
                unsuccessful_traits = unsuccessful_traits.append(trait, ignore_index=True)
            else:
                num_successful_traits += 1
        
        ## Return bad traits
        if len(unsuccessful_traits) > 0:
            unsuccessful_traits.to_csv('aam_unsuccessful_traits.csv', index=False)
            print('Unsuccessful traits written to aam_unsuccessful_traits.csv')
        return "{0} of {1} traits in file successfully created.".format(num_successful_traits, num_traits_in_file)
    
    @classmethod
    def delete_many(cls, file_path):
        ## Traits endpoint for delete is old demdex URL
        request_url = "https://api.demdex.com/v1/traits/"
        ## Required columns for API call
        reqd_cols = pd.DataFrame(columns=['sid'])
        ## Load csv into pandas df
        if file_path.endswith('.csv'):
            df = pd.read_csv(file_path, engine='python')
        else:
            raise Exception('File type is not csv.')
        ## Check for reqd cols
        if list(df.columns) != list(reqd_cols.columns):
            reqd_cols.to_csv('aam_trait_delete_template.csv', index=False)
            raise Exception('Column name should be sid. Please re-upload file with template.')
        
        ## Declare counter vars
        num_traits_in_file = len(df)
        num_successful_traits = 0
        
        ## Handle for bad traits
        unsuccessful_traits = pd.DataFrame(columns=['sid'])
               
        for index, row in df.iterrows():
            response = requests.delete(url = request_url+'/{0}'.format(row['sid']),
                                     headers = Headers.createHeaders())
            
            ## Print error code if get request is unsuccessful
            if response.status_code != 204:
                print("Attempt to delete trait {0} was unsuccessful. \nError code {1}. \nReason: {2}".format(row['sid'], response.status_code, response.content.decode('utf-8')))
                unsuccessful_traits = unsuccessful_traits.append(row, ignore_index=True)
            else:
                num_successful_traits += 1
        
        ## Return bad traits
        if len(unsuccessful_traits) > 0:
            unsuccessful_traits.to_csv('aam_unsuccessful_traits.csv', index=False)
            print('Unsuccessful traits written to aam_unsuccessful_traits.csv')
        return "{0} of {1} traits in file successfully deleted.".format(num_successful_traits, num_traits_in_file)
    
    @classmethod
    def delete_one(cls, sid, ic=None):
        ## Traits endpoint for delete is old demdex URL
        request_url = "https://api.demdex.com/v1/traits/{0}".format(str(sid))
        if ic:
            request_url = "https://api.demdex.com/v1/traits/{0}".format(str(ic))
        
        response = requests.delete(url = request_url,
                                   headers = Headers.createHeaders())     
        if ic:
            if response.status_code != 204:
                print("Attempt to delete trait with ic={0} was unsuccessful. \nError code {1}. \nReason: {2}".format(ic, response.status_code, response.content.decode('utf-8')))
            else:
                return "Trait with ic={0} successfully deleted.".format(ic)
        else:
            if response.status_code != 204:
                print("Attempt to delete trait {0} was unsuccessful. \nError code {1}. \nReason: {2}".format(sid, response.status_code, response.content.decode('utf-8')))
            else:
                return "Trait {0} successfully deleted.".format(sid)

    @classmethod
    def update_many(cls, file_path):
        ## Required columns for API call
        reqd_cols = pd.DataFrame(columns=['traitType', 'name', 'dataSourceId', 'folderId', 'sid'])
        ## Load csv into pandas df
        if file_path.endswith('.csv'):
            df = pd.read_csv(file_path, engine='python')
        else:
            raise Exception('File type is not csv.')
        ## Check for reqd cols
        if list(reqd_cols.columns) != list(df.columns):
            reqd_cols.to_csv('aam_trait_update_template.csv', index=False)
            raise Exception('CSV should include at least the following columns, with additional columns you want to update. Please re-upload file using template.')
        
        ## Declare counter vars
        num_traits_in_file = len(df)
        num_successful_traits = 0
        
        ## Handle for bad traits
        unsuccessful_traits = pd.DataFrame()
        
        ## Get request data
        traits_as_dict = df.to_dict(orient='records')

        for trait in traits_as_dict:
            sid = trait['sid']
            trait_json = json.dumps(trait)  
            request_url = "https://api.demdex.com/v1/traits/{0}".format(sid)
            response = requests.put(url = request_url,
                                    headers = Headers.createHeaders(traitCreate=True),
                                    data = trait_json)
            ## Print error code if get request is unsuccessful
            if response.status_code != 200:
                print("Attempt to update trait {0} was unsuccessful. \nError code {1}. \nReason: {2}".format(sid, response.status_code, response.content.decode('utf-8')))
                unsuccessful_traits = unsuccessful_traits.append(trait, ignore_index=True)
            else:
                num_successful_traits += 1
 
        ## Return bad traits
        if len(unsuccessful_traits) > 0:
            unsuccessful_traits.to_csv('aam_unsuccessful_traits.csv', index=False)
            print('Unsuccessful traits written to aam_unsuccessful_traits.csv')
        return "{0} of {1} traits in file successfully updated.".format(num_successful_traits, num_traits_in_file)