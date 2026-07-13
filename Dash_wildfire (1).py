import dash
from dash import dcc, html, Input, Output
import plotly.express as px
import pandas as pd
import numpy as np

# Création des données simulées
np.random.seed(42)

regions = ['Nord-Ouest', 'Sud-Est', 'Centre', 'Sud-Ouest', 'Nord-Est', 'Île-de-France']
years = list(range(2018, 2024))
months = ['Jan', 'Fév', 'Mar', 'Avr', 'Mai', 'Juin', 
          'Juil', 'Aoû', 'Sep', 'Oct', 'Nov', 'Déc']

fire_season = {
    'Jan': 0.3, 'Fév': 0.4, 'Mar': 0.6, 'Avr': 0.8,
    'Mai': 1.2, 'Juin': 1.8, 'Juil': 2.2, 'Aoû': 2.5,
    'Sep': 1.8, 'Oct': 1.0, 'Nov': 0.5, 'Déc': 0.3
}

data = []
for region in regions:
    for year in years:
        region_risk = {
            'Nord-Ouest': 1.2,
            'Sud-Est': 1.8,
            'Centre': 0.9,
            'Sud-Ouest': 1.5,
            'Nord-Est': 1.1,
            'Île-de-France': 0.7
        }
        
        if year >= 2020:
            year_factor = 1.0 + (year - 2020) * 0.15
        else:
            year_factor = 1.0
        
        for month in months:
            base_area = 100 * region_risk[region] * fire_season[month] * year_factor
            area_noise = np.random.normal(0, 30)
            area = max(10, int(base_area + area_noise))
            
            base_pixels = 50 * region_risk[region] * fire_season[month] * year_factor
            pixel_noise = np.random.normal(0, 15)
            pixels = max(5, int(base_pixels + pixel_noise))
            
            data.append({
                'Region': region,
                'Year': year,
                'Month': month,
                'Superficie_ha': area,
                'Pixels': pixels
            })

df = pd.DataFrame(data)

# Création de l'application Dash
app = dash.Dash(__name__)

# Mise en page
app.layout = html.Div([
    html.H1("🔥 Tableau de Bord des Incendies de Végétation", 
            style={'textAlign': 'center', 'color': '#2c3e50', 'padding': '20px'}),
    
    html.Hr(),
    
    html.Div([
        # Colonne gauche - Contrôles
        html.Div([
            html.H4("📅 Sélectionnez l'Année"),
            dcc.Dropdown(
                id='year-dropdown',
                options=[{'label': 'Toutes les années', 'value': 'All'}] + 
                        [{'label': str(y), 'value': y} for y in years],
                value='All',
                style={'width': '100%'}
            ),
            
            html.Br(),
            
            html.H4("📍 Sélectionnez la Région"),
            dcc.RadioItems(
                id='region-radio',
                options=[{'label': 'Toutes les régions', 'value': 'All'}] + 
                        [{'label': r, 'value': r} for r in regions],
                value='All',
                labelStyle={'display': 'block', 'padding': '5px 0'}
            ),
            
            html.Hr(),
            
            html.H4("📊 Résumé"),
            html.Div(id='summary-output', style={
                'backgroundColor': '#f8f9fa',
                'padding': '15px',
                'borderRadius': '5px'
            })
            
        ], style={'width': '30%', 'float': 'left', 'padding': '20px', 
                  'backgroundColor': '#f8f9fa', 'borderRadius': '10px'}),
        
        # Colonne droite - Graphiques
        html.Div([
            html.H4("📊 Graphiques", style={'textAlign': 'center'}),
            dcc.Graph(id='pie-chart', style={'height': '400px'}),
            html.Br(),
            dcc.Graph(id='bar-chart', style={'height': '400px'})
        ], style={'width': '65%', 'float': 'right', 'padding': '20px'})
        
    ], style={'display': 'flex', 'justifyContent': 'space-between'})
])

# Callback
@app.callback(
    [Output('pie-chart', 'figure'),
     Output('bar-chart', 'figure'),
     Output('summary-output', 'children')],
    [Input('year-dropdown', 'value'),
     Input('region-radio', 'value')]
)
def update_charts(selected_year, selected_region):
    filtered_df = df.copy()
    
    if selected_year != 'All':
        filtered_df = filtered_df[filtered_df['Year'] == selected_year]
    
    if selected_region != 'All':
        filtered_df = filtered_df[filtered_df['Region'] == selected_region]
    
    # Pie Chart
    pie_data = filtered_df.groupby('Month')['Superficie_ha'].mean().reset_index()
    fig_pie = px.pie(
        pie_data, 
        values='Superficie_ha', 
        names='Month', 
        title='Superficie Moyenne des Incendies',
        hole=0.3,
        color_discrete_sequence=px.colors.qualitative.Set3
    )
    fig_pie.update_traces(textposition='inside', textinfo='percent+label')
    
    # Bar Chart
    bar_data = filtered_df.groupby('Month')['Pixels'].mean().reset_index()
    fig_bar = px.bar(
        bar_data, 
        x='Month', 
        y='Pixels',
        title='Nombre Moyen de Pixels',
        color='Month',
        color_discrete_sequence=px.colors.qualitative.Set3
    )
    fig_bar.update_layout(xaxis_title='Mois', yaxis_title='Pixels')
    
    # Summary
    summary = html.Div([
        html.P(f"🔥 Superficie totale: {filtered_df['Superficie_ha'].sum():,.0f} ha", 
               style={'fontWeight': 'bold'}),
        html.P(f"📊 Pixels totaux: {filtered_df['Pixels'].sum():,.0f}"),
        html.P(f"📅 Enregistrements: {len(filtered_df):,}"),
        html.P(f"📍 Régions: {filtered_df['Region'].nunique()}"),
        html.P(f"📆 Années: {filtered_df['Year'].nunique()}")
    ])
    
    return fig_pie, fig_bar, summary

if __name__ == '__main__':
    print("\n" + "="*70)
    print("🚀 LANCEMENT DE L'APPLICATION DASH")
    print("📊 Dashboard accessible à : http://localhost:8050")
    print("📊 Ou à : http://127.0.0.1:8050")
    print("="*70 + "\n")
    
    app.run()