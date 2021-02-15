import pandas as pd

def simplify(df):
   return(df[['sid', 'name', 'description', 'dataSourceId', 'folderId']])