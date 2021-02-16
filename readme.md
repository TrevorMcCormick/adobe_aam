# Adobe Audience Manager - Python Extension

This is a Python wrapper for the Adobe Audience Manager API.

To get started [Generate a JWT Authentication using Adobe IO](https://www.adobe.io/apis/experiencecloud/analytics/docs.html#!AdobeDocs/analytics-2.0-apis/master/jwt.md)

This package requires you to create a .json document with the following credential details: client ID, client secret, tech account ID, tech account email, and organization ID. In a separate file, you also need generate a public/private key pair.

Once you have these documents, you can get install the package and login:

```py
import adobe_aam_python as aam
aam.Login('path/to/credentials.json', 'path/to/private.key')
```

Your authentication token should be tied to a Product Profile, which controls the actions you can execute and the objects on which you can act. If you are unable to perform an action supported by this package, the error is likely due to a permissions issue within the credentials setup.

Here are some examples:

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

```py
import pandas as pd
output = aam.Traits.get_one(sid=12345)
output.to_csv('path/to/your_aam_output.csv')
```