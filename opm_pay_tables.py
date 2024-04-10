import datetime
import pandas as pd
import requests
from bs4 import BeautifulSoup
import numpy as np
import time
import random
from tqdm import tqdm

current_year = datetime.date.today().year

min_year = 2018
root_url = 'https://www.opm.gov/policy-data-oversight/pay-leave/salaries-wages/'
report = '/general-schedule/'

location_df_list = []

for i in range((current_year - min_year) + 1):
        
    #Construct our URL for that year
    year = min_year + i
    URL = f"{root_url}{year}{report}"
    
    print(f"Grabbing data for {year}")

    #Grab HTML
    page = requests.get(URL)
    soup = BeautifulSoup(page.content, 'html.parser')


    #Find all table names
    results = soup.find_all('a', class_ = 'Web', href=True)


    table_urls = []

    for result in results:
        table_urls.append(f"https://www.opm.gov{result.get('href')}")



    '''
    What we want to do here is grab the list of locations for that year so we know
    what our tables correspond to.
    '''

    location_tables = pd.read_html(page.text)
    location_df = []
    for location_table in location_tables:
        # Check if all desired column names are present in the DataFrame
        if all(col in location_table.columns for col in ['Pay Table']):
            location_df.append(location_table)
            
    location_df = pd.concat(location_df)
    location_df = location_df[location_df['Pay Table'] != 'Locality Pay Tables for Geographic Areas']
    location_df = pd.DataFrame(np.repeat(location_df.values, 2, axis=0))
    locations = list(location_df[0])


    year_df_list = []
    for i in tqdm(range(len(table_urls))):
        
        #Grab the first year
        df = pd.read_html(table_urls[i])[0]
        
        #Add our location
        df['location'] = locations[i]
        
        if table_urls[i].endswith('_h.aspx'):
            df['pay_type'] = 'Hourly'
        else:
            df['pay_type'] = 'Salary'
        
        df.columns = [col.replace('\xa0', ' ') for col in df.columns]
        
        
        df = df.reset_index(drop=True)
        #Data Cleaning Stuff
        num_cols = ['Grade', 'Step 1', 'Step 2', 'Step 3', 'Step 4', 'Step 5', 'Step 6', 'Step 7', 'Step 8', 'Step 9', 'Step 10']

      
        
        for column in num_cols:
            df[column] = df[column].astype(str)
            df[column] = df[column].str.replace(r'[^0-9\.]', '', regex=True)
    
        df[num_cols] = df[num_cols].apply(pd.to_numeric, errors='coerce')
        
        
        df['year'] = year
        
        year_df_list.append(df)
        
        
        #This is just me trying to not get my IP banned by OPM
        random_number_sleep = random.randint(0,1)
        time.sleep(random_number_sleep)
        
        #
        year_df = pd.concat(year_df_list)
        
    location_df_list.append(year_df)


    
location_df = pd.concat(location_df_list)

