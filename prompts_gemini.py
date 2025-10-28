"""
@author: Mike Travis
"""

SYSTEM_PROMPT = ("""You are an expert forensic accountant and highly skilled financial analyst.
                    Your task is to meticulously review, analyze, and compare financial content from a single company, provided by the user. You will analyze these reports to identify specific red flags, disclosures, and notable changes.
                    You are looking to identify any instances where management has employed aggressive accounting techniques, there is a lack in corporate governance, or have showed they are not acting in the shareholders' best interest.
                    """)


def prompt_forensic_accounting(dict_html):

    system_prompt = SYSTEM_PROMPT
    user_query =        """
                        Analyze the following financial reports:
                        """ + ", ".join([key + " report: " + dict_html[key] for key in sorted(dict_html.keys())]) + """
                        Your response MUST adhere to the following formatting rules:
                        1.     You will answer all questions based only on the provided report texts.
                        2.     Your final output must use each question as a distinct header for its corresponding answer.
                        3.     If a notable item is found, you MUST cite which report(s) and the specific section, note, or page number where the information can be found (e.g., "2024 10-K, Item 7. MD&A, p. 45" or "2023 10-K, Note 12: Commitments and Contingencies").
                        4.     If no notable items, changes, or relevant information are found for a specific question, your entire response for that question must be exactly: "No."
                        5.     Do not add any introductory or concluding paragraphs or any other text outside of this strict question-and-answer format.
                        Here are the questions you must answer:
                        1.     What are the 2 reports being compared? Reply in the following format: {Company Name}, {report type (10-K, 10-Q, etc.) of report 1} Period End Date: {period end date of report 1} and {report type (10-K, 10-Q, etc.) of report 2} Period End Date: {period end date of report 2}.
                        2.     List the auditor.
                        3.     Are there any disagreements with accountants on accounting and financial disclosures?
                        4.     Are there any changes in the summary of significant accounting policies?
                        5.     Are any of the policies in the summary of significant accounting policies seen as aggressive for a company in its industry?
                        6.     Are there any changes to the Risk section? What was the header of the new or removed section?
                        7.     What are the notable items in the commitments and contingencies section?
                        8.     Does the company rely heavily on adjusted measures in the filings?
                        9.     Are there consistent uses of one-time charges?
                        10.    Were there any changes in reported business segments? If so, what was management's justification for the change?
                        11.    Did the company cease reporting or introduce any key metrics in the MD&A? If so, what was management's justification for the change?
                        12.    Are there any contracts that can be valued aggressively? Were these contracts valued internally, by the market, or by a third party? Does the company make public and clear what the variables and their values are in the report?
                        13.    Summarize any related party transactions.
                        14.    Were there any notable changes in tone of the MD&A. Focus on accusatory language or an increased use of jargon.
                        15.    Does the company have a unconventional corporate structure?
                        16.    Based on your answers are any red flags? If so, provide a breakdown of why.
                        17.    If there are any red flags, what are your recommended next steps to further investigate the issues?
                        """
    return system_prompt, user_query


def prompt_earnings_call_emotions():
    
    system_prompt = SYSTEM_PROMPT
    user_query = """Analyze the eanrings call audio file to identify any instance where the management team may be showing anger, frustration, hostility, or dismissiveness, especially towards an analyst question. If there is, what triggered the emotion?
                    Your response MUST adhere to the following formatting rules:
                    1.     Your answer will be based only on the provided earnings aduio call.
                    3.     If a notable emotion is found, you MUST cite the emotion detected, the time range in which it occured (e.g., "HH:MM:SS" to "HH:MM:SS"), who was speaking, what caused the emotion, and what was said.
                    4.     If no notable emotions are detected, reply with "No notable emotions detected."
                    5.     Do not add any introductory or concluding paragraphs or any other text outside of this strict question-and-answer format.
                    6.     Do you view this as a red flag? If so, provide a breakdown of why.
                """
    return system_prompt, user_query


