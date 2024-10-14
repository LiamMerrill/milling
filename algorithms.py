import random
import numpy as np
import pandas as pd
from utils import calculate_distance, simulate_person_movement


def people_behavior_algo1(people, stores, iteration_count):
    """
    Simulates the behavior of people, including movement to and from stores, and consumption of units over time.
    
    :param people: List of people in the simulation.
    :param stores: List of stores in the simulation.
    :param iteration_count: The current iteration of the simulation, used for unit consumption.
    :return: Updated people and stores after simulating behavior.
    """
    
    for person in people:
        # Skip the person if they don't have the required keys
        if 'units' not in person['data'] or 'dollars' not in person['data']:
            continue

        speed = 2  # Set the speed of movement (can be adjusted)

        # Check if the person is at home and consuming units
        if person['data'].get('at_home', False):
            # Consume 1 unit every 10 iterations
            if iteration_count % 10 == 0 and person['data']['units'] > 0:
                person['data']['units'] -= 1
            person['data']['label'] = f"Units: {person['data']['units']}, $: {person['data']['dollars']}"

            # If person has no units left, go to the store
            if person['data']['units'] <= 0:
                person['data']['at_home'] = False
                person['data']['at_store'] = False
                person['data']['target_store'] = None  # Reset target store to pick a new one
                person['data']['step_fraction'] = 0  # Reset step_fraction for movement

        # If the person is heading to the store
        if not person['data'].get('at_store', False) and not person['data'].get('at_home', False):
            # If person hasn't selected a store yet, find the nearest one
            if person['data'].get('target_store') is None:
                distances = [
                    {'store': store, 'distance': calculate_distance(person['position'], store['position'])}
                    for store in stores
                ]
                nearest_store = min(distances, key=lambda x: x['distance'])['store']

                # Set the target store and save home position
                person['data']['target_store'] = nearest_store['data']['id']
                person['data']['home_position'] = person['position']
                person['data']['step_fraction'] = 0  # Reset step_fraction for movement

            # Get the target store details
            target_store = next(store for store in stores if store['data']['id'] == person['data']['target_store'])
            target_store_position = target_store['position']

            # Move towards the store
            total_distance = calculate_distance(person['position'], target_store_position)
            
            if total_distance > 0:
                step_fraction = person['data']['step_fraction'] + (speed / total_distance)
                person['data']['step_fraction'] = min(step_fraction, 1)  # Ensure it doesn't exceed 1

                # Simulate movement towards the store
                new_pos = simulate_person_movement(person['data']['home_position'], target_store_position, step_fraction)
                person['position'] = new_pos

            # Check if the person has reached the store
            if person['data']['step_fraction'] >= 1:
                person['data']['at_store'] = True  # Mark that they reached the store
                person['data']['step_fraction'] = 0  # Reset for return journey

                # Handle the transaction when the person arrives at the store
                if target_store['data']['inventory'] > 0 and person['data']['dollars'] >= 2:
                    units_to_buy = min(5, target_store['data']['inventory'], person['data']['dollars'] // 2)
                    target_store['data']['inventory'] -= units_to_buy
                    target_store['data']['revenue'] = target_store['data'].get('revenue', 0) + units_to_buy * 2
                    person['data']['units'] += units_to_buy
                    person['data']['dollars'] -= units_to_buy * 2
                    person['data']['label'] = f"Units: {person['data']['units']}, $: {person['data']['dollars']}"


        # If the person has reached the store, they should return to their origin
        elif person['data'].get('at_store', False):
            home_position = person['data']['home_position']
            current_position = person['position']
            total_distance = calculate_distance(current_position, home_position)

            if total_distance > 0:
                step_fraction = person['data']['step_fraction'] + (speed / total_distance)
                person['data']['step_fraction'] = min(step_fraction, 1)

                # Simulate movement back to the home position
                new_pos = simulate_person_movement(current_position, home_position, step_fraction)
                person['position'] = new_pos

                # Check if they have returned home
                if person['data']['step_fraction'] >= 1:
                    person['data']['at_store'] = False  # Mark that they've returned to their origin
                    person['data']['at_home'] = True    # Mark them as being at home
                    person['data']['step_fraction'] = 0  # Reset for next trip

    return people, stores


def people_behavior_algo2(people, stores):
    people_df = pd.DataFrame(people)
    stores_df = pd.DataFrame(stores)
    
    for idx, person in people_df.iterrows():
        # Check if 'units' exists for the person
        if 'units' not in person:
            print(f"Error: 'units' key missing for person {idx}.")
            continue
        
        # Prioritize stores with higher inventory and consider proximity
        stores_df['distance'] = stores_df.apply(lambda store: calculate_distance(person['position'], store['position']), axis=1)
        prioritized_stores = stores_df.sort_values(by=['data.inventory', 'distance'], ascending=[False, True])
        
        if not prioritized_stores.empty and person['units'] > 0:
            chosen_store = prioritized_stores.iloc[0]
            chosen_store_idx = prioritized_stores.index[0]
            stores_df.at[chosen_store_idx, 'inventory'] -= 1
            people_df.at[idx, 'units'] -= 1
            
    return people_df, stores_df

def distribution_algo1(warehouse, supply_centers, stores, edges, iteration_count):
    """
    Distributes units and revenue between warehouse, supply centers, and stores based on edges.
    
    :param warehouse: Warehouse node.
    :param supply_centers: List of supply centers.
    :param stores: List of stores.
    :param edges: List of edges connecting stores and supply centers.
    :param iteration_count: The current iteration of the simulation, used for store restocking.
    :return: Updated warehouse, supply centers, and stores.
    """
    
    # Helper function to find the supply center for a store using edges
    def find_supply_center_for_store(store_id):
        for edge in edges:
            if edge['data']['target'] == store_id:
                return edge['data']['source']  # Return the supply center's ID

    # Step 1: Stores send money to the supply center only if their revenue reaches $100
    for center in supply_centers:
        for store in stores:
            supply_center_id = find_supply_center_for_store(store['data']['id'])
            if supply_center_id == center['data']['id']:
                # Only send money if the store's revenue reaches $100
                if store['data']['revenue'] >= 100:
                    center['data']['revenue'] += store['data']['revenue']  # Transfer store's revenue to supply center
                    store['data']['revenue'] = 0  # Reset store revenue after transfer

        # Update the supply center's label to reflect the updated inventory and revenue
        center['data']['label'] = f"Supply Center {center['data']['id']} ({int(center['data']['inventory'])} units, ${center['data']['revenue']})"

    # Step 2: Supply centers send all their money to the warehouse
    total_center_revenue = 0
    for center in supply_centers:
        total_center_revenue += center['data']['revenue']
        warehouse['data']['revenue'] += center['data']['revenue']
        center['data']['revenue'] = 0  # Reset the supply center's revenue after sending it to the warehouse

    # Step 3: Warehouse produces units based on revenue (2 units per $1)
    units_produced = warehouse['data']['revenue'] * 2
    warehouse['data']['inventory'] += units_produced
    warehouse['data']['revenue'] = 0  # Reset warehouse revenue after producing units

    # Step 4: Warehouse distributes units proportionally to the supply centers based on the revenue they sent
    if total_center_revenue > 0:
        for center in supply_centers:
            revenue_fraction = center['data']['revenue'] / total_center_revenue
            units_to_send = revenue_fraction * warehouse['data']['inventory']
            warehouse['data']['inventory'] -= units_to_send
            center['data']['inventory'] += units_to_send

            # Update the supply center's label to reflect new inventory
            center['data']['label'] = f"{center['data']['id']} ({int(center['data']['inventory'])} units, ${center['data']['revenue']})"

    # Step 5: Restock stores when they hit 0 units after a 10-iteration delay
    for store in stores:
        if store['data']['inventory'] == 0:
            if 'restock_timer' not in store['data'] or store['data']['restock_timer'] is None:
                store['data']['restock_timer'] = iteration_count  # Initialize restock timer
            
            # Check if 10 iterations have passed since the store ran out of inventory
            elif iteration_count - store['data']['restock_timer'] >= 10:
                store['data']['inventory'] = 100  # Restock 100 units
                store['data']['restock_timer'] = None  # Reset restock timer after restocking
        else:
            store['data']['restock_timer'] = None  # Reset restock timer if store still has inventory
        
        # Update the store's label to reflect the current inventory and revenue
        store['data']['label'] = f"{store['data']['id']} ({int(store['data']['inventory'])} units, ${store['data']['revenue']})"

    return warehouse, supply_centers, stores

# Algorithm 2: Prioritize supply centers that are selling more
def distribution_algo2(warehouse, supply_centers):
    total_supply = warehouse['inventory']
    # Sort supply centers by their revenue or sales performance
    supply_centers_df = pd.DataFrame(supply_centers)
    prioritized_centers = supply_centers_df.sort_values(by='data.revenue', ascending=False)
    
    for idx, center in prioritized_centers.iterrows():
        allocation = total_supply // (len(supply_centers) + 1)
        supply_centers_df.at[idx, 'inventory'] += allocation
        warehouse['inventory'] -= allocation
    
    return warehouse, supply_centers_df.to_dict('records')
