import dash
from dash import html, dcc, dash_table
from dash.dependencies import Input, Output, State
import dash_bootstrap_components as dbc
import plotly.graph_objs as go
import pandas as pd
import numpy as np
from dash import no_update
import plotly.express as px

from queries import get_top1, get_top1_songs, get_top10, get_top10_songs, get_regions, get_year_months, years
from queries import get_months, get_monthly_streams, get_artists_streams, get_anual_streams, get_anual_streams_regions


STYLESHEET = dbc.themes.COSMO




# Crear la aplicación Dash
app = dash.Dash(__name__,
                external_stylesheets=[STYLESHEET],
                prevent_initial_callbacks='initial_duplicate'
                )
server = app.server
app.title = 'Spotify Trends Explorer'


def get_figure_map(year):
    df = get_anual_streams_regions(year)
    df = df[~(df['region'] == 'Global')]

    # Crear un mapa coropleta con una escala de colores personalizada
    fig = px.choropleth(df, locations="iso_alpha",
                        color="streams",  # Variable que se va a mapear con el color
                        hover_name="region",  # Columna que aparecerá al pasar el mouse
                        color_continuous_scale=[(0, "white"), (1, "rgba(33,97,140,1)")],  # Escala del blanco al azul oscuro
                        hover_data={f"streams": ":,.0f"},  # Formato de los datos al pasar el mouse
    )
    
    fig.update_traces(
        hovertemplate="<b>%{hovertext}</b><br>Streams: %{customdata[0]:,.0f}"
    )
    
    # Configuración para hacer transparente el fondo del mapa y ajustar la visualización
    fig.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',  # Fondo del gráfico transparente
        paper_bgcolor='rgba(0,0,0,0)',  # Fondo exterior del gráfico transparente
        geo=dict(
            bgcolor='rgba(0,0,0,0)',  # Hacer el fondo del mapa (incluido el mar) transparente
            lakecolor='rgba(0,0,0,0)',  # Hacer el color de los lagos transparente
            showframe=False,  # Eliminar el borde del mapa
            showcoastlines=False,  # Eliminar las líneas de costa
            projection_type='natural earth',  # Tipo de proyección del mapa
        ),
        margin=dict(l=10, r=0, t=0, b=10), # Reducir el espacio en blanco en todos los lados del gráfico
        width=800,
        coloraxis_showscale=False,  # Eliminar el colorbar
    )

    # Ajustar los límites del mapa para excluir la Antártida
    fig.update_geos(
        showcountries=True, countrycolor="grey",
        landcolor='rgba(0,0,0,0.1)', subunitcolor="black",
        lonaxis_range=[-180, 180],
        lataxis_range=[-60, 90]  # Limitar la latitud para no mostrar la Antártida
    )

    return fig



def get_figure_anual_streams(years, region='Global'):
    df = get_anual_streams(years, region)
    
    fig = go.Figure()
    
    # Agregar la línea con datos de streams
    fig.add_trace(go.Scatter(
        x=df['year'], y=df['streams'], mode='lines+markers', name='Streams', line=dict(color='#21618C'),
        hovertemplate='%{y} streams<br>%{x}'
    ))
    
    fig.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',  # Fondo del gráfico transparente
        paper_bgcolor='rgba(0,0,0,0)',  # Fondo exterior del gráfico transparente
        yaxis=dict(title="Annual streams", zeroline=True, zerolinewidth=1.2, zerolinecolor='rgb(33,97,140,0.3)'),
        autosize=True,
        yaxis_range=[0, df['streams'].max() * 1.1],
    )
    
    return fig



