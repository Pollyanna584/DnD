import pandas as pd
import random
import os

# Adjust these variables for testing and customization
pet_percentage_range = (1, 5)
magic_item_percentage_range = (10, 20)
consumable_percentage_range = (75, 85)
price_adjustment_range = (-5, 5)  # Price adjustment in percentage
num_items_in_shop_low_percent = 5  # Lowest percentage for number of random items in the shop
num_items_in_shop_high_percent = 15  # Highest percentage for number of random items in the shop

def format_price(price):
    if pd.notna(price):
        price_in_copper = price
        if price_in_copper is not None:
            platinum = int(price_in_copper // 1000)
            gold = int((price_in_copper % 1000) // 100)
            silver = int((price_in_copper % 100) // 10)
            copper = int(round(price_in_copper % 10))  # Round to nearest digit before converting to integer

            # Add non-zero currency amounts to the list
            price_list = []
            if platinum != 0:
                price_list.append(f"{platinum} platinum")
            if gold != 0:
                price_list.append(f"{gold} gold")
            if silver != 0:
                price_list.append(f"{silver} silver")
            if copper != 0:
                price_list.append(f"{copper} copper")

            # Join the list elements with commas
            formatted_price = ', '.join(price_list)

            return formatted_price

    return "Price not available"

def adjust_prices(df_items, price_adjustment_range):
    df_items['Adjusted Price'] = df_items.loc[df_items['Price'].notna(), 'Price'].apply(lambda price: apply_adjustment(price, price_adjustment_range))
    return df_items

def apply_adjustment(price, price_adjustment_range):
    if price is None:
        return None
    price_adjustment = random.uniform(*price_adjustment_range)
    adjusted_price = price * (1 + price_adjustment / 100)
    return adjusted_price

def generate_general_store(df_summons_pets, df_magical, df_consumables, pet_percentage_range, magic_percent_range, consumable_percentage_range, price_adjustment_range, num_items_in_shop_low_percent, num_items_in_shop_high_percent):
    total_items = len(df_summons_pets) + len(df_magical) + len(df_consumables)

    # Calculate the number of items for each category based on percentage ranges
    pet_percent = random.randint(*pet_percentage_range)
    magic_percent = random.randint(*magic_item_percentage_range)
    consumable_percent = random.randint(*consumable_percentage_range)

    num_pet_items = round((pet_percent / 100) * total_items)
    num_magic_items = round((magic_percent / 100) * total_items)
    num_consumables = round((consumable_percent / 100) * total_items)

    # Filter pets by rarity and calculated percentage
    rarity_distribution = [num_pet_items // 5] * 5
    remainder = num_pet_items % 5
    for i in range(remainder):
        rarity_distribution[i] += 1

    pet_items = []
    for rarity, count in zip(['Common', 'Uncommon', 'Rare', 'Very Rare', 'Legendary'], rarity_distribution):
        items_of_rarity = df_summons_pets[df_summons_pets['Rarity'] == rarity]
        if not items_of_rarity.empty:
            sampled_items = items_of_rarity.sample(count, replace=True)
            pet_items.extend(sampled_items)

    # Concatenate pets and consumable items into one DataFrame
    df_pet_consumables = pd.concat([pd.DataFrame(pet_items), df_consumables])

    # Combine pets, magical, and consumable items into one DataFrame
    all_items = pd.concat([df_pet_consumables, df_magical])

    # Generate the store inventory with random price adjustments
    num_items_in_shop = round(random.uniform(num_items_in_shop_low_percent, num_items_in_shop_high_percent) / 100 * total_items)
    store_inventory = random.sample(list(all_items[['Name', 'Adjusted Price']].itertuples(index=False, name=None)), num_items_in_shop)

    for idx, item in enumerate(store_inventory, 1):
        name, price = item
        formatted_price = format_price(price)
        store_inventory[idx - 1] = (name, formatted_price)

    return store_inventory

# Load the CSV data into DataFrames (replace filenames accordingly)
data_dir = os.path.dirname(os.path.realpath(__file__))
df_magical = pd.read_csv(f'{data_dir}/Items/magic_items.csv')
df_summons_pets = pd.read_csv(f'{data_dir}/Items/summons_pets.csv') 
df_consumables = pd.read_csv(f'{data_dir}/Items/consumable_items.csv')

# Convert 'Price' column to numeric, coerce errors to convert non-numeric values to NaN
df_magical['Price'] = pd.to_numeric(df_magical['Price'], errors='coerce')
df_summons_pets['Price'] = pd.to_numeric(df_summons_pets['Price'], errors='coerce')
df_consumables['Price'] = pd.to_numeric(df_consumables['Price'], errors='coerce')

# Adjust the prices of each DataFrame
df_magical = adjust_prices(df_magical, price_adjustment_range)
df_summons_pets = adjust_prices(df_summons_pets, price_adjustment_range)
df_consumables = adjust_prices(df_consumables, price_adjustment_range)

# Generate and print the store inventory
store_inventory = generate_general_store(df_summons_pets, df_magical, df_consumables, pet_percentage_range, magic_item_percentage_range, consumable_percentage_range, price_adjustment_range, num_items_in_shop_low_percent, num_items_in_shop_high_percent)

print("Generated Store Inventory:")
for idx, item in enumerate(store_inventory, 1):
    name, price = item
    print(f"{idx}. {name} - Price: {price}")