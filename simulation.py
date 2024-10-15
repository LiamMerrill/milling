import numpy as np
from algorithms import people_behavior_algo1, people_behavior_algo2, distribution_algo1, distribution_algo2
from utils import update_revenue_and_inventory, calculate_distance
print(f"Calling simulate_inventory with people_behavior: {people_behavior_algo1}, distribution_algorithm: {distribution_algo1}")

def simulate_inventory(elements, people, selected_people_algo, selected_distribution_algo, iteration_count):
    # Filter nodes and edges
    nodes = [ele for ele in elements if 'inventory' in ele['data']]
    edges = [ele for ele in elements if 'source' in ele['data']]
    people_nodes = [ele for ele in elements if 'units' in ele['data']]  # Extract people nodes
    
    # Separate out the warehouse, supply centers, and stores
    warehouse = next(n for n in nodes if n['data']['type'] == 'warehouse')
    supply_centers = [n for n in nodes if n['data']['type'] == 'supply_center']
    stores = [n for n in nodes if n['data']['type'] == 'store']
    
    # Apply selected people behavior algorithm (people buy from stores)
    if selected_people_algo == 'algo1':
        people, stores = people_behavior_algo1(people, stores, iteration_count)
    elif selected_people_algo == 'algo2':
        people, stores = people_behavior_algo2(people, stores)

    # Remove the 20-unit minimum resupply logic
    # Previously here we resupplied stores with less than 20 units

    # Apply selected distribution algorithm (e.g., warehouse to supply centers)
    if selected_distribution_algo == 'algo1':
        warehouse, supply_centers, stores = distribution_algo1(warehouse, supply_centers, stores, edges, iteration_count)
    elif selected_distribution_algo == 'algo2':
        warehouse, supply_centers = distribution_algo2(warehouse, supply_centers)

    # Update the edge distances and labels
    for edge in edges:
        # Find the source and target nodes for each edge
        source_node = next(node for node in nodes if node['data']['id'] == edge['data']['source'])
        target_node = next(node for node in nodes if node['data']['id'] == edge['data']['target'])
        
        # Calculate the Euclidean distance between the source and target nodes
        distance = calculate_distance(source_node['position'], target_node['position'])
        
        # Update the edge label to reflect the distance
        edge['data']['label'] = f"Distance: {distance:.2f}"

    # Update inventory and revenue using the function in utils.py
    updated_nodes, updated_edges = update_revenue_and_inventory(nodes, edges)
    
    warehouse['data']['label'] = f"{warehouse['data']['id']}({int(warehouse['data']['inventory'])} units, ${int(warehouse['data']['revenue'])})"

    for supply_center in supply_centers:
        supply_center['data']['label'] = f"{supply_center['data']['id']} ({int(supply_center['data']['inventory'])} units, ${int(supply_center['data']['revenue'])})"

    # Update labels to reflect inventory for supply centers and stores
    for store in stores:
        store['data']['label'] = f"{store['data']['id']} ({store['data']['inventory']} units, ${store['data']['revenue']})"
    
    # Return the combined list of nodes, edges, and people
    return updated_nodes + updated_edges + people