# Definir el layout de la aplicación
app.layout = html.Div([
    html.Div([
        html.H1('Trends: Unveiling the Global Music Landscape on Spotify', style={'text-align': 'center', 'font-size': '50px', 'width': '80%', 'margin': '0 auto'}),
        html.P(f'Explore how the world listens from {np.min(years)} to {np.max(years)}, and discover the local and global tastes that shape our musical universe.', className='lead', style={'text-align': 'center'}),
    ]),
    html.Hr(style={'margin-top': '20px', 'margin-bottom': '20px'}),
    html.Div([
        html.Div([
            html.P("Is the Spotify Top 200 a true reflection of global music trends, or does it show a concentration of preferences in certain areas?",
                   style={'text-align': 'center', 'font-size': '35px', 'margin-bottom': '20px'}),
        ]),
    ], style={'display': 'flex', 'justify-content': 'space-around', 'width': '70%', 'margin': '0 auto'}),
    html.Div([
        html.Div([
            html.Div([
                html.Div([
                    html.Label("Select a year:"),
                    dcc.Dropdown(
                        id='year-anual',
                        options=[{'label': value, 'value': value} for value in years],
                        value=np.max(years),
                        clearable=False,
                        searchable=True,
                        placeholder="Selecciona una opción",
                        style={'width': '100%', 'background-color': 'rgba(33,97,140,0.1)', 'border-radius': '11px'},
                    ),
                ], style={'margin': '0 auto'}, className='d-grid gap-2'),
            ], style={'display': 'flex', 'justify-content': 'space-around', 'width': '80%', 'margin-bottom': '30px'}),
            html.P(id='title-choropleth-map', style={'text-align': 'center', 'font-size': '28px'}, className='lead'),
            dcc.Graph(id='choropleth-map', config={'displayModeBar': False}),
        ], style={'width': '65%'}),
        html.Div([
            html.Div([
                html.Label("Look again at global data!", style={'text-align': 'center'}),
                html.Button("GLOBAL", id="global", n_clicks=0, className="transparent-button"),
            ], style={'margin': '0 auto', 'margin-bottom': '30px', 'width': '60%'}, className='d-grid gap-2'),
            html.P("Annual streams Global", id='title-evolution-graph', style={'text-align': 'center', 'font-size': '28px'}, className='lead'),
            dcc.Graph(id='evolution-graph', figure=get_figure_anual_streams(years), config={'displayModeBar': False}),
        ], style={'width': '35%'}),
    ], style={'display': 'flex', 'justify-content': 'space-around', 'width': '100%', 'margin-top': '30px'}),
    
    html.Hr(style={'margin-top': '20px', 'margin-bottom': '20px'}),
    html.Div([
        html.Div([
            html.P("How do popular music artists and trends vary across different times and regions?",
                   style={'text-align': 'center', 'font-size': '35px', 'margin-bottom': '20px'}),
        ]),
    ], style={'display': 'flex', 'justify-content': 'space-around', 'width': '70%', 'margin': '0 auto'}),
    html.Div([
        html.Div([
            html.Label("Feeling adventurous? Hit the...", style={'fontSize': 'bold'}),
            html.Button("RANDOM", id="random-button-monthly", n_clicks=0, className="transparent-button"),
        ], style={'margin': '0 auto'}, className='d-grid gap-2'),
        html.Div([
            html.Label("What country or region do you want to explore?"),
            dcc.Dropdown(
                id='region-monthly',
                options=[{'label': region, 'value': region} for region in get_regions()],
                value='Global',
                clearable=False,
                searchable=True,
                placeholder="Selecciona una opción",
                style={'width': '100%', 'background-color': 'rgba(33,97,140,0.1)', 'border-radius': '11px'},
            ),
        ], style={'margin': '0 auto'}, className='d-grid gap-2'),
        html.Div([
            html.Label("Select a year:"),
            dcc.Dropdown(
                id='year-monthly',
                options=[{'label': value, 'value': value} for value in years],
                value=np.max(years),
                clearable=False,
                searchable=True,
                placeholder="Selecciona una opción",
                style={'width': '100%', 'background-color': 'rgba(33,97,140,0.1)', 'border-radius': '11px'},
            ),
        ], style={'margin': '0 auto'}, className='d-grid gap-2'),
    ], style={'display': 'flex', 'justify-content': 'space-around', 'width': '80%'}),
    html.Div(id='no-data', style={'text-align': 'center', 'margin-top': '20px', 'font-size': '20px'}),
    html.Div([
        html.Div([
            html.Label("Select a month:"),
            dcc.Slider(
                id='month',
                min=1,
                max=12,
                value=1,
                marks={i: f'{month}' for i, month in enumerate(get_months(), start=1)},
                step=1,
                vertical=True,
                verticalHeight=300,
            ),
        ], style={'display': 'flex', 'flex-direction': 'column', 'padding': '20px', 'width': '20%', 'align-items': 'center', 'justify-content': 'center'}),
        html.Div([
            dcc.Graph(id='top10-graph', style={'width': '100%', 'height': '100%'}, config={'displayModeBar': False}),
            html.P("Select an artist", style={'text-align': 'center', 'font-size': '20px', 'font-style': 'italic'}),
        ], style={'display': 'flex', 'flex-direction': 'column', 'justify-content': 'center', 'padding': '20px', 'width': '80%'}),
    ], style={'display': 'flex', 'flex-direction': 'row', 'width': '100%', 'margin': '0 auto'}),
    html.Hr(style={'margin-top': '10px'}),
    html.Div([
        html.Div([
            html.Div([
                html.H2(id='top1-artist', style={'text-align': 'right'}),
                html.P(id='top1-streams', className='lead', style={'font-size': '20px', 'text-align': 'right'}),
            ], style={'display': 'flex', 'flex-direction': 'column', 'justify-content': 'center', 'padding': '20px', 'width': '50%'}),
            html.Div([
                html.Img(id='top1-image', src='', width='200', height='200', style={'border-radius': '12px', 'padding': '20px'}),
            ], style={'display': 'flex', 'flex-direction': 'column', 'justify-content': 'center', 'padding': '20px', 'width': '50%'}),
        ], style={'display': 'flex', 'justify-content': 'center', 'width': '40%', 'margin': '0 auto', 'align-items': 'center'}),
        html.Div([
            dcc.Graph(id='top1-graph', style={'width': '100%'}, config={'displayModeBar': False}),
        ], style={'display': 'flex', 'flex-direction': 'column', 'justify-content': 'center', 'padding': '20px', 'width': '60%', 'margin': '0 auto', 'align-items': 'center'}),
    ], style={'display': 'flex', 'justify-content': 'space-between', 'margin': '0 auto'}),
    html.Div([
        html.Div([
            html.P(id='top1-song1-streams', className='lead', style={'font-size': '20px', 'text-align': 'center'}),
            html.Iframe(id='spotify-player-1', src="", width='90%', height='200', style={'border-radius': '12px', 'margin': '0 auto'},
                allow='autoplay; clipboard-write; encrypted-media; fullscreen; picture-in-picture'),
        ], className='responsive-div', style={'margin': '0 auto'}),
        html.Div([
            html.P(id='top1-song2-streams', className='lead', style={'font-size': '20px', 'text-align': 'center'}),
            html.Iframe(id='spotify-player-2', src="", width='90%', height='200', style={'border-radius': '12px', 'margin': '0 auto'},
                allow='autoplay; clipboard-write; encrypted-media; fullscreen; picture-in-picture'),
        ], className='responsive-div', style={'margin': '0 auto'}),
        html.Div([
            html.P(id='top1-song3-streams', className='lead', style={'font-size': '20px', 'text-align': 'center'}),
            html.Iframe(id='spotify-player-3', src="", width='90%', height='200', style={'border-radius': '12px', 'margin': '0 auto'},
                allow='autoplay; clipboard-write; encrypted-media; fullscreen; picture-in-picture'),
        ], className='responsive-div', style={'margin': '0 auto'}),
    ], style={'display': 'flex', 'flex-direction': 'row', 'justify-content': 'space-around', 'width': '80%', 'align-items': 'center', 'margin': '0 auto'}),
    html.Div([
        html.Div([
            html.P("These trends highlight music's global reach and local flavor.",
                   style={'text-align': 'center', 'font-size': '35px', 'margin-top': '20px', 'margin-bottom': '0'}),
            html.P("What do they reveal about how worldwide audiences are shaping their musical tastes?",
                   style={'text-align': 'center', 'font-size': '35px', 'margin-bottom': '20px'}),
        ]),
    ], style={'display': 'flex', 'justify-content': 'space-around', 'width': '70%', 'margin': '0 auto'}),
    
    html.Hr(),
    html.Div([
        html.H1("About", style={'text-align': 'left', 'margin-top': '40px'}),
        html.Div([
            html.H2("Data Source", style={'text-align': 'left', 'margin-top': '20px'}),
            html.P([
                "The data used in this analysis of the Top 200 charts is sourced from the ",
                html.A("Spotify Charts", href="https://www.kaggle.com/datasets/dhruvildave/spotify-charts", target="_blank"),
                " dataset, which is a comprehensive collection of all the 'Top 200' and 'Viral 50' charts published globally by Spotify since January 1, 2017. ",
                "The dataset was compiled by Dhruvil Dave and is available on Kaggle under an ",
                html.A("Open Data Commons Open Database License (ODbL)", href="https://opendatacommons.org/licenses/odbl/1-0/", target="_blank"),
                ". The specific subset used here includes only the 'Top 200' charts. For further details, please refer to the original dataset on Kaggle. ",
            ]),
            html.P("The dataset is cited as follows:", style={'text-align': 'left', 'margin-bottom': '5px'}),
            html.P([
                "Dhruvil Dave. (2021). Spotify Charts [Data set]. Kaggle. ",
                html.A("https://doi.org/10.34740/KAGGLE/DS/1265407", href="https://doi.org/10.34740/KAGGLE/DS/1265407", target="_blank"),
            ]),
            html.P([
                "Additionally, images of each artist were obtained via the Spotify API. These images are used under the terms of Spotify's API, which permits non-commercial use for public displays and analyses. ",
                "For further information regarding Spotify's API usage terms, please refer to ",
                html.A("Spotify's Developer Terms of Service", href="https://developer.spotify.com/terms", target="_blank"),
                "."
            ])
        ]),
        html.Div([
            html.H2("Proccess", style={'text-align': 'left', 'margin-top': '20px'}),
            html.P([
                "The original dataset consisted of daily streaming numbers for each song, detailed globally and by region. ",
                "For the purpose of this analysis, the data were aggregated to provide annual and monthly summaries of streaming activity. ",
                "This transformation not only tailored the dataset to better suit our analytical goals by focusing on larger trends rather than daily fluctuations but also significantly reduced the dataset size. ",
                "This reduction in size helped streamline our analysis process, making data handling and processing more efficient without compromising the depth and quality of insights gained."
            ]),
        ]),
        html.Div([
            html.H2("Contact", style={'text-align': 'left', 'margin-top': '20px'}),
            html.P([
                "For any questions or feedback, please feel free to reach out to the author of this analysis, Héctor Martínez, via ",
                html.A("LinkedIn", href="https://www.linkedin.com/in/hectormartinezhidalgo/", target="_blank"),
                " or email at ",
                html.A("hectormh@uoc.edu", href="mailto:hectormh@uoc.edu", target="_blank"),
            ]),
        ]),
    ], style={'width': '80%', 'margin': '0 auto'}),
    html.Footer([
        html.P("", style={'text-align': 'center'}),
    ], style={'margin-top': '20px', 'margin-bottom': '20px'}),
])


