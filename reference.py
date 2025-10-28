"""
@author: Mike Travis
"""

import os
DATAPATH = os.path.join('C:\\', 'Users', 'Mike Travis', 'Documents', 'gemini','data')

URL_TICKERS = 'https://www.sec.gov/files/company_tickers.json'

HEADERS = {
        'User-Agent': 'Personal MikeTravis mike.s.travis1@gmail.com'
        }

def ticker_to_cik_mappping(ticker):
    import requests
    response_tickers = requests.get(URL_TICKERS,headers=HEADERS)
    response_tickers.raise_for_status()
    data_tickers = response_tickers.json()
    ticker_to_cik = {
                company['ticker']: str(company['cik_str']).zfill(10)
                for company in data_tickers.values()
                if 'ticker' in company and 'cik_str' in company
            }
    return ticker_to_cik[ticker]

def data_filings(cik):
    import os
    import pandas as pd
    from reference import DATAPATH
    
    FILINGS_FOLDER = os.path.join(DATAPATH,cik,'filings')
    all_files = os.listdir(FILINGS_FOLDER)
    data = []
    for file in all_files:
        file_path = os.path.join(FILINGS_FOLDER,file)
        report_date = pd.Timestamp(file.split("_")[0])
        report_type = file.split("_")[1]
        data.append([report_date,report_type,file_path])
    return pd.DataFrame(data,columns=['report_date','report_type','file_path'])

def data_earnings_calls(cik):
    import os
    import pandas as pd
    from reference import DATAPATH
    
    AUDIO_FOLDER = os.path.join(DATAPATH,cik,'earnings_calls')
    all_files = os.listdir(AUDIO_FOLDER)
    all_files.sort()
    data = []
    for file in all_files:
        file_path = os.path.join(FILINGS_FOLDER,file)
        call_date = pd.Timestamp(file.split("_")[0])
        data.append([call_date,file_path])
    return pd.DataFrame(data,columns=['call_date','file_path'])

def company_info():
    import pandas as pd
    df = pd.read_csv('company_info.csv')
    df['cik'] = df['cik'].apply(lambda x: str(x).zfill(10))
    df['ts'] = df['ts'].apply(pd.Timestamp)
    df = df.sort_values(by=['ts'],ascending=False).drop_duplicates('cik')
    return df

def company_competitors(cik):
    import ast
    import pandas as pd
    df_info = company_info()
    df_info = df_info[df_info['cik']==cik]
    list_competitors = ast.literal_eval(df_info['competitors'][0])
    list_competitors = [x.strip() for x in list_competitors]
    list_competitors = [[ticker,ticker_to_cik_mappping(ticker)] for ticker in list_competitors]
    return pd.DataFrame(list_competitors,columns=['ticker','cik'])
