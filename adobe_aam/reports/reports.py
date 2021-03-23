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
                 identity="DEVICE",
                 folderId=None,
                 dataSourceId=None
                 ):
        ## Traits-trend reporting endpoint
        request_url = "https://api.demdex.com/v1/reports/traits-trend"
        
        ## Transform dateshttps://api.demdex.com/v1/traits
        startDate_unix = int(datetime.datetime.strptime(startDate, "%Y-%m-%d").timestamp())*1000
        endDate_unix = int(datetime.datetime.strptime(endDate, "%Y-%m-%d").timestamp())*1000
        
        ## Gets all trait IDs in datasource id
        if dataSourceId:
            sids = Traits.get_many(dataSourceId=dataSourceId)
            sid = list(sids['sid'])
        
        ## Runs traits get for folder ID to produce an array of trait IDs from folder ID
        if folderId:
            sids = Traits.get_many(folderId=folderId)
            sid = list(sids['sid'])
        
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
            traits_trend = pd.DataFrame(columns=columns)
            for i in range(1,len(sid)+1):
                traits_trend_row = raw_data.decode('utf-8').replace('"','').split("\n")[i].split(",")
                series = pd.Series(traits_trend_row, index = traits_trend.columns)
                traits_trend = traits_trend.append(series, ignore_index=True)
        return traits_trend