def create_spotify_embed_url(track_url):
    if track_url:
        track_id = track_url.split('/')[-1]
        return f"https://open.spotify.com/embed/track/{track_id}?utm_source=generator"
    else:
        return ""



def get_figure_graph_top1(artist, region, year_month):
    fig_data = get_monthly_streams(artist, region)
    fig = go.Figure()

    # Agregar la línea con datos de streams
    fig.add_trace(go.Scatter(
        x=fig_data[0], y=fig_data[1], mode='lines', name='Streams', fill='tozeroy', fillcolor='rgba(33,97,140,0.2)',
        line=dict(shape='spline', width=1, color='#21618C', smoothing=0.5),
        hovertemplate='%{y} streams<br>%{x}'
    ))

    # Encontrar el índice del year_month especificado
    if year_month in fig_data[0]:
        index = fig_data[0].get_loc(year_month)
        # Agregar un punto rojo en la línea a la altura del year_month indicado
        fig.add_trace(go.Scatter(
            x=[fig_data[0][index]], y=[fig_data[1][index]], mode='markers', name='Selected month',
            marker=dict(color='#21618C', size=7), hovertemplate='%{y} streams<br>%{x}'
        ))
    
    # Configurar el diseño del gráfico
    fig.update_layout(
        yaxis=dict(title="Monthly streams", zeroline=True, zerolinewidth=1.2, zerolinecolor='rgb(33,97,140,0.3)'),
        autosize=True,
        plot_bgcolor='rgba(0,0,0,0.009)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(
            family="Arial, sans-serif",
            size=12,
            color="black"
        )
    )

    # Mejorar la presentación en dispositivos móviles
    fig.update_layout(
        autosize=True,
        margin=dict(l=50, r=50, t=50, b=50),
        showlegend=False
    )

    # Remover las líneas guías verticales y horizontales
    fig.update_xaxes(showgrid=False)
    fig.update_yaxes(showgrid=False, linecolor='rgb(33,97,140,0.3)', linewidth=1.2)

    return fig



