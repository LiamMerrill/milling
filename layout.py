import dash_cytoscape as cyto
from dash import html, dcc

def create_layout(nodes, edges):
    return html.Div([
        html.H1("X Inventory Distribution Game", style={'text-align': 'center', 'font-family': 'Helvetica, sans-serif'}),

        # User inputs for starting values
        html.Div([
            html.Label('Supply Center Starting Units:', style={'font-family': 'Helvetica, sans-serif'}),
            dcc.Input(id='supply-center-units', type='number', value=250, min=0, style={'font-family': 'Helvetica, sans-serif'}),

            html.Label('Store Starting Units:', style={'font-family': 'Helvetica, sans-serif'}),
            dcc.Input(id='store-units', type='number', value=100, min=0, style={'font-family': 'Helvetica, sans-serif'}),

            html.Label('Range for People Units (min and max):', style={'font-family': 'Helvetica, sans-serif'}),
            dcc.RangeSlider(id='people-range', min=5, max=500, step=5, value=[5, 20],
                            marks={5: '5', 500: '500'}, 
                            tooltip={"placement": "bottom", "always_visible": True}),

            html.Label('Select People Behavior Algorithm:', style={'font-family': 'Helvetica, sans-serif'}),
            dcc.Dropdown(id='people-behavior', options=[
                {'label': 'Algorithm 1', 'value': 'algo1'},
                {'label': 'Algorithm 2', 'value': 'algo2'}
            ], value='algo1', style={'font-family': 'Helvetica, sans-serif'}),

            html.Label('Select Distribution Algorithm:', style={'font-family': 'Helvetica, sans-serif'}),
            dcc.Dropdown(id='distribution-algorithm', options=[
                {'label': 'Algorithm 1', 'value': 'algo1'},
                {'label': 'Algorithm 2', 'value': 'algo2'}
            ], value='algo1', style={'font-family': 'Helvetica, sans-serif'}),
        ], style={'padding': '20px', 'display': 'grid', 'grid-template-columns': 'repeat(2, 1fr)', 'gap': '10px'}),

        # Cytoscape component for network visualization
        cyto.Cytoscape(
            id='cytoscape-network',
            elements=nodes + edges,
            style={'width': '100%', 'height': '600px'},
            layout={'name': 'preset'},
            minZoom=0.5,  # Set minimum zoom level (can zoom out only up to 50% of the original size)
            maxZoom=1.0,
            stylesheet=[
                # Warehouse styling
                {'selector': '[type = "warehouse"]', 'style': {
                    'content': 'data(label)',
                    'background-color': '#2ECC40',
                    'width': 'mapData(inventory, 0, 500, 30, 60)',
                    'height': 'mapData(inventory, 0, 500, 30, 60)',
                    'color': 'black',
                    'background-opacity': 'mapData(revenue, 0, 1000, 0.2, 1)'  # Darker with more revenue
                }},
                {'selector': '[type = "supply_center"]', 'style': {
                    'content': 'data(label)',  # Show label (inventory units)
                    'background-color': '#3498DB',
                    'content': 'data(label)',
                    'width': 'mapData(inventory, 0, 500, 30, 60)',  # Dynamic width based on inventory
                    'height': 'mapData(inventory, 0, 500, 30, 60)',  # Dynamic height based on inventory
                    'color': 'black',
                    'background-opacity': 'mapData(revenue, 0, 1000, 0.2, 1)'
                }},
                {'selector': 'edge', 'style': {
                    'content': 'data(label)',  # Display the label for edges
                    'line-color': '#9dbaea',
                    'width': 2,
                    'target-arrow-shape': 'triangle',
                    'target-arrow-color': '#9dbaea',
                    'font-size': 12,  # Optional: adjust font size
                    'color': 'black'  # Color of the text (label)
                }},
                # Store styling
                {'selector': '[type = "store"]', 'style': {
                    'content': 'data(label)', 
                    'background-color': '#FF4136',
                    'width': 'mapData(inventory, 0, 200, 30, 70)', 
                    'height': 'mapData(inventory, 0, 200, 30, 70)',
                    'color': 'black',
                    'background-opacity': 'mapData(revenue, 0, 1000, 0.2, 1)'  # Darker with more revenue
                }},
                # Person styling
                {'selector': '[type = "person"]', 'style': {
                    'shape' : "ellipse",
                    'content': 'data(label)',  # Show the label (dollars and units)
                    'background-color': 'black',
                    'background-opacity': 0.1,
                    'text-wrap': 'wrap',  # Enable multiline labels
                    'text-valign': 'center',
                    'font-size': 12,  # Adjust font size if necessary
                    'locked': True,
                    'grabbed': False,
                }},
            ],
            userPanningEnabled=True,
            boxSelectionEnabled=True,
            autoungrabify=False,  # Nodes can be moved by the user
            autolock=False       # Allows dragging nodes freely
        ),

        # Buttons for starting/stopping simulation
        html.Div([
            html.Button('Start Simulation', id='start-simulation', n_clicks=0, style={'font-family': 'Helvetica, sans-serif'}),
            html.Button('Stop Simulation', id='stop-simulation', n_clicks=0, style={'font-family': 'Helvetica, sans-serif'}),
            dcc.Store(id='iteration-count-store', data=0),
            dcc.Interval(id='interval-component', interval=1000, n_intervals=0, disabled=True),
        ], style={'text-align': 'center', 'padding': '20px'})
    ], style={'font-family': 'Helvetica, sans-serif'})  # Apply font-family globally
