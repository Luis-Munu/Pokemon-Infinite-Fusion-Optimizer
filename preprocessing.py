from warnings import filterwarnings
from json import load, loads

from numpy import nan
from pandas import DataFrame, merge, read_json

from config import settings

filterwarnings("ignore")


def read_routes():
    with open('data/routes.csv', 'r') as f:
        routext = f.read().split('\n')
    routes = DataFrame(columns=['Medals', 'Locations'])
    for r in routext:
        if r != '':
            routes.loc[len(routes)] = [len(routes), [i.title() for i in r.split(',')]]
    return routes


def filter_encounters_by_medals(encounters):
    if settings["Medals owned"] < 2:
        encounters = encounters.loc[~encounters['Location'].str.contains('OldRod')]
    if settings["Medals owned"] < 4:
        encounters = encounters.loc[~encounters['Location'].str.contains('GoodRod')]
    if settings["Medals owned"] < 6:
        encounters = encounters.loc[~encounters['Location'].str.contains('SuperRod')]
        encounters = encounters.loc[~encounters['Location'].str.contains('Water')]
    if settings["Medals owned"] < 10:
        encounters = encounters.loc[~encounters['Location'].str.contains('Underwater')]
    return encounters


def assign_medals_to_pokemon(df, routes, encounters):
    df['Route'] = nan
    for i in range(len(routes)):
        route_pokemon = routes['Locations'][i]
        pokes = encounters.loc[encounters['Name'].isin(route_pokemon)]['Pokemon'].values
        pokes = [item for sublist in pokes for item in sublist]
        df.loc[(df['Name'].isin(pokes)) & (df['Route'].isnull()), 'Route'] = i
    return df


def add_traded_pokemon(df):
    traded_pokemon = load(open('data/traded_pokemon.json'))
    df2 = df.loc[(df['Route'].notnull()) & (df['Route'] <= settings["Medals owned"])]
    for i, m in traded_pokemon.items():
        if settings["Medals owned"] >= int(i):
            for p in m:
                if p in df['Name'].values:
                    df2 = df2.append(df.loc[df['Name'] == p])

    return df2


def read_evo_items():
    with open('data/evolution_items.csv', 'r') as f:
        evo_items = f.read().split('\n')
    evo_items = {k: v for k, v in enumerate(evo_items)}
    evo_items = [v for k, v in evo_items.items() if settings["Medals owned"] >= int(k)]
    evo_items = [i for i in evo_items if 'nothing' not in i]
    evo_items = [item for sublist in evo_items for item in sublist.split(',')]
    return [i.strip() for i in evo_items]


def add_evolutions(df, dfcp):
    evo_items = read_evo_items()
    obedience_level = min(100, 10 + settings["Medals owned"] * 10)
    for j in range(2):
        for i in range(len(df)):
            if df.iloc[i]['Evolution'] not in df['Name'].values:
                if df.iloc[i]['Min Level'] and type(
                        df.iloc[i]['Min Level']) == int and df.iloc[i]['Min Level'] < obedience_level:
                    df = df.append(dfcp.loc[dfcp['Name'] == df.iloc[i]['Evolution']])
                elif df.iloc[i]['Item'] and df.iloc[i]['Item'] in evo_items:
                    df = df.append(dfcp.loc[dfcp['Name'] == df.iloc[i]['Evolution']])
    return df


def filter_by_progress(df):
    encounters = read_json('data/encounters.json')
    evos = read_json('data/pokemon_evolutions.json')
    routes = read_routes()

    df = merge(df, evos, left_on='Name', right_on='Name', how='left')
    dfcp = df.copy()

    encounters = filter_encounters_by_medals(encounters)

    df = assign_medals_to_pokemon(df, routes, encounters)
    df = add_traded_pokemon(df)
    df = add_evolutions(df, dfcp)
    df.drop(columns=['Route'], inplace=True)

    return df


def handle_exceptions(pokemon_set):
    exception_set = loads(open('data/exceptions.json').read())

    pokemon_set.loc[pokemon_set['Name'].isin(exception_set["exceptions"]), 'Type 2'] = nan

    pokemon_set.loc[(pokemon_set['Type 1'] == 'normal') & (pokemon_set['Type 2'] == 'flying'), 'Type 1'] = 'flying'
    pokemon_set.loc[(pokemon_set['Type 1'] == 'normal') & (pokemon_set['Type 2'] == 'flying'), 'Type 2'] = nan
    pokemon_set.loc[pokemon_set['Name'] == 'Fletchling', 'Type 1'] = 'normal'
    pokemon_set.loc[pokemon_set['Name'] == 'Fletchling', 'Type 2'] = 'flying'

    pokemon_set.loc[pokemon_set['Name'].isin(exception_set["swapped"]), 'Type 1'], pokemon_set.loc[
        pokemon_set['Name'].isin(exception_set['swapped']),
        'Type 2'] = pokemon_set.loc[pokemon_set['Name'].isin(exception_set['swapped']),
                                    'Type 2'], pokemon_set.loc[pokemon_set['Name'].isin(exception_set['swapped']),
                                                               'Type 1']

    return pokemon_set


def preprocessing(pokemon_set):
    pokemon_set = handle_exceptions(pokemon_set)
    if settings["Filter Pokemon by medals"]:
        pokemon_set = filter_by_progress(pokemon_set)
    if settings["Filter Pokemon by name"]:
        pokemon_set = pokemon_set.loc[~pokemon_set['Name'].isin(settings["Filtered names"])]
    pokemon_set.sort_index(inplace=True)
    return pokemon_set