def get_figure_graph_top10(artist, region, year_month):
    fig_data = get_artists_streams(year_month, region)

    # Convertir los datos en un DataFrame para facilitar la ordenación
    df = pd.DataFrame({'Artist': fig_data[0], 'Streams': fig_data[1]})

    # Ordenar el DataFrame por Streams en orden descendente
    df = df.sort_values(by='Streams', ascending=False)

    # Crear una lista de colores para las barras, todas azules
    colors = ['rgba(33,97,140,0.4)' for _ in range(len(df))]

    # Resaltar la barra del artista seleccionado
    if artist in df['Artist'].values:
        index = df.index[df['Artist'] == artist].tolist()[0]
        colors[index] = 'rgba(33,97,140,0.8)'

    # Crear el gráfico de barras horizontales
    fig = go.Figure()

    fig.add_trace(go.Bar(
        x=df['Streams'],
        y=df['Artist'],
        orientation='h',
        marker=dict(color=colors),
        hovertemplate='%{x} streams<br>%{y}',
        name='Streams'
    ))

    # Configurar el diseño del gráfico
    fig.update_layout(
        xaxis=dict(title="Monthly streams"),
        yaxis=dict(title="Top 10 artists", autorange="reversed"),  # Para mostrar de mayor a menor
        autosize=True,
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(
            family="Arial, sans-serif",
            size=12,
            color="black"
        ),
        margin=dict(l=50, r=50, t=50, b=50),
        showlegend=False,
        height=400,
    )
    
    # Remover las líneas guías verticales y horizontales
    fig.update_xaxes(showgrid=False)
    fig.update_yaxes(showgrid=False)

    return fig


