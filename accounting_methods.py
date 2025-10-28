"""
@author: Mike Travis
"""

import os
import json
import asyncio
import pandas as pd
from bs4 import BeautifulSoup

from prompts_gemini import prompt_forensic_accounting
from call_gemini import call_gemini_api, count_tokens
from reference import DATAPATH


async def main(cik):
    """
        Takes in the annual reports of a given company and uses the Gemini API to analyze for accounting method red flags based on predetermined criteria.
    """    
    
    print('----- Retrieving Desired Financial Statements from Local -----')
    FILINGS_FOLDER = os.path.join(DATAPATH,cik,'filings')
    all_files = [f for f in os.listdir(FILINGS_FOLDER) if (f.lower().endswith(('.html', '.htm')) and (f.split("_")[1]=='10-K') and f.split("_")[2] != 'A')]
    
    filings = {} # Dictionary to store {report: report text}
    for filename in all_files:
        report = filename.split("_")[-1].split("-")[-1][:8] + " " + filename.split("_")[1]
        filepath = os.path.join(FILINGS_FOLDER, filename)
        with open(filepath, 'r', encoding='utf-8') as file:
            html_cont = file.read()
        filings[report] = BeautifulSoup(html_cont, 'html.parser').get_text()
    print('----- Done -----\n')
        
    if len(filings) < 2:
        raise ValueError('Need at Least 2 Annual Reports to Process')

    print('----- Constructing Queries -----')
    sorted_years = sorted(filings.keys())
    comparison_tasks = []
    for i in range(len(sorted_years) - 1):
        report1 = sorted_years[i]
        report2 = sorted_years[i+1]
        html1 = filings[report1]
        html2 = filings[report2]
        system_prompt, user_query = prompt_forensic_accounting({report1: html1, report2: html2})
        comparison_tasks.append(call_gemini_api(system_prompt, user_query))
    print('----- Done -----\n')
        
    print('----- Comparing Financial Statements -----')
    dict_results = {}
    if comparison_tasks:
        results = await asyncio.gather(*comparison_tasks)
        for i, result in enumerate(results):
            report1 = sorted_years[i]
            report2 = sorted_years[i+1]
            print(f"\n--- ({report1} vs {report2}) ---")
            dict_results[report1+ " vs "+ report2] = result
    print('----- Done -----\n')
    
    print('----- Saving Responses -----')
    filename = sorted_years[0].replace(' ','_')+'_to_'+sorted_years[1].replace(' ','_')+"_"+pd.Timestamp.now().strftime("%Y%m%d-%H%M%S")
    path = os.path.join(DATAPATH,cik,'results_accounting_methods','{filename}.json'.format(filename=filename))
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(dict_results, f, ensure_ascii=False)
    print('----- Done -----\n')
    
    return dict_results