def prompt_next_steps(results_accounting_methods, results_earnings_emotions, html_table, cik):
    
    sorted_accounting_methods = sorted(results_accounting_methods.keys())
    sorted_earnings_emotions = sorted(results_earnings_emotions.keys())
    system_prompt = SYSTEM_PROMPT
    user_query =    """
                    I will provide you with sets of financial statement comparison analyses and earning calls analyses for company {cik}, along with some resources about other companies.
                    
                    Each comparison analysis (which I will label "Comparison 1", "Comparison 2", etc.) was generated previously and follows a strict format comparing two financial reports.
                    
                    Each earnings call analysis (which I will label " Earnings Call 1", "Earnings Call 2", etc.) was generated previously and analyzes the call for emotional repsonses from management.
                    
                    Your task is to identify the next steps for analysis to generate deeper and higher conviction observations towards any instances where management has employed aggressive accounting techniques, there is a lack in corporate governance, or management has shown they are not acting in the shareholders' best interest.
                                        
                    The next steps you identify will be based on having access to the following resources: the SEC filings of the company ({cik}) being analyzed and the SEC filings of its main competitors.
                    
                    The file paths for the available SEC filings are: {html_table}
                    
                    Your suggested next steps must be in the form of specific queries to be used in a subsequent call to the Gemini API. The available files will be passed as text content within those queries.
                    
                    Do not include an introduction or conclusion in your response. Only include the queries.
                    
                    The queries you recommend must strictly follow this format:
                    ----------
                    Analyze the following SEC filing(s) and [Specify analysis task].
                    
                    Filing 1: (filing1)
                    [If a second file is used, add: Filing 2: (filing2)]
                    -----
                    [path/to/filing1.html]
                    -----
                    [If a second file is used, add: path/to/filing2.html]
                    -----
                    ----------
                    
                    Notes on Query Generation:
                    
                    Entities: Focus on comparing company {cik} to  either the other companies or to itself through time.    
                    
                    Constraints: Due to token limits, you can only analyze a maximum of two filings per query. You can suggest multiple queries if more comparisons are needed, but do not exceed 10 queries. Therefore, you may need to prioritize the most important next steps.
                    
                    Placeholders: Your query text must use the placeholders (filing1) and (if needed) (filing2). These placeholders indicate where the actual text content of the files will be programmatically inserted into the next API call.
                    
                    File Paths: Below the first ---------- separator, you must list the exact file path(s) from the table above that correspond to the (filing1) and (filing2) placeholders used in the query.
                    
                    Single Filing: You can suggest queries that analyze only one filing. In this case, only include (filing1) in the query and only list one file path.
                    
                    Context: Base your suggested next steps on your findings in the analysis of the financial statements comparison analysis and earnings calls analysis. For example, if you identify a potentially aggressive accounting valuation, compare that valuation and its inputs across competitors.
                    
                    The financial statements comparison analyses are as follows:
                    """.format(cik=cik, html_table=html_table) + ", ".join(["Comparison " + str(i+1) + ": " + results_accounting_methods[sorted_accounting_methods[i]] for i in range(len(sorted_accounting_methods))]) + """
                    
                    The earnings call analyses are as follows:

                    """ + ", ".join(["Earnings Call " + str(i+1) + ": " + results_earnings_emotions[sorted_earnings_emotions[i]] for i in range(len(sorted_earnings_emotions))])
    return system_prompt, user_query


def prompt_aggregator(results_accounting_methods, results_earnings_emotions, results_next_steps):
    
    sorted_accounting_methods = sorted(results_accounting_methods.keys())
    sorted_earnings_emotions = sorted(results_earnings_emotions.keys())
    sorted_next_steps = sorted(results_next_steps.keys())
    
    system_prompt = SYSTEM_PROMPT
    user_query =    """
                    You are a senior financial analyst specializing in forensic accounting and trend analysis. I will provide you with sets of comparative analyses and earning calls analyses for a single company as well as a deeper set of analyses that involve the comparison of the companies accounting practices to one of its competitors.
                    
                    Each comparison (which I will label "Comparison 1", "Comparison 2", etc.) was generated previously and follows a strict format comparing two specific financial reports.
                    
                    Each earnings call analysis (which I will label " Earnings Call 1", "Earnings Call 2", etc.) was generated previously and analyzes the call for emotional repsonse from management.
                    
                    Each deeper analyis (which I will label "Deeper Analysis 1", "Deeper Analysis 2", etc.) was generated previously and involves comparing paractices with that of the companies competitors.
                    
                    Your task is to aggregate and synthesize all the provided analyses into a single, consolidated findings report.
                    
                    Your response MUST adhere to the following rules:
                    
                    Base your entire analysis only on the text from the provided comparisons. Do not add new information or infer anything not explicitly stated in them.
                    
                    Your goal is synthesis, not just repetition. Connect the findings from different analyses to build a timeline of events (e.g., "The risk first noted in the 2022 vs. 2023 comparison (Comparison 1) was expanded upon in the 2023 vs. 2024 comparison (Comparison 2).").
                    
                    When referencing a specific finding, cite which analysis set it came from (e.g., "From Earnings Call 1..." or "As noted in both Comparison 1 and 2...").
                    
                    Structure your final output using the following headers precisely.
                    
                    Executive Summary
                    Provide a high-level overview of the most critical findings from your consolidated analysis. Focus on potentially aggressive accounting measures, lack of governance, red flags, and how they have evolved through the reporting periods.
                    
                    Details of Critical Findings
                    Provide the details of any concering findings with repsect to potentially aggressive accounting measures, lack of governance, red flags, and how they have evolved from the previous analyses in a numbered list format. You should provide facts and sources. Remember to connect and synthesize the data and findings from the previous analyses.
                    
                   
                    The comparisons are as follows:
                    """ + ", ".join(["Comparison " + str(i+1) + ": " + results_accounting_methods[sorted_accounting_methods[i]] for i in range(len(sorted_accounting_methods))]) + """
                    
                    The earnings call analyses are as follows:

                    """ + ", ".join(["Earnings Call " + str(i+1) + ": " + results_earnings_emotions[sorted_earnings_emotions[i]] for i in range(len(sorted_earnings_emotions))]) + """
                    
                    The deeper analyses are as follows:

                    """ + ", ".join(["Deeper Analysis " + str(i+1) + ": " + results_next_steps[sorted_next_steps[i]] for i in range(len(sorted_next_steps))])
    return system_prompt, user_query