@app.callback(
    [Output('choropleth-map', 'figure'),
     Output('title-choropleth-map', 'children')],
    [Input('year-anual', 'value')],
)

def update_year_map(year):
    if year is not None:
        figure_choropleth_map = get_figure_map(year)
        title_map = f"Annual streams {year}"
        return figure_choropleth_map, title_map


@app.callback(
    [Output('title-evolution-graph', 'children', allow_duplicate=True),
     Output('evolution-graph', 'figure', allow_duplicate=True)],
    [Input('choropleth-map', 'clickData')]
)
def update_output_evolution_graph(clickData):
    if clickData is not None:
        country_code = clickData['points'][0]['location']
        country_name = clickData['points'][0]['hovertext']
        figure_annual_streams = get_figure_anual_streams(years, country_name)
        
        return f"Annual streams {country_name}", figure_annual_streams
    
    #figure_annual_streams = get_figure_anual_streams(years)

    return no_update, no_update


@app.callback(
    [Output('title-evolution-graph', 'children', allow_duplicate=True),
     Output('evolution-graph', 'figure', allow_duplicate=True)],
    [Input('global', 'n_clicks')]
)
def update_evolution_graph_global(n_clicks):
    if n_clicks > 0:
        figure_annual_streams = get_figure_anual_streams(years)
        return f"Annual streams Global", figure_annual_streams
    else:
        return no_update, no_update


