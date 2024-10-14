from dash import Dash
from layout import create_layout
from callbacks import register_callbacks
from utils import generate_initial_nodes_and_edges, generate_people

# Provide default values for initial setup
default_supply_center_units = 250
default_store_units = 100
default_store_revenue = 0

# Initialize nodes, edges, and people with default values
nodes, edges = generate_initial_nodes_and_edges(default_supply_center_units, default_store_units, default_store_revenue)
people = generate_people()  # Generate people

# Combine nodes, edges, and people into one elements list for Cytoscape
elements = nodes + edges + people

# Initialize the Dash app
app = Dash(__name__)

# Set the layout using the function from layout.py, passing the full elements list (including people)
app.layout = create_layout(elements, edges)

# Register callbacks from callbacks.py
register_callbacks(app)

# Run the app server
if __name__ == '__main__':
    app.run_server(debug=True, port=8051)
