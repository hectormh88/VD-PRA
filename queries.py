import pandas as pd
import numpy as np

top1 = pd.read_csv('data/top1_monthly.csv', index_col=0).reset_index(drop=False)
top1_songs = pd.read_csv('data/top1_monthly_songs.csv', index_col=0).reset_index(drop=False)
top1_artists_images = pd.read_csv('data/top1_artists_images.csv', index_col=0).reset_index(drop=False)
monthly_streams = pd.read_csv('data/monthly_streams.csv', index_col=0).reset_index(drop=False)

top10 = pd.read_csv('data/top10_monthly.csv', index_col=0).reset_index(drop=False)
top10_songs = pd.read_csv('data/top10_monthly_songs.csv', index_col=0).reset_index(drop=False)
top10_artists_images = pd.read_csv('data/top10_artists_images.csv', index_col=0).reset_index(drop=False)


years = np.arange(2017, 2022)


def get_top10(date, region):
    filter = (top10['year_month'] == date) & (top10['region'] == region)
    top10_filtered = top10[filter].reset_index(drop=True).drop(columns=['year_month', 'region']).sort_values('streams', ascending=False)
    top10_filtered['image'] = top10_filtered['artist'].map(top10_artists_images.set_index('artist')['image'])
    top10_filtered['image'] = top10_filtered['image'].fillna('assets/no_image.png')
    return top10_filtered


def get_top10_songs(date, region, artist):
    filter = (top10_songs['year_month'] == date) & (top10_songs['region'] == region) & (top10_songs['artist'] == artist)
    top10_songs_filtered = top10_songs[filter].reset_index(drop=True).drop(columns=['year_month', 'region'])
    return top10_songs_filtered


def get_top1(date, region):
    filter = (top1['year_month'] == date) & (top1['region'] == region)
    top1_filtered = top1[filter].reset_index(drop=True).drop(columns=['year_month', 'region']).sort_values('streams', ascending=False)
    top1_filtered['image'] = top1_filtered['artist'].map(top1_artists_images.set_index('artist')['image'])
    top1_filtered['image'] = top1_filtered['image'].fillna('assets/no_image.png')
    return top1_filtered


def get_top1_songs(date, region):
    filter = (top1_songs['year_month'] == date) & (top1_songs['region'] == region)
    top1_songs_filtered = top1_songs[filter].reset_index(drop=True).drop(columns=['year_month', 'region'])
    return top1_songs_filtered


def get_regions():
    regions = sorted(list(top10['region'].unique()))
    return regions


def get_year_months():
    year_month = top1['year_month'].unique()
    return year_month


def get_monthly_streams(artist, region):
    index = monthly_streams[(monthly_streams['artist'] == artist) & (monthly_streams['region'] == region)].columns[2:]
    values = monthly_streams[(monthly_streams['artist'] == artist) & (monthly_streams['region'] == region)].values[0,2:]
    return index, values

def get_anual_streams(years, region):
    df = pd.DataFrame(columns=['year', 'streams'])
    for year in years:
        columns = [col for col in monthly_streams.columns if col.startswith(f"{year}-")]
        columns.insert(0, 'region')
        filter = (monthly_streams['region'] == region)
        df_anual_streams = monthly_streams[filter][columns].reset_index(drop=True)
        df_anual_streams = df_anual_streams.drop(columns='region')
        anual_streams = df_anual_streams.sum(axis=1)
        anual_streams = anual_streams.sum()
        df_year = pd.DataFrame({'year': [year], 'streams': anual_streams})
        df = pd.concat([df, df_year], ignore_index=True)
    return df

def get_anual_streams_regions(year):
    columns = [col for col in monthly_streams.columns if col.startswith(f"{year}-")]
    columns.insert(0, 'region')
    columns.insert(1, 'iso_alpha')
    columns.insert(2, 'artist')
    df_anual_streams = monthly_streams.loc[:, columns]
    df_anual_streams[f'{year}'] = df_anual_streams[columns[3:]].sum(axis=1)
    df_anual_streams = df_anual_streams.drop(columns=columns[3:])
    df_anual_streams = df_anual_streams.groupby(['region', 'iso_alpha']).sum().reset_index(drop=False)
    df_anual_streams.rename(columns={f'{year}': 'streams'}, inplace=True)
    df_anual_streams = df_anual_streams.drop(columns='artist')
    return df_anual_streams

def get_artists_streams(year_month, region):
    df = monthly_streams[(monthly_streams['region'] == region)][['artist', year_month]].sort_values(year_month, ascending=False).head(10)
    index = df['artist'].values
    values = df[year_month].values
    return index, values


def get_months():
    month_numbers = np.arange(1, 13)
    month_names = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']
    months = dict(zip(month_names, month_numbers))
    return months