"""
@author: Mike Travis
"""

import os
import json
import asyncio
import pandas as pd

from prompts_gemini import prompt_aggregator
from call_gemini import call_gemini_api
from reference import DATAPATH

async def main(cik, results_accounting_methods, results_earnings_emotions, results_next_steps):
    
    print('----- Constructing Query -----')
    system_prompt, user_query = prompt_aggregator(results_accounting_methods, results_earnings_emotions, results_next_steps)
    print('----- Done -----\n')
    
    print('----- Aggregating Analyses -----')
    dict_results = {}
    results = await asyncio.gather(*[call_gemini_api(system_prompt, user_query)])
    for i, result in enumerate(results):
        dict_results['Aggregated'] = result
    print('----- Done -----\n')
    
    print('----- Saving Response -----')
    filename = pd.Timestamp.now().strftime("%Y%m%d-%H%M%S")
    path = os.path.join(DATAPATH,cik,'results_aggregated','{filename}.json'.format(filename=filename))
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(dict_results, f, ensure_ascii=False)
    print('----- Done -----\n')
    

    return dict_results
