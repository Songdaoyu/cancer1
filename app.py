import dash
from dash import dcc, html, Input, Output
import pandas as pd
import plotly.express as px
import plotly.graph_objs as go
from dash.exceptions import PreventUpdate
import os

# Load the data
df = pd.read_csv('survey lung cancer.csv')

# Convert binary columns to numeric
binary_columns = ['SMOKING', 'YELLOW_FINGERS', 'ANXIETY', 'PEER_PRESSURE', 'CHRONIC DISEASE', 
                  'FATIGUE', 'ALLERGY', 'WHEEZING', 'ALCOHOL CONSUMING', 'COUGHING', 
                  'SHORTNESS OF BREATH', 'SWALLOWING DIFFICULTY', 'CHEST PAIN']
df[binary_columns] = df[binary_columns].apply(pd.to_numeric)

# Create the Dash app
app = dash.Dash(__name__)
server = app.server  # Expose the server variable for Render

# Define the layout
app.layout = html.Div([
    html.H1("Lung Cancer Survey Analysis"),
    
    html.Div([
        html.Div([
            dcc.Dropdown(
                id='x-axis-dropdown',
                options=[{'label': col, 'value': col} for col in df.columns if col != 'LUNG_CANCER'],
                value='AGE',
                style={'width': '100%'}
            ),
        ], style={'width': '48%', 'display': 'inline-block'}),
        
        html.Div([
            dcc.Dropdown(
                id='y-axis-dropdown',
                options=[{'label': col, 'value': col} for col in df.columns if col != 'LUNG_CANCER'],
                value='SMOKING',
                style={'width': '100%'}
            ),
        ], style={'width': '48%', 'float': 'right', 'display': 'inline-block'})
    ]),
    
    dcc.Graph(id='scatter-plot'),
    
    html.Div([
        dcc.RadioItems(
            id='gender-filter',
            options=[{'label': i, 'value': i} for i in ['All', 'M', 'F']],
            value='All',
            labelStyle={'display': 'inline-block', 'marginRight': 10}
        ),
    ]),
    
    dcc.RangeSlider(
        id='age-range-slider',
        min=df['AGE'].min(),
        max=df['AGE'].max(),
        step=1,
        marks={i: str(i) for i in range(int(df['AGE'].min()), int(df['AGE'].max()) + 1, 5)},
        value=[df['AGE'].min(), df['AGE'].max()]
    ),
    
    dcc.Graph(id='symptoms-bar-chart'),
    
    dcc.Graph(id='correlation-heatmap'),
    
    html.Div(id='summary', style={'marginTop': 20})
])

# Callback for scatter plot
@app.callback(
    Output('scatter-plot', 'figure'),
    [Input('x-axis-dropdown', 'value'),
     Input('y-axis-dropdown', 'value'),
     Input('gender-filter', 'value'),
     Input('age-range-slider', 'value')]
)
def update_scatter_plot(x_col, y_col, gender, age_range):
    if not x_col or not y_col:
        raise PreventUpdate
    filtered_df = df[(df['AGE'] >= age_range[0]) & (df['AGE'] <= age_range[1])]
    if gender != 'All':
        filtered_df = filtered_df[filtered_df['GENDER'] == gender]
    
    fig = px.scatter(filtered_df, x=x_col, y=y_col, color='LUNG_CANCER',
                     title=f'{x_col} vs {y_col}', hover_data=['AGE', 'GENDER'])
    return fig

# Callback for symptoms bar chart
@app.callback(
    Output('symptoms-bar-chart', 'figure'),
    [Input('gender-filter', 'value'),
     Input('age-range-slider', 'value')]
)
def update_symptoms_bar_chart(gender, age_range):
    filtered_df = df[(df['AGE'] >= age_range[0]) & (df['AGE'] <= age_range[1])]
    if gender != 'All':
        filtered_df = filtered_df[filtered_df['GENDER'] == gender]
    
    symptoms = ['YELLOW_FINGERS', 'ANXIETY', 'PEER_PRESSURE', 'CHRONIC DISEASE', 'FATIGUE', 
                'ALLERGY', 'WHEEZING', 'ALCOHOL CONSUMING', 'COUGHING', 'SHORTNESS OF BREATH', 
                'SWALLOWING DIFFICULTY', 'CHEST PAIN']
    symptom_counts = filtered_df[symptoms].sum().sort_values(ascending=False)
    
    fig = px.bar(x=symptom_counts.index, y=symptom_counts.values, 
                 title='Prevalence of Symptoms', labels={'x': 'Symptom', 'y': 'Count'})
    return fig

# Callback for correlation heatmap
@app.callback(
    Output('correlation-heatmap', 'figure'),
    [Input('gender-filter', 'value'),
     Input('age-range-slider', 'value')]
)
def update_correlation_heatmap(gender, age_range):
    filtered_df = df[(df['AGE'] >= age_range[0]) & (df['AGE'] <= age_range[1])]
    if gender != 'All':
        filtered_df = filtered_df[filtered_df['GENDER'] == gender]
    
    corr_matrix = filtered_df.drop(['GENDER', 'LUNG_CANCER'], axis=1).corr()
    
    fig = go.Figure(data=go.Heatmap(
        z=corr_matrix.values,
        x=corr_matrix.columns,
        y=corr_matrix.columns,
        colorscale='RdBu',
        zmin=-1,
        zmax=1
    ))
    fig.update_layout(title='Correlation Heatmap of Factors')
    return fig

# Callback for summary
@app.callback(
    Output('summary', 'children'),
    [Input('gender-filter', 'value'),
     Input('age-range-slider', 'value')]
)
def update_summary(gender, age_range):
    filtered_df = df[(df['AGE'] >= age_range[0]) & (df['AGE'] <= age_range[1])]
    if gender != 'All':
        filtered_df = filtered_df[filtered_df['GENDER'] == gender]
    
    total_count = len(filtered_df)
    cancer_count = filtered_df['LUNG_CANCER'].value_counts().get('YES', 0)
    cancer_percentage = (cancer_count / total_count) * 100
    
    avg_age = filtered_df['AGE'].mean()
    top_symptom = filtered_df.drop(['GENDER', 'AGE', 'LUNG_CANCER'], axis=1).sum().idxmax()
    
    summary = f"""
    Based on the selected filters:
    - Total individuals: {total_count}
    - Number of lung cancer cases: {cancer_count} ({cancer_percentage:.2f}%)
    - Average age: {avg_age:.2f} years
    - Most common symptom: {top_symptom}
    
    Key observations:
    1. The scatter plot allows comparison of different factors, helping identify potential correlations with lung cancer.
    2. The symptoms bar chart highlights the most prevalent symptoms in the selected group.
    3. The correlation heatmap provides an overview of how different factors relate to each other.
    
    Remember that this is survey data and may not represent the entire population. Consult with healthcare professionals for medical advice.
    """
    
