# Forensic Analysis AI Pipeline using Gemini API and Python
Uses the Gemini API to analyze financial statements and earnings calls for red flags.

Process begins from main.py.

This project specifically analyzes United Wholesale Mortgage Corp (UWMC, 0001783398 in the data folder), but the main idea would be to run the process over an equity universe and the score and rank the results.

The AI forensic analysis Python pipeline process used here is as follows:
  1.	Use the Gemini API to analyze UWMC’s past 5 years of 10-K’s based on a pre-determined set of questions and tasks.
  2.	Use the Gemini API to analyze UWMC’s past 5 years of earnings call .mp3 files to identify instances of anger, frustration, hostility, or dismissiveness.
  3.	Based on the findings from above, the Gemini API constructs a set of next steps and then conducts those steps itself using provided resources. At this step, the AI is provided a database of its own SEC filings and of its main competitors’ SEC filings from the past 5 years. It can choose to use any of the filings for its analysis. There are many other resources that could be provided here such as Google search, court documents, alternative data, etc.
  4.	Gemini writes a report on its most critical findings.

# Output File Details
- final_output.md: The final report on the most critical findings.
- accounting_methods.md: The responses to the pre-determined set of questions and tasks from comparing subsequent annual reports.
- earnings_emotions.md: The responses for each earnings call on whether it contained instances of anger, frustration, hostility, or dismissiveness.
- next_steps.md: The queries Gemini constructed when tasked with identifying next steps by reviewing the account_methods and earnings_emotions texts.

# Next Steps
There are many ways this project can be taken further.
  1. Reiterate over Step 3 either X amount of times or until the AI model decides it's satisfied with it's research.
  2. Analyze and evaluate various AI models over different parts of the process. Opimal outcome would likely have multiple AI models used throughout the process.
  3. Add quantitative factors. This process focuses on mores so on the qualitative factors to focus on showcasing the AI's ability.
  4. Expand further on the pre-determined set of questions and tasks.
