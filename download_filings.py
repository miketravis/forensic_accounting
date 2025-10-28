"""
@author: Mike Travis
"""

import os
import io
import json
import requests
import time
import zipfile
import pandas as pd

from reference import DATAPATH, HEADERS, company_competitors

URL_CIK_SUBMISSIONS = 'https://data.sec.gov/submissions/CIK{CIK_PADDED}.json'
URL_FILING = 'https://www.sec.gov/Archives/edgar/data/{CIK_UNPADDED}/{ACCESSION_NO}/{PRIMARY_DOC}'

def retrieve_filing(filings, i, cik, filings_path, date):
    """
        Retrieves an individual file from the SEC website
    """    
    filing_date = filings['filingDate'][i]
    if pd.Timestamp(filing_date) > date:
        return True
    if pd.Timestamp(filing_date) < date - pd.offsets.DateOffset(years=5):
        print("Completed downloading previous 5 years of filings.")
        return False
    form = filings['form'][i]
    accession_no = filings['accessionNumber'][i]
    primary_doc = filings['primaryDocument'][i]
    doc_content = requests.get(URL_FILING.format(CIK_UNPADDED=cik.lstrip('0'),ACCESSION_NO=accession_no.replace('-', ''),PRIMARY_DOC=primary_doc),headers=HEADERS)
    
    accession_no = accession_no.replace('_','-')
    primary_doc = primary_doc.replace('_','-')

    filename = "{filing_date}_{form}_{accession_no}_{primary_doc}".format(filing_date=filing_date,form=form,accession_no=accession_no,primary_doc=primary_doc).replace('/','-')
    filepath = os.path.join(filings_path, filename)
    if (not os.path.exists(filepath)) or overwrite:
        if doc_content.status_code == 200:
            with open(filepath, 'wb') as f:
                f.write(doc_content.content)
        else:
            print(doc_content.status_code)
    time.sleep(0.2) # Delay between requests in consideration of SEC rate limits (10 req/sec)
    return True

def download(cik, date=pd.Timestamp.today(), overwrite=False):
    """
        Downloads the preceding 5 years of a given date of SEC filings for a specified company
    """
    
    print('----- Retrieving List of Report Submissions from SEC -----')
    response_cik_submissions = requests.get(URL_CIK_SUBMISSIONS.format(CIK_PADDED=cik),headers=HEADERS)
    response_cik_submissions.raise_for_status()
    data_cik_submissions = response_cik_submissions.json()
    filings_recent = data_cik_submissions.get('filings', {}).get('recent', {}) # The 'recent' key holds the last ~1,000 filings
    print("Successfully fetched data for: {name}".format(name=data_cik_submissions.get('name')))
    print("Former Names: {former_names}".format(former_names=data_cik_submissions.get('formerNames')))
    print("Found {num_filings} RECENT filings.".format(num_filings=len(filings_recent.get('form', []))))
    print('----- Done -----\n')


    print('----- Retrieving Each Recent Filing from SEC -----')
    # if there are more than 1,000 documents then we will also need to retrieve filings from the archive folder
    # this is conditional on if the 1,000 documents are <5 years old (this check happens below)
    archive_flag = len(filings_recent.get('form', [])) >= 950 # Use 950 instead of 1,000 as a safety
    filings_path = os.path.join(DATAPATH, cik, 'filings')
    os.makedirs(filings_path, exist_ok=True) 
    for i in range(len(filings_recent.get('form', []))):
        flag = retrieve_filing(filings_recent, i, cik, filings_path, date)
        if not flag: break
    archive_flag = archive_flag and flag #if greater than 950 files and none were from before previous 5 years then check archive files
    print('----- Done -----\n')
    
    if archive_flag:
        print("----- Processing Older Filings Archives -----")
        archive_folder_info = data_cik_submissions.get('filings', {}).get('files', [])
        if not archive_folder_info:
            print("No archive files listed.")
            return
        print("Found {num_archive_folder} archive folders to process.".format(num_archive_folder=len(archive_folder_info)))
        
        for folder_info in archive_folder_info:
            last_date = pd.Timestamp(folder_info['filingTo'])
            if last_date < date - pd.offsets.DateOffset(years=5):
                continue
            archive_foldername = folder_info['name']
            archive_url = "https://data.sec.gov/submissions/{archive_foldername}".format(archive_foldername=archive_foldername)

            response_archive = requests.get(archive_url, headers=HEADERS)
            response_archive.raise_for_status()
            filings_archive = response_archive.json()
            
            print("Found {num_filings} filings in this archive folder.".format(num_filings=len(filings_archive.get('form', []))))
            for i in range(len(filings_archive.get('form', []))):
                retrieve_filing(filings_archive, i, cik, filings_path, date)
        print('----- Done -----\n')
    
    print('----- Retrieving Financial Data File from SEC -----')
    url = 'https://data.sec.gov/api/xbrl/companyfacts/CIK{CIK_NUMBER_PADDED}.json'
    response = requests.get(url.format(CIK_NUMBER_PADDED=cik),headers=HEADERS)
    response.raise_for_status()
    response = response.json()
    filename = cik +"_"+pd.Timestamp.now().strftime("%Y%m%d-%H%M%S")
    path = os.path.join(DATAPATH,cik,'financials')
    os.makedirs(path, exist_ok=True)
    file_path = os.path.join(path,'{filename}.json'.format(filename=filename))
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(response, f, ensure_ascii=False)
    print('----- Done -----\n')


def main(cik, date=pd.Timestamp.today(), competitors=False, overwrite=False):
    if competitors:
        print('----- Retrieving Company Competitors -----')
        df_competitors = company_competitors(cik)
        ciks = [cik] + df['cik'].tolist()
        print('----- Done -----\n')
    else:
        ciks = [cik]
    
    for cik in ciks:
        download(cik, date)
    
    
    
    
    

    
    
    

            
            
            

