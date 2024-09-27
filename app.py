import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import plotly.express as px
import pandas as pd

# Load the dataset
df = pd.read_csv('https://raw.githubusercontent.com/Songdaoyu/cancer1/refs/heads/main/survey%20lung%20cancer.csv')

# Initialize the Dash app
app = dash.Dash(__name__)
server = app.server

# App layout
app.layout = html.Div([
    html.H1("Lung Cancer Survey Analysis"),

    # Dropdown to select gender
    html.Label("Select Gender:"),
    dcc.Dropdown(
        id='gender-dropdown',
        options=[{'label': 'Male', 'value': 'M'}, {'label': 'Female', 'value': 'F'}],
        value='M',
        multi=False
    ),

    # Slider to select age range
    html.Label("Select Age Range:"),
    dcc.RangeSlider(
        id='age-slider',
        min=df['AGE'].min(),
        max=df['AGE'].max(),
        value=[df['AGE'].min(), df['AGE'].max()],
        marks={i: str(i) for i in range(int(df['AGE'].min()), int(df['AGE'].max())+1, 5)},
        step=1
    ),

    # Checkboxes for smoking habit
    html.Label("Include Smokers:"),
    dcc.Checklist(
        id='smoking-checklist',
        options=[{'label': 'Smokers', 'value': 1}, {'label': 'Non-Smokers', 'value': 2}],
        value=[1, 2],
        inline=True
    ),

    # Bar chart for chronic disease vs lung cancer
    dcc.Graph(id='bar-chart'),

    # Pie chart for gender distribution
    dcc.Graph(id='pie-chart'),

    # Scatter plot for age vs anxiety with lung cancer outcome
    dcc.Graph(id='scatter-plot')
])

# Callback to update the bar chart
@app.callback(
    Output('bar-chart', 'figure'),
    [Input('gender-dropdown', 'value'),
     Input('age-slider', 'value'),
     Input('smoking-checklist', 'value')]
)
def update_bar_chart(selected_gender, selected_age, smoking_status):
    filtered_df = df[(df['GENDER'] == selected_gender) &
                     (df['AGE'] >= selected_age[0]) &
                     (df['AGE'] <= selected_age[1]) &
                     (df['SMOKING'].isin(smoking_status))]
    fig = px.bar(filtered_df, x='CHRONIC DISEASE', y='AGE', color='LUNG_CANCER',
                 title="Chronic Disease vs Lung Cancer")
    return fig

# Callback to update the pie chart
@app.callback(
    Output('pie-chart', 'figure'),
    [Input('gender-dropdown', 'value')]
)
def update_pie_chart(selected_gender):
    filtered_df = df[df['GENDER'] == selected_gender]
    fig = px.pie(filtered_df, names='LUNG_CANCER', title="Lung Cancer Distribution by Gender")
    return fig

# Callback to update the scatter plot
@app.callback(
    Output('scatter-plot', 'figure'),
    [Input('gender-dropdown', 'value'),
     Input('age-slider', 'value')]
)
def update_scatter_plot(selected_gender, selected_age):
    filtered_df = df[(df['GENDER'] == selected_gender) &
                     (df['AGE'] >= selected_age[0]) &
                     (df['AGE'] <= selected_age[1])]
    fig = px.scatter(filtered_df, x='AGE', y='ANXIETY', color='LUNG_CANCER',
                     title="Age vs Anxiety with Lung Cancer Outcome",
                     size='FATIGUE ', hover_data=['WHEEZING'])
    return fig

# Run the app
if __name__ == '__main__':
    app.run_server(debug=True, host="0.0.0.0")
