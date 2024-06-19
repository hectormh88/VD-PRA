import pandas as pd


countries_in_conflict = pd.read_csv('data/countries_in_conflict.csv')
crime_2021 = pd.read_csv('data/crime_2021.csv')
GDP_pc = pd.read_csv('data/GDP_pc.csv')
migrants = pd.read_csv('data/migrants.csv')
country_codes = pd.read_csv('data/country_codes.csv')
population = pd.read_excel('data/population.xlsx')

countries_in_conflict.drop(columns=['country_iso_alpha3'], inplace=True)
countries_in_conflict = countries_in_conflict[~(countries_in_conflict['Country'] == "Yemen People's Republic")]

continent_translation = {
    'Africa': 'África',
    'Asia': 'Asia',
    'Europe': 'Europa',
    'Northern America': 'Norteamérica',
    'Oceania': 'Oceanía',
    'Latin America and the Caribbean': 'Latinoamérica y el Caribe',
}

gender_translation = {
    'Both': 'Ambos',
    'Males': 'Hombres',
    'Females': 'Mujeres',
}

def get_df1():
    countries_in_conflict_grouped = countries_in_conflict.groupby(['Continent', 'Year'])['Deaths in ongoing conflicts'].sum()
    countries_in_conflict_grouped = countries_in_conflict_grouped.reset_index()
    return countries_in_conflict_grouped


def get_df2(year=2020):
    gender = 'Both'
    migrants_filtered = migrants
    migrants_filtered = migrants_filtered[migrants_filtered['Gender'] == gender][['Origin ISO', f'{year}']]
    migrants_filtered = migrants_filtered[migrants_filtered['Origin ISO'] != 'WLD']
    migrants_grouped = migrants_filtered.groupby('Origin ISO')[f'{year}'].sum().reset_index()
    crime_2021_filtered = crime_2021[['Code Value', 'Criminality']]
    GDP_pc_filtered = GDP_pc[~(GDP_pc['Country ISO'].isin(['WLD', 'XKX']))]
    GDP_pc_filtered = GDP_pc_filtered[GDP_pc_filtered['Year'] == year][['Country ISO', 'GDP per capita']]
    years = list(range(year-4, year+1))
    countries_in_conflict_filtered = countries_in_conflict[~(countries_in_conflict['Country ISO'].isin(['XKX', 'YUG']))]
    countries_in_conflict_filtered = countries_in_conflict_filtered[countries_in_conflict_filtered['Year'].isin(years)][['Country ISO', 'Deaths in ongoing conflicts']]
    population_filtered = population[['Country', 'Country ISO', year]]
    population_filtered = population_filtered.rename(columns={year: 'Population'})
    df_corr = migrants_grouped.merge(crime_2021_filtered, left_on='Origin ISO', right_on='Code Value')
    df_corr = df_corr.merge(GDP_pc_filtered, left_on='Origin ISO', right_on='Country ISO')
    df_corr = df_corr.merge(countries_in_conflict_filtered, left_on='Origin ISO', right_on='Country ISO')
    df_corr = df_corr.merge(population_filtered, left_on='Origin ISO', right_on='Country ISO')
    df_corr.drop(columns=['Code Value', 'Country ISO_x', 'Country ISO_y', 'Country ISO'], inplace=True)
    df_corr.rename(columns={'Origin ISO': 'Country ISO', f'{year}': 'Migrants', 'Deaths in ongoing conflicts': 'Deaths in conflicts'}, inplace=True)
    df_corr['Migrants rate'] = df_corr['Migrants'] / df_corr['Population'] * 100
    df_corr['Migrants rate'] = df_corr['Migrants rate'].apply(pd.to_numeric)
    df_corr = df_corr[(df_corr['Population'] > 1000000) & (df_corr['Migrants'] > 100000)]
    return df_corr


def get_df3(year=2020, migrants_from=100000):
    GDP_pc_filtered = GDP_pc[~(GDP_pc['Country ISO'].isin(['WLD', 'XKX']))]
    GDP_pc_filtered = GDP_pc_filtered[GDP_pc_filtered['Year'] == year]
    gender = 'Both'
    migrants_filtered = migrants[migrants['Gender'] == gender][['Destination ISO', f'{year}']]
    migrants_filtered = migrants_filtered[migrants_filtered['Destination ISO'] != 'WLD']
    migrants_grouped = migrants_filtered.groupby('Destination ISO')[f'{year}'].sum().reset_index()
    migrants_grouped.rename(columns={f'{year}': 'Immigrants', 'Destination ISO': 'Country ISO'}, inplace=True)
    df_corr = migrants_grouped.merge(GDP_pc_filtered, left_on='Country ISO', right_on='Country ISO')
    df_corr = df_corr[df_corr['Immigrants'] > migrants_from]
    return df_corr


