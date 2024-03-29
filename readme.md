# Adobe Audience Manager - Python Extension

## I no longer work with Adobe Audience Manager, and I am retiring this repository, meaning you would need to fork this repository to make updates. If you would like to assume the maintainer role of the PyPi project, please contact me and I will add you as a collaborator. Thanks!

This is a Python wrapper for the Adobe Audience Manager API.

To get started [Generate a JWT Authentication using Adobe IO](https://www.adobe.io/apis/experiencecloud/analytics/docs.html#!AdobeDocs/analytics-2.0-apis/master/jwt.md)

This package requires you to create a .json document with the following credential details: client ID, client secret, tech account ID, and organization ID. In a separate file, you also need generate a public/private key pair.

credentials.json:
```json
{
    "client_id":"...",
    "client_secret": "...",
    "tech_acct_id": "...",
    "org_id": "..."
}
```

Once you have these documents, you can get install the package and login:

Terminal:
```
pip install adobe_aam
```

Python:
```py
import adobe_aam as aam
aam.Login('path/to/credentials.json', 'path/to/private.key')
```

Your authentication token should be tied to a Product Profile, which controls the actions you can execute and the objects on which you can act. If you are unable to perform an action supported by this package, the error is likely due to a permissions issue within the credentials setup.

Here are some examples:

Python:
```py
# Get traits by folder and sort
aam.Traits.get_many(folderId=12345, sortBy='createTime', descending=True)

# Get trait by sid
aam.Traits.get_one(sid=12345)

# Get traits by integration code and simplify resulting dataframe
aam.Traits.get_many(ic='code', condense=True)

# Get trait limits of account
aam.Traits.get_limits()

# Create traits from csv
aam.Traits.create_from_csv('path/to/traits_to_create.csv')
```

If you're new to Python and want to output the results of an AAM API call, you can try something like the following:

Python:
```py
import pandas as pd
output = aam.Traits.get_one(sid=12345)
output.to_csv('path/to/your_aam_output.csv')
```

### Coverage:
[Every standard API call for AAM can be found on Swagger](https://bank.demdex.com/portal/swagger/index.html#/)

| Endpoint        | Action | Coverage |
|-----------------|--------|----------|
| Traits          | Create | x        |
| Traits          | Get    | x        |
| Traits          | Update | x        |
| Traits          | Delete | x        |
| Segments        | Create | x        |
| Segments        | Get    | x        |
| Segments        | Update | x        |
| Segments        | Delete | x        |
| Trait Folder    | Get    | x        |
| Segment Folder  | Get    | x        |
| Destinations    | Create | -        |
| Destinations    | Get    | -        |
| Destinations    | Update | -        |
| Destinations    | Delete | -        |
| Derived Signals | Create | -        |
| Derived Signals | Get    | -        |
| Derived Signals | Update | -        |
| Derived Signals | Delete | -        |
| Datasources     | Create | -        |
| Datasources     | Get    | -        |
| Datasources     | Update | -        |
| Datasources     | Delete | -        |


Custom reporting will be added according to roadmap. Examples:

```py
# Get traits trends for all SIDs in a folder
aam.Reports.traits_trend(startDate="2021-02-21",
                         endDate="2021-02-23",
                         folderId=12345)
                         
# Get traits trends for one SID
aam.Reports.traits_trend(startDate="2021-02-21",
                         endDate="2021-02-23",
                         sid=[12345])
```
                  
