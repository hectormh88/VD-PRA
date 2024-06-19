import dash
from dash import html, dcc
import dash_bootstrap_components as dbc



app = dash.Dash(__name__,
                )
server = app.server
app.title = 'Migración, crimen y conflictos: Análisis visual de datos'




# Layout de la aplicación

app.layout = html.Div([
    html.H1('Migración, crimen y conflictos: Análisis visual de datos', style={'textAlign': 'center', 'fontWeight': 'bold'}),
])

# Main para ejecutar la aplicación
if __name__ == "__main__":
    app.run_server(debug=True)