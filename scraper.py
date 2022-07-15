from bs4 import BeautifulSoup
import requests
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
# %matplotlib inline


def get_base_url(job, year):
    return f"https://h1bdata.info/index.php?job={job}&year={year}"

jobs = ["Data Scientist", "Senior Data Scientist", "Software Engineer", "Senior Software Engineer", "Software Developer", "Senior Software Developer"]
# jobs = ["Data Scientist"]


def h1b_scraper():
    data = []
    for job in jobs:
        for year in range(2019, 2020):
            year = str(year)
            url = get_base_url(job, year)
            response = requests.get(url)
            c = response.content
            soup = BeautifulSoup(c, 'html.parser')
            my_table = soup.find('table', attrs = {'class': 'tablesorter tablesorter-blue hasStickyHeaders'})
            for x in my_table.find_all('td'):
                data.append(x.get_text())

    return data

def scrape():
    data = h1b_scraper()
    data = [ x for x in data if "\n" not in x ]
    df = pd.DataFrame(np.array(data).reshape(int(len(data)/6),6),
                      columns = ['company', 'role', 'salary',
                                 'city','submitdate', 'startdate'])

    df = df.loc[~(df['role'].str.contains('MANAGER'))]
    df['salary'] = [x.replace(',', '') for x in df.salary]
    df['salary'] = df['salary'].astype(int)
    df.submitdate = pd.to_datetime(df.submitdate)
    df.startdate = pd.to_datetime(df.startdate).dt.year

    df[['city', 'state']] = df['city'].str.split(',',1, expand = True)
    df = df.loc[~(df['city'].str.split().str.len()>=4)]
    df.loc[df['city'].str.contains('NEW YORK'), ['city']] = 'NEW YORK'
    df['state'] = [x.strip()[-2:] for x in df['state']]

    # print(df.head(10))

    state_mean = df[['state', 'salary']].groupby('state').mean().reset_index()
    state_mean = state_mean.sort_values('salary', ascending = False).reset_index(drop = True)

    fig = plt.figure(figsize = [12,6])
    plt.bar(state_mean['state'], state_mean['salary'])
    plt.xticks(rotation = 70)
    plt.show()
    # ----
    # ----
    year_mean = df[['startdate', 'salary']].groupby('startdate').mean().reset_index()
    year_mean = year_mean.sort_values('salary', ascending = False).reset_index(drop = True)

    fig = plt.figure(figsize = [12,6])
    plt.bar(year_mean['startdate'], year_mean['salary'])
    plt.xticks(rotation = 70)
    plt.show()

scrape()
