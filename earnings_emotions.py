"""
@author: Mike Travis
"""

import os
import json
import pandas as pd
import asyncio

from prompts_gemini import prompt_earnings_call_emotions
from call_gemini import call_gemini_api_files, count_tokens
from reference import DATAPATH


async def main(cik):
    """
        Takes in the pre-downloaded earnings calls of a given company and uses the Gemini API to analyze for emotional responses.
    """
    print('----- Retrieving Desired Earnings Calls from Local -----')
    AUDIO_FOLDER = os.path.join(DATAPATH,cik,'earnings_calls')
    all_files = os.listdir(AUDIO_FOLDER)
    all_files.sort()
    dates = [x.split('_')[2] for x in all_files]
    all_files = [os.path.join(AUDIO_FOLDER,f) for f in all_files]
    print('----- Done -----\n')
    
    print('----- Constructing Queries -----')
    system_prompt, user_query = prompt_earnings_call_emotions()
    tasks = []
    for file in all_files:        
        tasks.append(call_gemini_api_files(system_prompt, user_query, file))    
    print('----- Done -----\n')
        
    print('----- Analyzing Earnings Calls -----')
    dict_results = {}
    if tasks:
        results = await asyncio.gather(*tasks)
        for i, result in enumerate(results):
            print(f"\n--- ({all_files[i]}) ---")
            dict_results[dates[i]] = result
    print('----- Done -----\n')
    
    print('----- Saving Responses -----')
    filename = dates[0]+'_to_'+dates[-1]+'_'+pd.Timestamp.now().strftime("%Y%m%d-%H%M%S")
    path = os.path.join(DATAPATH,cik,'results_earnings_emotions','{filename}.json'.format(filename=filename))
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(dict_results, f, ensure_ascii=False)
    print('----- Done -----\n')
    
    return dict_results