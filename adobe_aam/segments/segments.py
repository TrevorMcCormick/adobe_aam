# Import packages
import os
import json
from datetime import datetime, timedelta
import requests
import jwt
import numpy as np
import pandas as pd

from adobe_aam.helpers.headers import *
from adobe_aam.helpers.simplify import *

class Segments:
    @classmethod
    def get_many(cls,
            ## These are all of the Adobe arguments
            containssegment=None,
            folderId=None,
            includePermissions=None,
            permission=None,
            integrationCode=None,
            updatedSince=None,
            dataSourceId=None,
            mergeRuleDataSourceId=None,
            pid=None,
            includesegmentDataSourceIds=None,
            includeMetrics=None,
            ## These are all of the custom arguments
            condense=None
                ):
            """
                Get multiple AAM Segments.
                Args:
                    containssegment: (int) segment ID.
                    folderId: (int) Limit segments returned to Folder ID.
                    includePermissions: (bool) includes Permissions column.
                    permission: (str) Filters by permission type; ex: "READ".
                    integrationCode: (str) Filters by integrationCode.
                    updatedSince: (int) Filters by updateTime, by UNIX timestamp.
                    dataSourceId: (int) Filters by Data Source ID.
                    mergeRuleDataSourceId: (int) Filters by mergeRuleDataSourceId.
                    pid: (int) Your AAM enterprise ID.
                    includesegmentDataSourceIds: (bool) Includes includesegmentDataSourceIds column.
                    includeMetrics: (bool) Includes many metrics columns by segment.
                    condnse: (bool) Limit cols returned in df.
                    includeUsers: (bool) Include mapping of user IDs to names and email addresses.
                Returns:
                    df of all segments to which the AAM API user has READ access.
            """
            ## segments endpoint
            request_url = "https://api.demdex.com/v1/segments/"
            request_data = {"containssegment":containssegment,
                "folderId":folderId,
                "includePermissions":includePermissions,
                "permission":permission,
                "integrationCode":integrationCode,
                "updatedSince":updatedSince,
                "dataSourceId":dataSourceId,
                "mergeRuleDataSourceId":mergeRuleDataSourceId,
                "pid":pid,
                "includesegmentDataSourceIds":includesegmentDataSourceIds,
                "type":type,
                "includeMetrics":includeMetrics
                }
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
                ## This begins the PDM section for additional functionality
                ## Simplify: limits columns
                if condense:
                    df = df[['name', 'description',
                         'sid', 'folderId', 'dataSourceId',
                         'createTime', 'updateTime']]
                return df

    @classmethod
    def get_one(cls,
                sid,
                limitCols=None,
                includeMetrics=None,
                includeExprTree=None,
                includesegmentDataSourceIds=None,
                includeInUseStatus=None,
                ## These are all of the custom arguments
                condense=None
               ):
            """
               Get multiple AAM Segments.
               Args:
                   sid: (int) Segment ID.
                   limitCols: (bool) List of df columns to subset.
                   includeMetrics: (bool) Includes many metrics columns by segment.
                   includeExprTree: (bool) Includes segments, mappablesegments, codeViewOnly, and expressionTree columns.
                   includesegmentDataSourceIds: (bool) Includes includesegmentDataSourceIds column.
                   includeInUseStatus: (bool) Includes inUse column.
                   includeMappedsegments: (bool) Include list of segments included in segment.
               Returns:
                   Transposed df of one segment to which the AAM API user has READ access.
            """
            ## segments endpoint
            request_url = "https://api.demdex.com/v1/segments/{0}".format(str(sid))
            request_data = {"includeMetrics":includeMetrics,
                "includeExprTree":includeExprTree,
                "includesegmentDataSourceIds":includesegmentDataSourceIds,
                "includeInUseStatus":includeInUseStatus
               }
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
                df = df.iloc[0]
                ## Change time columns from unix time to datetime
                df['createTime'] = pd.to_datetime(df['createTime'], unit='ms')
                df['updateTime'] = pd.to_datetime(df['updateTime'], unit='ms')
                ## This begins the PDM section for additional functionality
                ## Simplify: limits columns
                if condense:
                    df = df[['name', 'description',
                         'sid', 'folderId', 'dataSourceId',
                         'createTime', 'updateTime']]
                return df

    @classmethod
    def create(cls,segments):
            """
               Create multiple AAM Segments.
               Args:
                   segments: (Excel or csv) List of segments to create.
               Returns:
                   String with segment create success and # of segments created.
            """
    @classmethod
    def create_from_csv(cls, file_path):
        ## Segments endpoint for create is old demdex URL
        request_url = "https://api.demdex.com/v1/segments/"
        ## Required columns for API call
        reqd_cols = pd.DataFrame(columns=['dataSourceId', 'name', 'segmentRule', 'folderId'])
        ## Load csv into pandas df
        if file_path.endswith('.csv'):
            df = pd.read_csv(file_path, engine='python')
        else:
            raise Exception('File type is not csv.')
        ## Check for reqd cols
        col_check = all(item in reqd_cols.columns for item in df.columns)
        if not col_check:
            reqd_cols.to_csv('aam_segment_create_template.csv', index=False)
            raise Exception('Missing one or more required columns. Please re-upload file with template.')
        segments_as_dict = df.to_dict(orient='records')
        
        ## Declare counter vars
        num_segments_in_file = len(segments_as_dict)
        num_successful_segments = 0
        
        ## Handle for bad Segments
        unsuccessful_segments = pd.DataFrame(columns=df.columns)
               
        for segment in segments_as_dict:
            segment_json = json.dumps(segment)
            response = requests.post(url = request_url,
                                    headers = Headers.createHeaders(json=True),
                                    data=segment_json)
            ## Print error code if get request is unsuccessful
            if response.status_code != 201:
                print("Attempt to create segment {0} was unsuccessful. \nError code {1}. \nReason: {2}".format(segment['name'], response.status_code, response.content.decode('utf-8')))
                unsuccessful_segments = unsuccessful_segments.append(segment, ignore_index=True)
            else:
                num_successful_segments += 1
        
        ## Return bad Segments
        if len(unsuccessful_segments) > 0:
            unsuccessful_segments.to_csv('aam_unsuccessful_segments.csv', index=False)
            print('Unsuccessful segments written to aam_unsuccessful_segments.csv')
        return "{0} of {1} segments in file successfully created.".format(num_successful_segments, num_segments_in_file)



    @classmethod
    def get_limits(cls):
        ## segments endpoint for limits
        request_url = "https://api.demdex.com/v1/segments/limits"
        
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
    def delete_many(cls, file_path):
        ## Segments endpoint for delete is old demdex URL
        request_url = "https://api.demdex.com/v1/segments/"
        ## Required columns for API call
        reqd_cols = pd.DataFrame(columns=['sid'])
        ## Load csv into pandas df
        if file_path.endswith('.csv'):
            df = pd.read_csv(file_path, engine='python')
        else:
            raise Exception('File type is not csv.')
        ## Check for reqd cols
        if list(df.columns) != list(reqd_cols.columns):
            reqd_cols.to_csv('aam_segment_delete_template.csv', index=False)
            raise Exception('Column name should be sid. Please re-upload file with template.')
        
        ## Declare counter vars
        num_segments_in_file = len(df)
        num_successful_segments = 0
        
        ## Handle for bad segments
        unsuccessful_segments = pd.DataFrame(columns=['sid'])
               
        for index, row in df.iterrows():
            response = requests.delete(url = request_url+'/{0}'.format(row['sid']),
                                     headers = Headers.createHeaders())
            
            ## Print error code if get request is unsuccessful
            if response.status_code != 204:
                print("Attempt to delete segment {0} was unsuccessful. \nError code {1}. \nReason: {2}".format(row['sid'], response.status_code, response.content.decode('utf-8')))
                unsuccessful_segments = unsuccessful_segments.append(row, ignore_index=True)
            else:
                num_successful_segments += 1
        
        ## Return bad segments
        if len(unsuccessful_segments) > 0:
            unsuccessful_segments.to_csv('aam_unsuccessful_segments.csv', index=False)
            print('Unsuccessful segments written to aam_unsuccessful_segments.csv')
        return "{0} of {1} segments in file successfully deleted.".format(num_successful_segments, num_segments_in_file)

    @classmethod
    def delete_one(cls, sid, ic=None):
        ## segments endpoint for delete is old demdex URL
        request_url = "https://api.demdex.com/v1/segments/{0}".format(str(sid))
        if ic:
            request_url = "https://api.demdex.com/v1/segments/{0}".format(str(ic))
        
        response = requests.delete(url = request_url,
                                   headers = Headers.createHeaders())     
        if ic:
            if response.status_code != 204:
                print("Attempt to delete segment with ic={0} was unsuccessful. \nError code {1}. \nReason: {2}".format(ic, response.status_code, response.content.decode('utf-8')))
            else:
                return "segment with ic={0} successfully deleted.".format(ic)
        else:
            if response.status_code != 204:
                print("Attempt to delete segment {0} was unsuccessful. \nError code {1}. \nReason: {2}".format(sid, response.status_code, response.content.decode('utf-8')))
            else:
                return "segment {0} successfully deleted.".format(sid)    
    
    @classmethod
    def update_many(cls, file_path):
        ## Required columns for API call
        reqd_cols = pd.DataFrame(columns=['sid'])
        ## Load csv into pandas df
        if file_path.endswith('.csv'):
            df = pd.read_csv(file_path, engine='python')
        else:
            raise Exception('File type is not csv.')
        ## Check for reqd cols
        col_check = all(item in df.columns for item in reqd_cols.columns)
        if not col_check:
            reqd_cols.to_csv('aam_segment_update_template.csv', index=False)
            raise Exception('Missing sid columns. Please re-upload file with template.')
        
        ## Declare counter vars
        num_segments_in_file = len(df)
        num_successful_segments = 0
        
        ## Handle for bad segments
        unsuccessful_segments = pd.DataFrame()
        
        for index, row in df.iterrows():
            response = None
            ## Get current segment info
            current_segment_info = Segments.get_one(sid=row['sid'])
            current_segment_info = current_segment_info[['name', 'dataSourceId', 'folderId', 'sid', 'segmentRule']]
            current_segment_info = current_segment_info.to_frame().T
            ## Determine diff of given file and segment GET request
            col_diff = list(current_segment_info.columns.difference(df.columns))
            current_segment_info = current_segment_info[col_diff]
            current_segment_info['sid'] = row['sid']
            segment_to_update = row.to_frame().T
            ## Merge required cols if they do not exist in CSV
            updated_segment = pd.merge(segment_to_update, current_segment_info)
            ## Get request data
            segment_as_dict = updated_segment.to_dict(orient='records')[0]
            for key in segment_as_dict:
              if isinstance(segment_as_dict[key], (int, np.integer)):
                segment_as_dict[key] = int(segment_as_dict[key])
            sid = segment_as_dict['sid']
            segment_json = json.dumps(segment_as_dict)  
            request_url = "https://api.demdex.com/v1/segments/{0}".format(sid)
            response = requests.put(url = request_url,
                                    headers = Headers.createHeaders(json=True),
                                    data = segment_json)
            if response.status_code == 200:
              num_successful_segments += 1       
            else:
              print(f'Attempt to update segment {row["sid"]} was unsuccessful.')
              unsuccessful_segments = unsuccessful_segments.append(row, ignore_index=True)
                
 
        ## Return bad segments
        if len(unsuccessful_segments) > 0:
            unsuccessful_segments.to_csv('aam_unsuccessful_segments.csv', index=False)
            print('Unsuccessful segments written to aam_unsuccessful_segments.csv')
        return "{0} of {1} segments in file successfully updated.".format(num_successful_segments, num_segments_in_file)