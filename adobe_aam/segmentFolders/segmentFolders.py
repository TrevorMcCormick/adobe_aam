# Import packages
import os
import json
from datetime import datetime, timedelta
import requests
import jwt
import pandas as pd

from adobe_aam.helpers.headers import *
from adobe_aam.helpers.simplify import *


from pandas import json_normalize
def bytesToJson(response_content):
    json_response = json.loads(response_content.decode('utf-8'))
    df = json_normalize(json_response)
    return(df)


def flattenJson(nested_json):
    """
        Flatten json object with nested keys into a single level.
        Args:
            nested_json: A nested json object.
        Returns:
            The flattened json object if successful, None otherwise.
    """
    out = {}

    def flatten(x, name=''):
        if type(x) is dict:
            for a in x:
                flatten(x[a], name + a + '/')
        elif type(x) is list:
            i = 0
            for a in x:
                flatten(a, name + str(i) + '/')
                i += 1
        else:
            out[name[:-1]] = x

    flatten(nested_json)
    return out


class SegmentFolders:
    @classmethod
    def get_many(cls):
            """
                Get multiple AAM segmentFolders.
                Args:
                    includeThirdParty: (bool) Includes 3rd Party segmentFolders (defaults True).
                    dataSourceId: (int) Filter segmentFolders by Data Source ID.
                Returns:
                    df of all folderIds, parentFolderIds, and paths to which the AAM API user has READ access.
            """
            request_url = "https://api.demdex.com/v1/folders/segments"
            request_data = {}
            ## Make request 
            response = requests.get(url = request_url,
                                    headers = Headers.createHeaders(),
                                    params = request_data) 
            ## Print error code if get request is unsuccessful
            if response.status_code != 200:
                print(response.content)
            else:
                folders_json = response.json()
                folders_flat = flattenJson(folders_json)
                df = folders_flat
                folderIDs = []
                parentFolderIDs = []
                paths = []
                for k, v in folders_flat.items():
                    if k.endswith("folderId") == True:
                        folderIDs.append(v)
                    elif k.endswith("parentFolderId"):
                        parentFolderIDs.append(v)
                    elif k.endswith("path"):
                        paths.append(v)
                df = pd.DataFrame({'folderId':folderIDs, 'parentFolderId':parentFolderIDs, 'path':paths})
                return df

    @classmethod
    def get_one(cls,
        folderId,
        includeSubFolders=None):
            """
                Get one AAM segmentFolder.
                Args:
                    includeSubFolders: (bool) Scans subfolders and returns in df.
                Returns:
                    df of one folderId, with optional subfolders, provided the AAM API user has READ access.
            """
            request_url = "https://api.demdex.com/v1/folders/segments/{0}".format(folderId)
            request_data = {"includeSubFolders":includeSubFolders}
            ## Make request 
            response = requests.get(url = request_url,
                                    headers = Headers.createHeaders(),
                                    params = request_data) 
            ## Print error code if get request is unsuccessful
            if response.status_code != 200:
                print(response.content)
            else:
                if includeSubFolders == True:
                    folders_json = response.json()
                    folders_flat = flattenJson(folders_json)
                    df = folders_flat
                    folderIDs = []
                    parentFolderIDs = []
                    paths = []
                    for k, v in folders_flat.items():
                        if k.endswith("folderId") == True:
                            folderIDs.append(v)
                        elif k.endswith("parentFolderId"):
                            parentFolderIDs.append(v)
                        elif k.endswith("path"):
                            paths.append(v)
                    df = pd.DataFrame({'folderId':folderIDs, 'parentFolderId':parentFolderIDs, 'path':paths})
                else:
                    df = bytesToJson(response.content)
                return df

    @classmethod
    def search(cls, search, keywords):
        segmentFolders = segmentFolders.get_many()
        if type(keywords) != list:
            split = keywords.split(",")
            keywords = split
        if search=="any":
            result = segmentFolders.path.apply(lambda sentence: any(keyword in sentence for keyword in keywords))
            df = segmentFolders[result]
        elif search=="all":
            result = segmentFolders.path.apply(lambda sentence: all(keyword in sentence for keyword in keywords))
            df = segmentFolders[result]
        return df