def get_df4(continent):
    migrants_filtered = migrants[(migrants['Origin ISO'] != 'WLD')]
    migrants_filtered = migrants_filtered[(migrants_filtered['Destination ISO'] != 'WLD')]
    migrants_filtered = migrants_filtered[['1990', '1995', '2000', '2005', '2010', '2015', '2020', 'Gender', 'Origin Continent', 'Destination Continent']]
    migrants_filtered = migrants_filtered.groupby(['Gender', 'Origin Continent', 'Destination Continent']).sum().reset_index()
    migrants_filtered_origin = migrants_filtered[migrants_filtered['Gender'] != 'Both']
    migrants_filtered_origin = migrants_filtered_origin.drop(columns=['Destination Continent'])
    migrants_filtered_origin = migrants_filtered_origin.groupby(['Gender', 'Origin Continent']).sum().reset_index()
    migrants_filtered_origin = pd.melt(
        migrants_filtered_origin, id_vars=['Gender', 'Origin Continent'], 
        var_name='Year', value_name='Migrants')
    migrants_filtered_origin_temp = migrants_filtered_origin[migrants_filtered_origin['Origin Continent'] == continent]
    return migrants_filtered_origin_temp


def get_df5():
    migrants_filtered = migrants[(migrants['Origin ISO'] != 'WLD')]
    migrants_filtered = migrants_filtered[(migrants_filtered['Destination ISO'] != 'WLD')]
    migrants_filtered = migrants_filtered[['1990', '1995', '2000', '2005', '2010', '2015', '2020', 'Gender', 'Origin Continent', 'Destination Continent']]
    migrants_filtered = migrants_filtered.groupby(['Gender', 'Origin Continent', 'Destination Continent']).sum().reset_index()
    migrants_filtered_both = migrants_filtered[migrants_filtered['Gender'] == 'Both']
    migrants_filtered_both = migrants_filtered_both.drop(columns=['Gender'])
    migrants_filtered_both = pd.melt(
        migrants_filtered_both, id_vars=['Origin Continent', 'Destination Continent'], 
        var_name='Year', value_name='Migrants')
    return migrants_filtered_both


def get_df6(year=2020):
    gender = 'Both'
    migrants_filtered = migrants[migrants['Gender'] == gender][['Origin ISO', 'Region of origin', f'{year}']]
    migrants_filtered = migrants_filtered[migrants_filtered['Origin ISO'] != 'WLD']
    migrants_grouped = migrants_filtered.groupby(['Origin ISO', 'Region of origin'])[f'{year}'].sum().reset_index()
    migrants_grouped.rename(columns={f'{year}': 'Emigrants', 'Origin ISO': 'Country ISO', 'Region of origin': 'Country'}, inplace=True)
    years = list(range(year-4, year+1))
    countries_in_conflict_filtered = countries_in_conflict[~(countries_in_conflict['Country ISO'].isin(['XKX', 'YUG']))]
    countries_in_conflict_filtered = countries_in_conflict_filtered[countries_in_conflict_filtered['Year'].isin(years)][['Country ISO', 'Deaths in ongoing conflicts']]
    countries_in_conflict_filtered = countries_in_conflict_filtered.groupby('Country ISO')['Deaths in ongoing conflicts'].sum().reset_index()
    population_filtered = population[['Country ISO', year]]
    population_filtered = population_filtered.rename(columns={year: 'Population'})
    df_corr = migrants_grouped.merge(countries_in_conflict_filtered, on='Country ISO')
    df_corr = df_corr.merge(population_filtered, on='Country ISO')
    df_corr['Emigrants rate'] = df_corr['Emigrants'] / df_corr['Population'] * 100
    df_corr['Emigrants rate'] = df_corr['Emigrants rate'].apply(pd.to_numeric)
    return df_corr


def get_df7(year=2020, head=20):
    flows = migrants[(migrants['Origin ISO'] != 'WLD')]
    flows = flows[(flows['Destination ISO'] != 'WLD')]
    flows = flows[flows['Gender'] == 'Both']
    flows = flows[['Region of destination', 'Destination ISO', 'Region of origin', 'Origin ISO', f'{year}']]
    flows = flows.rename(columns={f'{year}': 'Migrants'})
    flows = flows.sort_values(by='Migrants', ascending=False).reset_index(drop=True).head(head)
    return flows