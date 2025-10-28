"""
@author: Mike Travis
"""
import asyncio
import pandas as pd

import download_filings, accounting_methods, earnings_emotions, next_steps, aggregate_results
from reference import ticker_to_cik_mappping

def main(ticker, download_filings_flag=False, date=pd.Timestamp.today()):
    
    print('----- BEGINNING FORENSIC ANALYST PIPELINE -----\n')
    cik = ticker_to_cik_mappping(ticker)
    
    if download_filings_flag:
        print('----- DOWNLOADING SEC FILINGS FOR COMPANY AND COMPETITORS -----\n')
        download_filings.main(cik, date, competitors=True)
    
    print('----- EXAMINING FINANCIAL REPORTS FOR RED FLAGS -----\n')
    results_accounting_methods = asyncio.run(accounting_methods.main(cik))

    print('----- EXAMINING EARNINGS CALLS FOR EMOTIONAL RESPONSES -----\n')
    results_earnings_emotions = asyncio.run(earnings_emotions.main(cik))
 
    print('----- RETRIEVING AND COMPLETING NEXT STEPS -----\n')
    results_next_steps = asyncio.run(next_steps.main(cik, ticker, results_accounting_methods, results_earnings_emotions))

    print('----- AGGREGATING FOR FINAL RESULT -----\n')
    results_final = asyncio.run(aggregate_results.main(cik, results_accounting_methods, results_earnings_emotions, results_next_steps))

    #format results to .md
if __name__ == '__main__':
    main('UWMC',download_filings_flag=False)


        
        
    