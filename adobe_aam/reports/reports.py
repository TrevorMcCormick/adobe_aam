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
        
        ## Gets all trait IDs in datasource id
        if dataSourceId:
            sids = Traits.get_many(dataSourceId=dataSourceId)
            sid = list(sids['sid'])
        
        ## Runs traits get for folder ID to produce an array of trait IDs from folder ID
        if folderId:
            sids = Traits.get_many(folderId=folderId)
            sid = list(sids['sid'])
        
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
                    # The code below handles for trait names with commas in them.
                    try:
                        traits_trend_row = raw_data.decode('utf-8').replace('"','').split("\n")[1].split(",")
                        trait_name = []
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
                            series = pd.Series(traits_trend_new, index = traits_trend_identity.columns)
                        else:
                            series = pd.Series(traits_trend_row, index = traits_trend_identity.columns)
                        traits_trend_identity = traits_trend_identity.append(series, ignore_index=True)
                    except:
                        traits_trend_row = raw_data.decode('utf-8').replace('"','').split("\n")[i].split(",")
                        print('Trait ID {0} has commas in weird spots.'.format(traits_trend_row[0]))
            return traits_trend_identity
        
        traits_trend_device = traits_trend_identity('DEVICE')
        traits_trend_xdevice = traits_trend_identity('CROSS_DEVICE')
        traits_trend_xdevice_metrics = traits_trend_xdevice.iloc[:,4:]
        traits_trend_merged = pd.merge(traits_trend_device, traits_trend_xdevice_metrics, left_index=True, right_index=True)
        return traits_trend_merged