from bs4 import BeautifulSoup
import requests
import pandas as pd
import time
from datetime import datetime
from tqdm import tqdm
import numpy as np

current_year = datetime.now().year

#Get the URL for the current year
URL = f'https://www.opm.gov/special-rates/{current_year}/IndexByAgencies.aspx'

#Get webpage data
r=requests.get(URL)
soup=BeautifulSoup(r.content, "lxml")

# Find all rows in the table
tbl = soup.findAll('table')[-1]
rows = tbl.find_all('tr')

# Find what row corresponds to the USDA
agency_df = pd.read_html(str(soup.find_all('table')))[-1]
specific_row = rows[agency_df[agency_df['Agency'] == 'AG'].index[0] + 1]
cell_with_hyperlink = specific_row.find_all('td')[-1]


hyperlinks = []
for link in cell_with_hyperlink.find_all('a'):
    if link['class'] == []:
        link_url = link['href']
        link_text = link.get_text()
        hyperlinks.append((link_text, link_url))

hyperlinks = ['https://www.opm.gov/' + hyperlink[1] for hyperlink in hyperlinks]


special_rate_tables = []

for hyperlink in tqdm(hyperlinks):
    #Get the data on the webpage
    r = requests.get(hyperlink)
    soup=BeautifulSoup(r.content, "lxml")

    table = soup.find_all('table')
    
    #Get every dataframe from the page
    df_list = pd.read_html(str(table))

    #Grab the specific tables we need by looking at column names
    occ_series = [df for df in df_list if df.columns[0] == 'SERIES'][0]
    pay_table = [df for df in df_list if df.columns[0] == 'Grade'][0]
    location_table = [df for df in df_list if df.columns[0] == 'STATE CODE'][0]

    #Get the catesian product
    all_df = pd.merge(occ_series, pay_table, how = 'cross')
    all_df = pd.merge(all_df, location_table, how = 'cross')


    #Grab the effective date for when the special rate is effective
    try:
        effective_date = soup.select('#ctl01_ctl00_MainContentDiv > div > p:nth-child(5) > strong')[0].text.strip()
        
    except:
        effective_date = soup.select('#ctl01_ctl00_MainContentDiv > div > p:nth-child(6) > strong')[0].text.strip()
        
        
    all_df['effective_date'] = effective_date
    
    all_df['year'] = current_year

    special_rate_tables.append(all_df)

    time.sleep(np.random.uniform(1, 2))


special_rate_table = pd.concat(special_rate_tables)


special_rate_table.to_csv(r'/Users/erfan/Desktop/Python_Directory/special_rate_tables.csv', index=False)
