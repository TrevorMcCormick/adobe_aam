# Import packages
import os

class Headers:

    @classmethod
    def createHeaders(cls, traitCreate=False):
        credentials = eval((os.environ.get('aam_api_credentials')))
        request_headers = {"Authorization": "Bearer {0}".format(os.environ.get('aam_api_token')),
                          "x-api-key": credentials['client_id'],
                          "x-gw-ims-org-id": credentials['org_id']}
        if traitCreate:
            request_headers = {"Authorization": "Bearer {0}".format(os.environ.get('aam_api_token')),
                               "x-api-key": credentials['client_id'],
                               "x-gw-ims-org-id": credentials['org_id'],
                               "content-type": "application/json"}
        return request_headers