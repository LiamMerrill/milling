import dash
from dash import Input, Output, State
from simulation import simulate_inventory
from utils import generate_people, generate_initial_nodes_and_edges, calculate_distance

def register_callbacks(app):
    
    # Main callback to initialize and update the simulation
    @app.callback(
        [
            Output('cytoscape-network', 'elements'),
            Output('interval-component', 'disabled')  # Output to enable/disable the interval component
        ],
        [
            Input('cytoscape-network', 'elements'),
            Input('start-simulation', 'n_clicks'),
            Input('stop-simulation', 'n_clicks'),
            Input('interval-component', 'n_intervals')
        ],
        [
            State('supply-center-units', 'value'),
            State('store-units', 'value'),
            State('people-range', 'value'),
            State('people-behavior', 'value'),  # People behavior algorithm
            State('distribution-algorithm', 'value')  # Distribution algorithm
        ]
    )

    def initialize_and_update_simulation(elements, n_clicks_start, n_clicks_stop, n_intervals, supply_center_units, store_units, people_range, people_behavior, distribution_algorithm):
        ctx = dash.callback_context
        people = [ele for ele in elements if 'data' in ele and 'type' in ele['data'] and ele['data']['type'] == 'person']

        # Ensure that `elements` is a valid list or initialize it
        if elements is None or not isinstance(elements, list):
            elements = []  # Initialize as an empty list if elements is invalid

        # If no context is triggered, return the elements unchanged
        if not ctx.triggered:
            return elements, True  # By default, the interval is disabled
        store_revenue=0
        # If 'start-simulation' triggered the callback
        if ctx.triggered[0]['prop_id'] == 'start-simulation.n_clicks' and n_clicks_start > 0:
            # Initialize nodes, edges, and people on start
            nodes, edges = generate_initial_nodes_and_edges(supply_center_units, store_units, store_revenue)
            people = generate_people()  # Initialize people here
            
            # Return nodes, edges, and people combined, and enable the interval
            return nodes + edges + people, False

        # If 'stop-simulation' triggered the callback
        if ctx.triggered[0]['prop_id'] == 'stop-simulation.n_clicks' and n_clicks_stop > 0:
            # Stop the simulation by disabling the interval
            return elements, True

        # If 'cytoscape-network.elements' triggered the callback (for updating distances)
        if ctx.triggered[0]['prop_id'] == 'cytoscape-network.elements':
            # Ensure `elements` is still a valid list
            if not isinstance(elements, list):
                return elements, True  # If it's not a list, return the elements without any changes

            # Update edge distances before the simulation starts
            nodes = [ele for ele in elements if 'inventory' in ele['data']]
            edges = [ele for ele in elements if 'source' in ele['data']]

            for edge in edges:
                source_node = next(node for node in elements if node['data']['id'] == edge['data']['source'])
                target_node = next(node for node in elements if node['data']['id'] == edge['data']['target'])

                # Calculate distance using the updated positions
                distance = calculate_distance(source_node['position'], target_node['position'])

                # Update the edge label to reflect the new distance
                edge['data']['label'] = f"Distance: {distance:.2f}"

            # Return updated elements with recalculated edge distances
            return elements, False

        # If 'interval-component' triggered the callback (for simulation updates)
        if ctx.triggered[0]['prop_id'] == 'interval-component.n_intervals' and n_intervals > 0:
            # Update the elements during the simulation run
            updated_elements = simulate_inventory(elements, people, people_behavior, distribution_algorithm)
            
            # Return the updated elements (nodes, edges, and people), keep interval enabled
            return updated_elements, False

        return elements, True
def update_edge_distances_on_move(node_positions):
    # Extract current node positions and edges
    nodes = [ele for ele in elements if 'inventory' in ele['data']]
    edges = [ele for ele in elements if 'source' in ele['data']]

    # Recalculate the distances and update edge labels
    for edge in edges:
        # Find the source and target nodes for each edge
        source_node = next(node for node in nodes if node['data']['id'] == edge['data']['source'])
        target_node = next(node for node in nodes if node['data']['id'] == edge['data']['target'])
        
        # Recalculate the distance based on the new node positions
        distance = calculate_distance(source_node['position'], target_node['position'])
        
        # Update the edge label with the new distance
        edge['data']['label'] = f"Distance: {distance:.2f}"

    return nodes + edges