@app.callback(
    [Output('top1-artist', 'children'),
     Output('top1-streams', 'children'),
     Output('top1-image', 'src'),
     Output('top1-song1-streams', 'children'),
     Output('top1-song2-streams', 'children'),
     Output('top1-song3-streams', 'children'),
     Output('spotify-player-1', 'src'),
     Output('spotify-player-2', 'src'),
     Output('spotify-player-3', 'src'),
     Output('top1-graph', 'figure'),
     Output('top10-graph', 'figure'),
     Output('no-data', 'children'),
     Output('region-monthly', 'value'),
     Output('year-monthly', 'value'),
     Output('month', 'value'),],
    [Input('region-monthly', 'value'),
     Input('year-monthly', 'value'),
     Input('month', 'value'),
     Input('top10-graph', 'clickData'),
     Input('random-button-monthly', 'n_clicks')]
)
def update_output(region, year, month, clickData, n_clicks):
    ctx = dash.callback_context

    #if n_clicks > 0:
    if n_clicks > 0 and not ctx.triggered or ctx.triggered[0]['prop_id'].split('.')[0] == 'random-button-monthly':

        region = np.random.choice(get_regions())
        year = np.random.choice(['2017', '2018', '2019', '2020', '2021'])
        month = np.random.choice(np.arange(1, 13))
        year_month = f"{year}-{month:02}"
        top1 = get_top1(year_month, region).to_dict('records')
        top10 = get_top10(year_month, region).to_dict('records')
        if len(top1) > 0:
            if clickData is not None:
                pointIndex = clickData['points'][0]['pointIndex']
                top1_artist = top10[pointIndex]['artist']
                top1_streams = f"{int(top10[pointIndex]['streams']):,} monthly streams"
                top1_image = top10[pointIndex]['image']
                top1_songs = get_top10_songs(year_month, region, top1_artist).to_dict('records')
            else:
                top1_artist = top10[0]['artist']
                top1_streams = f"{int(top10[0]['streams']):,} monthly streams"
                top1_image = top10[0]['image']
                top1_songs = get_top10_songs(year_month, region, top10[0]['artist']).to_dict('records')            
            
            top1_song1_streams = f"{int(top1_songs[0]['streams']):,} monthly streams" if len(top1_songs) > 0 else None
            top1_song2_streams = f"{int(top1_songs[1]['streams']):,} monthly streams" if len(top1_songs) > 1 else None
            top1_song3_streams = f"{int(top1_songs[2]['streams']):,} monthly streams" if len(top1_songs) > 2 else None
            track_url_1 = top1_songs[0]['id_song']
            track_url_2 = top1_songs[1]['id_song'] if len(top1_songs) > 1 else None
            track_url_3 = top1_songs[2]['id_song'] if len(top1_songs) > 2 else None
            embed_url_1 = create_spotify_embed_url(track_url_1)
            embed_url_2 = create_spotify_embed_url(track_url_2) if len(top1_songs) > 1 else None
            embed_url_3 = create_spotify_embed_url(track_url_3) if len(top1_songs) > 2 else None
            fig_top1 = get_figure_graph_top1(top1_artist, region, year_month)
            fig_top10 = get_figure_graph_top10(top1_artist, region, year_month)
            return top1_artist, top1_streams, top1_image, top1_song1_streams, top1_song2_streams, top1_song3_streams, embed_url_1, embed_url_2, embed_url_3, fig_top1, fig_top10, "", region, year, month
        else:
            fig_top1 = go.Figure()
            fig_top1.update_layout(
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                xaxis=dict(showgrid=False, zeroline=False, visible=False),
                yaxis=dict(showgrid=False, zeroline=False, visible=False)
            )
            fig_top10 = go.Figure()
            fig_top10.update_layout(
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                xaxis=dict(showgrid=False, zeroline=False, visible=False),
                yaxis=dict(showgrid=False, zeroline=False, visible=False)
            )
            message = "Sorry. No data available"
            return "", "", "assets/no_data.png", "", "", "", "", "", "", fig_top1, fig_top10, message, region, year, month
    
    #if region and year:
    else:
        year_month = f"{year}-{month:02}"
        top1 = get_top1(year_month, region).to_dict('records')
        top10 = get_top10(year_month, region).to_dict('records')
        if len(top1) > 0:
            if clickData is not None:
                pointIndex = clickData['points'][0]['pointIndex']
                top1_artist = top10[pointIndex]['artist']
                top1_streams = f"{int(top10[pointIndex]['streams']):,} monthly streams"
                top1_image = top10[pointIndex]['image']
                top1_songs = get_top10_songs(year_month, region, top1_artist).to_dict('records')
            else:
                top1_artist = top10[0]['artist']
                top1_streams = f"{int(top10[0]['streams']):,} monthly streams"
                top1_image = top10[0]['image']
                top1_songs = get_top10_songs(year_month, region, top10[0]['artist']).to_dict('records')            
            
            top1_song1_streams = f"{int(top1_songs[0]['streams']):,} monthly streams" if len(top1_songs) > 0 else None
            top1_song2_streams = f"{int(top1_songs[1]['streams']):,} monthly streams" if len(top1_songs) > 1 else None
            top1_song3_streams = f"{int(top1_songs[2]['streams']):,} monthly streams" if len(top1_songs) > 2 else None
            track_url_1 = top1_songs[0]['id_song']
            track_url_2 = top1_songs[1]['id_song'] if len(top1_songs) > 1 else None
            track_url_3 = top1_songs[2]['id_song'] if len(top1_songs) > 2 else None
            embed_url_1 = create_spotify_embed_url(track_url_1)
            embed_url_2 = create_spotify_embed_url(track_url_2) if len(top1_songs) > 1 else None
            embed_url_3 = create_spotify_embed_url(track_url_3) if len(top1_songs) > 2 else None
            fig_top1 = get_figure_graph_top1(top1_artist, region, year_month)
            fig_top10 = get_figure_graph_top10(top1_artist, region, year_month)
            return top1_artist, top1_streams, top1_image, top1_song1_streams, top1_song2_streams, top1_song3_streams, embed_url_1, embed_url_2, embed_url_3, fig_top1, fig_top10, "", no_update, no_update, no_update
        else:
            fig_top1 = go.Figure()
            fig_top1.update_layout(
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                xaxis=dict(showgrid=False, zeroline=False, visible=False),
                yaxis=dict(showgrid=False, zeroline=False, visible=False)
            )
            fig_top10 = go.Figure()
            fig_top10.update_layout(
                xaxis=dict(showgrid=False, zeroline=False, visible=False),
                yaxis=dict(showgrid=False, zeroline=False, visible=False),
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
            )
            message = "Sorry. No data available"
            return "", "", "assets/no_data.png", "", "", "", "", "", "", fig_top1, fig_top10, message, no_update, no_update, no_update


# Main para ejecutar la aplicación
if __name__ == "__main__":
    app.run_server(debug=True)