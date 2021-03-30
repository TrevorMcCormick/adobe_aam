# Import packages
from adobe_aam.helpers.headers import *
from adobe_aam.traits.traits import *
import os
import json
import time
import datetime
import requests
import jwt
import pandas as pd


class Reports:
## https://bank.demdex.com/portal/swagger/index.html#/Reporting%20API

    @classmethod
    def traits_trend(cls,
                 ## These are all of the Adobe arguments
                 startDate=None,
                 endDate=None,
                 interval="1D",
                 sid=None,
                 ## These are custom arguments
                 folderId=None,
                 dataSourceId=None
                 ):
        ## Traits-trend reporting endpoint
        request_url = "https://api.demdex.com/v1/reports/traits-trend"
        
        ## Transform dateshttps://api.demdex.com/v1/traits
        startDate_unix = int(datetime.datetime.strptime(startDate, "%Y-%m-%d").timestamp())*1000
        endDate_unix = int(datetime.datetime.strptime(endDate, "%Y-%m-%d").timestamp())*1000
        
        ## Gets details for just one sid
        if sid:
            sid_extra = Traits.get_one(sid=sid[0])[["traitRule", "traitRuleVersion", "type", "backfillStatus"]]
        
        ## Gets all trait IDs in datasource id
        if dataSourceId:
            sids = Traits.get_many(dataSourceId=dataSourceId, includeDetails=True)
            sid = list(sids['sid'])
            sid_extra = sids[["traitRule", "traitRuleVersion", "type", "backfillStatus"]]
        
        ## Runs traits get for folder ID to produce an array of trait IDs from folder ID
        if folderId:
            sids = Traits.get_many(folderId=folderId)
            sid = list(sids['sid'])
            sid_extra = sids[["traitRule", "traitRuleVersion", "type", "backfillStatus"]]
        
        def traits_trend_identity(identity):
            request_data = {"startDate":startDate_unix,
                            "endDate":endDate_unix,
                            "interval":interval,
                            "sids":[sid],
                            "traitMetricsType":identity}

            ## Make request 
            general_headers = Headers.createHeaders()
            reporting_headers = {"accept": "application/json, text/plain, */*"}

            response = requests.post(url = request_url,
                                    headers = {**general_headers, **reporting_headers},
                                    data = request_data) 
            ## Print error code if get request is unsuccessful
            if response.status_code != 200:
                print(response.content)
            else:
                ## Make a dataframe out of the response.json object
                raw_data = response.content
                columns = raw_data.decode('utf-8').replace('"','').split("\n")[0].split(",")
                for col in range(4, len(columns)):
                    columns[col] = '{0}_'.format(identity) + columns[col]
                traits_trend_identity = pd.DataFrame(columns=columns)
                for i in range(1,len(sid)+1):
                    traits_trend_row = raw_data.decode('utf-8').replace('"','').split("\n")[i].split(",")
                    trait_name = []
                    series = None
                    if len(traits_trend_row) > 13:
                        for i in traits_trend_row:
                            if ' ' in i:
                                trait_name.append(traits_trend_row.index(i))
                                traits_trend_row_left = traits_trend_row[0:3]
                                traits_trend_row_mid = traits_trend_row[trait_name[0]:trait_name[-1]+1]
                                traits_trend_row_mid = ','.join(traits_trend_row_mid)
                                traits_trend_row_right = traits_trend_row[trait_name[-1]+1:]
                                traits_trend_name = []
                                traits_trend_name.append(traits_trend_row_mid)
                                traits_trend_new = traits_trend_row_left + traits_trend_name + traits_trend_row_right
                                try:
                                    series = pd.Series(traits_trend_new, index = traits_trend_identity.columns)
                                except:
                                    pass
                    else:
                        series = pd.Series(traits_trend_row, index = traits_trend_identity.columns)
                    traits_trend_identity = traits_trend_identity.append(series, ignore_index=True)
            return traits_trend_identity
        traits_trend_device = traits_trend_identity('DEVICE')
        traits_trend_xdevice = traits_trend_identity('CROSS_DEVICE')
        traits_trend_xdevice_metrics = traits_trend_xdevice.iloc[:,4:]
        traits_trend_merged = pd.merge(traits_trend_device, traits_trend_xdevice_metrics, left_index=True, right_index=True)
        traits_trend_merged_details = pd.merge(traits_trend_merged, sid_extra, left_index=True, right_index=True)
        
        
        return traits_trend_merged_details
    
    @classmethod
    def general(cls,
                 ## These are all of the Adobe arguments
                 datesThrough=None,
                 sid=None,
                 ## These are custom arguments
                 folderId=None,
                 dataSourceId=None
                 ):
        ## Traits-trend reporting endpoint
        request_url = "https://audience-manager.adobe.com/portal/api/v1/reports/traits-for-date?no-cache=true"
        
        ## Transform dates
        datesThrough = int(datetime.datetime.strptime(datesThrough, "%Y-%m-%d").timestamp())*1000
        
        ## Gets details for just one sid
        if sid:
            sid_extra = Traits.get_one(sid=sid[0])[["traitRule", "traitRuleVersion", "type", "backfillStatus"]]
        
        ## Gets all trait IDs in datasource id
        if dataSourceId:
            sids = Traits.get_many(dataSourceId=dataSourceId, includeDetails=True)
            sid = list(sids['sid'])
            sid_extra = sids[["traitRule", "traitRuleVersion", "type", "backfillStatus"]]
        
        ## Runs traits get for folder ID to produce an array of trait IDs from folder ID
        if folderId:
            sids = Traits.get_many(folderId=folderId)
            sid = list(sids['sid'])
            sid_extra = sids[["traitRule", "traitRuleVersion", "type", "backfillStatus"]]
        
        request_data = {"date":datesThrough,
                        "sids":[sid],
                        "pageSize":100000,
                        "page":0}

        ## Make request 
        general_headers = Headers.createHeaders()
        reporting_headers = {"accept": "application/json, text/plain, */*"}
        response = requests.post(url = request_url,
                                headers = {**general_headers, **reporting_headers},
                                data = request_data) 
        ## Print error code if get request is unsuccessful
        if response.status_code != 200:
            print(response.content)
        else:
            ## Make a dataframe out of the response.json object
            raw_data = response.content
            columns = raw_data.decode('utf-8').replace('"','').split("\n")[0].split(",")
            general_report = pd.DataFrame(columns=columns)
            for i in range(1,len(sid)+1):
                series = None
                general_report_row = raw_data.decode('utf-8').replace('"','').split("\n")[i].split(",")
                if len(general_report_row) > 46:
                    trait_name = []
                    for i in general_report_row:
                        if ' ' in i:
                            trait_name.append(general_report_row.index(i))
                            general_report_row_left = general_report_row[0:3]
                            general_report_row_mid = general_report_row[trait_name[0]:trait_name[-1]+1]
                            general_report_row_mid = ','.join(general_report_row_mid)
                            general_report_row_right = general_report_row[trait_name[-1]+1:]
                            general_name = []
                            general_name.append(general_report_row_mid)
                            general_new = general_report_row_left + general_name + general_report_row_right
                            try:
                                series = pd.Series(general_new, index = general_report.columns)
                            except:
                                pass
                else:
                    series = pd.Series(general_report_row, index = general_report.columns)
                general_report = general_report.append(series, ignore_index=True)
        general_report_details = pd.merge(general_report, sid_extra, left_index=True, right_index=True)
        return general_report_details
                        