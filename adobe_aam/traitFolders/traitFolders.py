# Import packages
import os
import json
from datetime import datetime, timedelta
import requests
import jwt
import pandas as pd
import warnings
from pandas.core.common import SettingWithCopyWarning

warnings.simplefilter(action="ignore", category=SettingWithCopyWarning)

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


class TraitFolders:
    @classmethod
    def get_many(cls):
            """
                Get multiple AAM TraitFolders.
                Args:
                    includeThirdParty: (bool) Includes 3rd Party TraitFolders (defaults True).
                    dataSourceId: (int) Filter TraitFolders by Data Source ID.
                Returns:
                    df of all folderIds, parentFolderIds, and paths to which the AAM API user has READ access.
            """
            request_url = "https://api.demdex.com/v1/folders/traits"
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
            parent_folders = []
            for index, row in df.iterrows():
              count = -1
              for char in row['path']:
                  if char == '/':
                      count = count + 1
              parent_folders.append(count)
            df['parent_folders'] = parent_folders
            child_folders = []
            num_child_folders = df['parentFolderId'].value_counts().to_dict()
            for index, row in df.iterrows():
              if row['folderId'] in num_child_folders.keys():
                child_folders.append(num_child_folders[row['folderId']])
              else:
                child_folders.append(0)
            df['child_folders'] = child_folders
            return df

    @classmethod
    def get_one(cls,
        folderId,
        get_children=None,
        get_parents=None):
            """
                Get one AAM TraitFolder.
                Args:
                    includeSubFolders: (bool) Scans subfolders and returns in df.
                Returns:
                    df of one folderId, with optional subfolders, provided the AAM API user has READ access.
            """
            df = TraitFolders.get_many()
            df1 = df[df['folderId']==folderId]
            df1['level'] = ['0'] * len(df1)
            if get_children:
              df_children = df[df['parentFolderId']==folderId]
              df_children['level'] = ['-1'] * len(df_children)
              df1 = df1.append(df_children)
            if get_parents:
              df_parents = df[df['folderId']==df1['parentFolderId'].iloc[0]]
              df_parents['level'] = ['+1'] * len(df_parents)
              df1 = df1.append(df_parents)
            return df1

    @classmethod
    def search(cls, search, keywords):
        traitFolders = TraitFolders.get_many()
        if type(keywords) != list:
            split = keywords.split(",")
            keywords = split
        if search=="any":
            result = traitFolders.path.apply(lambda sentence: any(keyword in sentence for keyword in keywords))
            df = traitFolders[result]
        elif search=="all":
            result = traitFolders.path.apply(lambda sentence: all(keyword in sentence for keyword in keywords))
            df = traitFolders[result]
        return df
