# patentsmatch_bingsearchapproach
Match Patent Assignees with Compustat and SDC via Bing Search 

This data project is a systematic effort to match assignee names on USPTO patent records, sometimes abbreviated or misspelled, to all public and private firms that have been involved in alliances and M&A in Compustat and SDC Platinum databases. The current coverage runs from 1976 to 2017 for all public firms in Compustat and from 1985-2017 for all private firms in SDC Platinum. 
Our algorithm leverages the Bing web search engine and significantly improves upon fuzzy name matching, a common practice in the literature. This document presents a step-by-step guide to our searching and matching algorithm. All codes are publicly available on the GitHub page:
https://github.com/danielm-github/patentsmatch_bingsearchapproach
Matching Patent Assignees to Compustat Public Firms: 
Our procedure to match patent assignees to Compustat firms is similar to that of Autor et al. (forthcoming). The initial project started before they publish their paper and procedure. So there are a few differences between ours and theirs as detailed below. We extend their sample period from 2013 to 2017. The number of public deals (i.e., public acquirer – public target) is 6,175. Among these deals, 19% has patent records. 
Matching Patent Assignees to SDC Private Firms: 
We are the first attempt in the literature to match patent assignees to private firms using the web search engine approach. The number of private deals (i.e., public acquirer – private target) is 42,206. Among all private targets in these deals, 9.5% has patent records, giving us 4,019 observations. 

Our matching procedure has four steps.
Step 1: Download the source data: 
• Patent data from the U.S. Patent and Inventor Database (the March 2019 version from PatentsView is used here).
• Linked patent-Compustat data from the NBER Patent Data Project, which covers only patents granted by 2006.
• Linked patent-CRSP data from Kogan et al. (2017), which covers patents granted by 2010.
• Compustat North America. The relevant variables include Compustat firm ID (gvkey), firm name, firm website.
• SDC Platinum. The relevant variables include SDC deal number, firm name of the target and acquirer, and firm ID (cusip).

Step 2: Clean assignee names and Compustat/SDC firm names.
In this step, we remove punctuation and accent marks. The file “dict_char_replace.json” provides a complete list of punctuations and accent marks that we remove or replace. These choices appear to produce the best Bing search results based on our manual checks. The folder “clean_name” contains the codes for removing punctuations and accent marks in the assignee and Compustat/SDC firm names. The punctuation-free names are used as input into the Bing search in the next step.

Step 3: Use the Bing Web Search API to collect search results in the form of URLs.
a. In this step, we first create the csv input file that contains the punctuation-free firm name.
b. Run the Python program “bing_search_name.py” after adding the API key. A paid subscription to the Bing Web Search API is required when performing more than 3000 searches in a month. 
c. The Python programs will generate an output file in SQL database that contains the links, titles, and descriptions of the top 50 search results from searching the punctuation-free firm names on Bing. 
d. The folder “match” contains some simple code for cleaning the URLs collected from the Bing search.

Step 4: Match assignees to Compustat public firms and SDC private firms using names and URLs.
In the final step, we consider a patent assignee and a Compustat/SDC firm to be a match if the top five search results for the assignee and for the Compustat/SDC firm share at least two exact matches.

Reference:
Autor, David, David Dorn, Gordon H. Hanson, Gary Pisano, and Pian Shu, 2019, “Foreign Competition and Domestic Innovation: Evidence from U.S. Patents,” American Economic Review: Insights, forthcoming.

Kogan, Leonid, Dimitris Papanikolaou, Amit Seru, and Noah Stoffman, 2017, “Technological Innovation, Resource Allocation, and Growth,” The Quarterly Journal of Economics 132, 665–712.
