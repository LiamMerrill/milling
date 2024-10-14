import random
import numpy as np
import pandas as pd
from utils import calculate_distance, simulate_person_movement


def people_behavior_algo1(people, stores):
    for person in people:
        # Skip the person if they don't have the required keys
        if 'units' not in person['data'] or 'dollars' not in person['data']:
            continue

        speed = 3  # Set the speed of movement (can be adjusted)

        # Check if the person is heading to the store
        if not person['data'].get('at_store', False):
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

        # If the person has reached the store, they should return to their origin
        else:
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

def distribution_algo1(warehouse, supply_centers, stores):
    # Access the 'inventory' from the 'data' field of the warehouse
    total_supply = warehouse['data']['inventory']
    num_centers = len(supply_centers)
    
    if num_centers > 0:
        even_distribution = total_supply // num_centers
        for center in supply_centers:
            # Distribute inventory to each supply center
            center['data']['inventory'] += even_distribution
            warehouse['data']['inventory'] -= even_distribution
            
            # Update the supply center's label to reflect new inventory and revenue
            center['data']['label'] = f"Supply Center {center['data']['id']} ({center['data']['inventory']} units, ${center['data']['revenue']})"
    
    # Now, update the store labels similarly
    for store in stores:
        # Update the store's label to show both inventory and revenue
        store['data']['label'] = f"{store['data']['id']} ({store['data']['inventory']} units, ${store['data']['revenue']})"
    
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
