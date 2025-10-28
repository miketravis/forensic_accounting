"""
@author: Mike Travis
"""

import os
import json
import ast
import asyncio
import pandas as pd
from bs4 import BeautifulSoup

from reference import DATAPATH, ticker_to_cik_mappping, data_filings, company_competitors
from prompts_gemini import prompt_next_steps, SYSTEM_PROMPT
from call_gemini import call_gemini_api

async def main(cik, ticker, results_accounting_methods, results_earnings_emotions):
    """
        Decides next steps for the analysis and then conducts those steps on its own using the Gemini API.
            Takes in the accounting methods and earnings calls analyses to identify potential further analysis using the Gemini API and then conducts that analyis based on provided resources.
            The resources provided in this case are competitors its competitors SEC filings as well as its SEC filings.
    """
    
    print('----- Retrieving Company Info and Files -----')
    df_competitors = company_competitors(cik).set_index('cik')
    df_competitors.loc[cik] = ticker
    datas = []
    for temp_cik in df_competitors.index:
        data = data_filings(temp_cik)
        data['ticker'] = df_competitors.loc[temp_cik,'ticker']
        data['cik'] = temp_cik
        datas.append(data)
        df = pd.concat(datas)
    print('----- Done -----\n')
    
    print('----- Retrieving Queries for Next Steps and Formatting -----')
    system_prompt, user_query = prompt_next_steps(results_accounting_methods, results_earnings_emotions, df.to_html(), cik)
    result = await asyncio.gather(*[call_gemini_api(system_prompt, user_query)])
    results = result[0].split('----------')[1:]
    results = [res for res in results if len(res)>2] # some of the splits are "\n", so can remove those
    queries = []
    for resp in results:
        try:
            resp = resp.split('-----')
            user_query = resp[0]
            file_path = resp[1].removesuffix('\n').removeprefix('\n')
            with open(file_path, 'r', encoding='utf-8') as f:
                html_cont = f.read()
                user_query = user_query.replace('(filing1)',BeautifulSoup(html_cont, 'html.parser').get_text())
            
            if len(resp)>2:
                if len(resp[2]) >2:
                    file_path = resp[2].removesuffix('\n').removeprefix('\n')
                    with open(file_path, 'r', encoding='utf-8') as f:
                        html_cont = f.read()
                        user_query = user_query.replace('(filing2)',BeautifulSoup(html_cont, 'html.parser').get_text())
            queries.append(user_query)
        except Exception as e:
            print(e)
    dict_queries = {'Query '+str(i+1    ): queries[i] for i in range(len(queries))}
    path = os.path.join(DATAPATH,cik,'queries_next_steps','{}_{}.json'.format(cik,pd.Timestamp.now().strftime("%Y%m%d-%H%M%S")))
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(dict_queries, f, ensure_ascii=False, indent=4)
    print('----- Done -----\n')
    
    print('----- Constructing Tasks for Next Steps -----')
    sorted_queries = sorted(dict_queries.keys())
    tasks = []
    for i in range(len(sorted_queries)):
        tasks.append(call_gemini_api(system_prompt, dict_queries[sorted_queries[i]]))
    print('----- Done -----\n')
        
    print('----- Performing Next Steps Analysis -----')
    dict_results = {}
    if tasks:
        results = await asyncio.gather(*tasks)
        for i, result in enumerate(results):
            print("\n--- {} ---".format(sorted_queries[i]))
            dict_results[sorted_queries[i]] = result
    print('----- Done -----\n')
    
    print('----- Saving Responses -----')
    filename = cik +"_"+pd.Timestamp.now().strftime("%Y%m%d-%H%M%S")
    path = os.path.join(DATAPATH,cik,'results_next_steps','{filename}.json'.format(filename=filename))
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(dict_results, f, ensure_ascii=False)
    print('----- Done -----\n')
    
    return dict_results