import random
import math
import pandas as pd
import numpy as np

# Function to generate the initial nodes and edges based on user input
def generate_initial_nodes_and_edges(supply_center_units, store_units, store_revenue):
    nodes = []
    
    # Set the warehouse in the center
    warehouse = {
        'data': {
            'id': 'Warehouse', 
            'label': f'Warehouse ({1000})', 
            'type': 'warehouse', 
            'inventory': 1000, 
            'revenue': 0},
        'position': {'x': 500, 'y': 300}  # Center position
    }
    nodes.append(warehouse)

    # Create supply centers, one on each side (left and right)
    supply_centers_positions = [{'x': 200, 'y': 300}, {'x': 800, 'y': 300}]
    
    for i in range(2):  # Ensure the loop is defined, so `i` gets a value
        supply_center = {
            'data': {
                'id': f'Supply_Center_{i+1}', 
                'label': f'Supply Center {i+1} ({supply_center_units} units)',  # Label with inventory
                'type': 'supply_center', 
                'inventory': supply_center_units, 
                'revenue': 0
            },
            'position': supply_centers_positions[i]  # Position for the supply center
        }
        nodes.append(supply_center)

    # Create stores, spread out on the left side and right side
    for i in range(8):  # Left side stores (associated with Supply Center 1)
        store = {
            'data': {
                'id': f'Store_{i+1}', 
                'label': f'Store {i+1} ({store_units}, ${store_revenue})', 
                'type': 'store', 
                'inventory': store_units, 
                'revenue': store_revenue},
            'position': {'x': random.randint(100, 300), 'y': random.randint(100, 500)}
        }
        nodes.append(store)

    for i in range(8):  # Right side stores (associated with Supply Center 2)
        store = {
            'data': {'id': f'Store_{i+9}', 'label': f'Store {i+9} ({store_units})', 'type': 'store', 'inventory': store_units, 'revenue': 0},
            'position': {'x': random.randint(700, 900), 'y': random.randint(100, 500)}
        }
        nodes.append(store)

    # Create edges between warehouse, supply centers, and stores
    edges = []
    for i in range(2):  # Connect warehouse to supply centers
        source_node = warehouse
        target_node = nodes[i+1]  # Supply centers
        distance = calculate_distance(source_node['position'], target_node['position'])
        
        edges.append({
            'data': {'source': 'Warehouse', 'target': f'Supply_Center_{i+1}', 'label': f"Distance: {distance:.2f}"}
        })
    
    for i in range(8):  # Connect Supply Center 1 to left side stores
        source_node = nodes[1]  # Supply Center 1
        target_node = nodes[i+3]  # Left side stores
        distance = calculate_distance(source_node['position'], target_node['position'])

        edges.append({
            'data': {'source': 'Supply_Center_1', 'target': f'Store_{i+1}', 'label': f"Distance: {distance:.2f}"}
        })

    for i in range(8):  # Connect Supply Center 2 to right side stores
        source_node = nodes[2]  # Supply Center 2
        target_node = nodes[i+11]  # Right side stores
        distance = calculate_distance(source_node['position'], target_node['position'])

        edges.append({
            'data': {'source': 'Supply_Center_2', 'target': f'Store_{i+9}', 'label': f"Distance: {distance:.2f}"}
        })

    return nodes, edges

# Function to calculate the Euclidean distance between two points
def calculate_distance(pos1, pos2):
    return np.sqrt((pos2['x'] - pos1['x']) ** 2 + (pos2['y'] - pos1['y']) ** 2)

# Function to update revenue and inventory for each node
def update_revenue_and_inventory(nodes, edges):
    for node in nodes:
        if node['data']['type'] == 'store':
            # Inventory and revenue changes are controlled elsewhere (e.g., in the people behavior function)
            pass
        elif node['data']['type'] == 'supply_center':
            node['data']['inventory'] = max(0, node['data']['inventory'] - 5)
            node['data']['revenue'] = node['data'].get('revenue', 0) + 2
        elif node['data']['type'] == 'warehouse':
            node['data']['inventory'] = max(0, node['data']['inventory'] - 10)
            node['data']['revenue'] = node['data'].get('revenue', 0) + 5

    return nodes, edges


# Function to generate people with random unit values, clustered randomly on the grid
def generate_people(num_people=100):
    people = []
    for i in range(num_people):
        dollars = np.random.randint(30, 101)  # Randomize dollars between 30 and 100
        units = 0  # Start with 0 units
        
        person = {
            'data': {
                'id': f'Person_{i+1}', 
                'label': f"${dollars}\nunits: {units}",  # Label showing dollars and units
                'type': 'person', 
                'nearest_store': None,
                'step_fraction':0,
                'dollars': dollars,  # Dollars initialization
                'units': units  # Units initialization
            },
            'position': {'x': random.randint(50, 950), 'y': random.randint(50, 950)}  # Position within the grid
        }
        people.append(person)
    
    return people
def simulate_person_movement(start_pos, end_pos, step_fraction):
    """ Calculate the next position of the person along the path to the store. """
    x = (1 - step_fraction) * start_pos['x'] + step_fraction * end_pos['x']
    y = (1 - step_fraction) * start_pos['y'] + step_fraction * end_pos['y']
    return {'x': x, 'y': y}
