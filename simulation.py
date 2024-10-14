import numpy as np
from algorithms import people_behavior_algo1, people_behavior_algo2, distribution_algo1, distribution_algo2
from utils import update_revenue_and_inventory, calculate_distance
print(f"Calling simulate_inventory with people_behavior: {people_behavior_algo1}, distribution_algorithm: {distribution_algo1}")

def simulate_inventory(elements, people, selected_people_algo, selected_distribution_algo):
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
        people, stores = people_behavior_algo1(people, stores)
    elif selected_people_algo == 'algo2':
        people, stores = people_behavior_algo2(people, stores)

    # Resupply stores from supply centers when inventory is below threshold
    for store in stores:
        if store['data']['inventory'] < 20:  # Resupply threshold for stores
            if supply_centers:
                # Find the nearest supply center
                distances = [
                    {'supply_center': sc, 'distance': calculate_distance(store['position'], sc['position'])}
                    for sc in supply_centers
                ]
                nearest_supply_center = min(distances, key=lambda x: x['distance'])['supply_center']
                
                # Resupply from the nearest supply center
                if nearest_supply_center['data']['inventory'] > 0:
                    transfer_amount = min(20 - store['data']['inventory'], nearest_supply_center['data']['inventory'])  # Resupply up to the threshold
                    store['data']['inventory'] += transfer_amount
                    nearest_supply_center['data']['inventory'] -= transfer_amount

    # Apply selected distribution algorithm (e.g., warehouse to supply centers)
    if selected_distribution_algo == 'algo1':
        warehouse, supply_centers, stores = distribution_algo1(warehouse, supply_centers, stores)
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


    # Update labels to reflect inventory for supply centers and stores
    for supply_center in supply_centers:
        supply_center['data']['label'] = f"Supply Center {supply_center['data']['id']} ({supply_center['data']['inventory']} units)"
    
    for store in stores:
        store['data']['label'] = f"{store['data']['id']} ({store['data']['inventory']} units, ${store['data']['revenue']})"
    
    # Return the combined list of nodes, edges, and people
    return updated_nodes + updated_edges + people
