from urllib.request import urlopen

from bs4 import BeautifulSoup
from pandas import DataFrame, merge

from config import type_info


def extract_table(url, table_class):
    html = urlopen(url).read()
    soup = BeautifulSoup(html, 'html.parser')
    table = soup.find('table', {'class': table_class})

    data = []
    for row in table.find_all('tr'):
        row_data = []
        for cell in row.find_all('td'):
            row_data.append(cell.text.strip())
        data.append(row_data)
    return DataFrame([row for row in data if row != []])


def data_merge():
    infinite_mons = extract_table("https://infinitefusion.fandom.com/wiki/Pok%C3%A9dex", 'article-table')
    infinite_mons = infinite_mons.iloc[:, :2]
    infinite_mons.columns = ['Index', 'Name']

    pokemon_set = extract_table("https://pokemon-index.com/base", 'move-lev by-base')
    pokemon_set = pokemon_set.drop(columns=[0])
    pokemon_set['Index'] = pokemon_set.index

    pokemon_set['Type 1'] = ''
    pokemon_set['Type 2'] = ''
    pokemon_set['Type 1'] = pokemon_set[2].str.split(' ').str[0].map(type_info["type_dict"])
    pokemon_set['Type 2'] = pokemon_set[2].str.split(' ').str[1].map(type_info["type_dict"])

    pokemon_set = pokemon_set.drop(columns=[2])
    pokemon_set.columns = [
        'Name', 'HP', 'Attack', 'Defense', 'Special Attack', 'Special Defense', 'Speed', 'Total', 'Index', 'Type 1',
        'Type 2'
    ]

    return merge(infinite_mons, pokemon_set, on='Name', how='right')


def prepare_df(pokemon_set):
    pokemon_set = pokemon_set.loc[((pokemon_set['Index_y'] < 252) & (pokemon_set['Index_y'].notnull())) |
                                  ((pokemon_set['Index_x'].notnull()) & (pokemon_set['Index_y'].notnull()))]

    pokemon_set.drop(columns=['Index_x'], inplace=True)
    pokemon_set.rename(columns={'Index_y': 'Index'}, inplace=True)
    for col in ['HP', 'Attack', 'Defense', 'Special Attack', 'Special Defense', 'Speed', 'Total']:
        pokemon_set[col] = pokemon_set[col].astype(int)

    return pokemon_set


def data_extraction():
    pokemon_set = data_merge()
    pokemon_set = prepare_df(pokemon_set)
    return pokemon_set