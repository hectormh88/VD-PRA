import dash
from dash import html, dcc
import dash_bootstrap_components as dbc
import plotly.express as px
from plotly.subplots import make_subplots
import plotly.graph_objects as go

from queries import get_df1, get_df2, get_df3, get_df4, get_df5, get_df6, get_df7, continent_translation, gender_translation

STYLESHEET = dbc.themes.COSMO



app = dash.Dash(__name__,
                external_stylesheets=[STYLESHEET],
                prevent_initial_callbacks='initial_duplicate'
                )
server = app.server
app.title = 'Migración, crimen y conflictos: Análisis visual de datos'




# Funciones de gráficos

def get_graph1():
    
    df = get_df1()
    df['Continent'] = df['Continent'].map(continent_translation)
    
    fig = px.line(
        df,
        x='Year',
        y='Deaths in ongoing conflicts',
        color='Continent',
        log_y=False,
        labels={
            'Year': 'Año',
            'Deaths in ongoing conflicts': 'Muertes en conflictos en curso',
            'Continent': 'Continente'
        }
    )
    
    return fig

def get_graph2(migrants_variable):
    
    df = get_df2()
    
    fig = px.scatter(df, x='GDP per capita', y='Criminality',
                    size=migrants_variable, color='Deaths in conflicts',
                    hover_name='Country', log_x=True, size_max=40,
                    opacity=0.25,
                    labels={
                        'GDP per capita': 'PIB per capita',
                        'Criminality': 'Criminalidad',
                        'Country': 'País',
                        'Deaths in conflicts': 'Muertes en conflictos'
                    })
    fig.update_layout(coloraxis_colorbar=dict(title="Muertes en conflictos"))

    fig.update_layout(
        xaxis_title="GDP per capita",
        yaxis_title="Criminality",
        legend_title="Deaths in conflicts",

        xaxis=dict(
            showline=True,
            showgrid=False,
            showticklabels=True,
            linecolor='rgb(204, 204, 204)',
            linewidth=2,
            ticks='outside',
            tickfont=dict(
                family='Arial',
                size=12,
                color='rgb(82, 82, 82)',
            ),
        ),
        height=600,
    )
    return fig


def get_graph3():
    
    df = get_df3()
    
    fig = px.choropleth(df, locations="Country ISO",
                        color="GDP per capita", hover_name="Country",
                        projection="natural earth",
                        color_continuous_scale=px.colors.sequential.Viridis)
    fig.update_layout(coloraxis_colorbar=dict(title="PIB per capita"))

    fig.add_trace(px.scatter_geo(
        data_frame=df, locations="Country ISO",
        size="Immigrants", hover_name="Country").data[0],
        )

    fig.update_layout(
        height=600
    )

    return fig


def get_graph4(continent):
    df = get_df4(continent)
    df['Gender'] = df['Gender'].map(gender_translation)
    
    fig = px.bar(
        df, x='Year', y='Migrants', color='Gender', barmode='group',
        labels={'Year': 'Año', 'Migrants': 'Número de emigrantes', 'Gender': 'Género'},
    )
    
    return fig

continents = ['Africa', 'Asia', 'Europe', 'Northern America', 'Oceania', 'Latin America and the Caribbean']

def get_graph4_combined(continents):
    fig = make_subplots(rows=3, cols=2, subplot_titles=[continent_translation[c] for c in continents])
    
    for i, continent in enumerate(continents):
        graph = get_graph4(continent)
        
        for trace in graph['data']:
            if i > 0:
                trace.showlegend = False
            fig.add_trace(trace, row=i//2 + 1, col=i%2 + 1)
    
    fig.update_layout(
        height=1000, width=1000,
        )
    
    return fig


def get_graph6():
    df = get_df6()
    
    fig = px.choropleth(df, locations="Country ISO",
                        color="Deaths in ongoing conflicts",
                        hover_name="Country",
                        projection="natural earth",
                        color_continuous_scale=px.colors.sequential.Viridis,
                        hover_data={
                            'Country ISO': False, 
                            'Deaths in ongoing conflicts': True, 
                            'Emigrants rate': True
                        })
    fig.update_layout(coloraxis_colorbar=dict(title="Muertes en conflictos en curso"))

    scatter = px.scatter_geo(df, 
                             locations="Country ISO",
                             size="Emigrants rate", 
                             hover_name="Country",
                             hover_data={
                                 'Country ISO': False, 
                                 'Emigrants rate': True
                             })

    scatter.update_traces(hovertemplate='Tasa de emigrantes: %{marker.size:.2f}<br>País: %{hovertext}')
    
    fig.add_trace(scatter.data[0])

    fig.update_layout(
        height=600
    )
    
    return fig


def get_graph7():
    flows = get_df7()

    # Crear el mapa
    fig = go.Figure()

    # Agregar los flujos migratorios como líneas en el mapa con suavizado y puntas de flecha
    for i, row in flows.iterrows():
        origin = row['Origin ISO']
        destination = row['Destination ISO']
        
        # Coordenadas de origen y destino utilizando el código ISO
        fig.add_trace(go.Scattergeo(
            locationmode='ISO-3',
            locations=[origin, destination],
            mode='lines',
            line=dict(width=2, color='blue'),  # Todas las flechas tienen el mismo grosor y color
            opacity=0.6,
            hoverinfo='text',
            text=f"Desde {row['Region of origin']} a {row['Region of destination']}<br>Emigrantes: {row['Migrants']}"
        ))
        
        # Agregar punta de flecha proporcional en el destino
        fig.add_trace(go.Scattergeo(
            locationmode='ISO-3',
            locations=[destination],
            mode='markers',
            marker=dict(size=10, symbol='triangle-up', color='blue'),
            opacity=0.8,
            hoverinfo='skip'
        ))
        
        # Agregar un punto en el origen
        fig.add_trace(go.Scattergeo(
            locationmode='ISO-3',
            locations=[origin],
            mode='markers',
            marker=dict(size=6, color='blue', symbol='circle'),
            opacity=0.8,
            hoverinfo='skip'
        ))

    # Configurar las propiedades del mapa
    fig.update_layout(
        showlegend=False,
        geo=dict(
            showcoastlines=True,
            coastlinecolor="RebeccaPurple",
            showland=True,
            landcolor="LightGreen",
            showocean=True,
            oceancolor="LightBlue",
            projection_type='natural earth',
            showcountries=True,  # Mostrar las fronteras de los países
            countrycolor="Black"  # Color de las fronteras de los países
        ),
        height=800
    )
    return fig
    


# Layout de la aplicación

app.layout = html.Div([
    html.H1('Migración, crimen y conflictos: Análisis visual de datos', style={'textAlign': 'center', 'fontWeight': 'bold'}),
])

# Main para ejecutar la aplicación
if __name__ == "__main__":
    app.run_server(debug=True)