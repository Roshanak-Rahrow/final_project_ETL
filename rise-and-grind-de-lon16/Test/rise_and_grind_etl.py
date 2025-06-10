import csv
from datetime import datetime
import logging
from decimal import Decimal
import uuid

LOGGER = logging.getLogger()
LOGGER.setLevel(logging.INFO)

#Defining transaction columns (reminder:look into if location_id is needed)
DATAFIELDS = [
    'transaction_date',
    'location_name',
    'customer_name',
    'products',
    'total_cost',
    'payment_type',
    'card_number'
]

# Defining sensitive information fields to be removed in the transform step
SENSITIVEFIELDS = ['customer_name', 'card_number']

def extract(body_text):  
    LOGGER.info('extract: starting')
    reader = csv.DictReader(
        body_text,
        fieldnames=DATAFIELDS,
        delimiter=','
    )

    data = [row for row in reader]

    LOGGER.info(f'extract: done: rows={len(data)}')
    return data

#Removes sensitive data 
def remove_sensitive_information(data):
    LOGGER.info(f'remove_sensitive_information: processing rows={len(data)}')
    return [
        {k: v for k, v in item.items() if k not in SENSITIVEFIELDS} for item in data
    ]

#normalises datetime
def reformat_datetime(data):
    LOGGER.info('reformat_visit_date: starting')
    updated_data = []
    for item in data:
        updated_item = item.copy()
        input_format_string = '%d/%m/%Y %H:%M'
        dt = datetime.strptime(updated_item['transaction_date'], input_format_string)
        new_datetime = dt.strftime('%Y-%m-%d %H:%M')
        updated_item['transaction_date'] = new_datetime
        updated_data.append(updated_item)

    LOGGER.info(f'reformat_visit_date: done: rows={len(updated_data)}')
    return updated_data
    
def split_order(products):
    items = [] 
    product_size = ['Small', 'Regular', 'Large']
    
    for product in products.split(','): #split with commas
        product = product.strip() #removes white space
        parts = product.split('-') #split each item
        if len(parts) < 2:
            continue
        try: 
           product_name = parts[0].strip()
           product_flavour = parts[1].strip() if len(parts) == 3 else None #only if there are 3 parts 
           product_price = float(parts[-1].strip()) #-1 means last item in the list
        except (IndexError, ValueError):
            continue
        item = { #create dictionary
        'product_name' : product_name,
        'product_flavour': product_flavour,
        'product_price': product_price
        }

        for size in product_size:
            if item['product_name'].startswith(size): #to check if the product name starts with size
                item['product_size'] = size #store the info
                item['product_name'] = item['product_name'][len(size):].strip() #remove size from the name and remove white space
                break
        items.append(item)
    return items
    
#numbers are interperted by python as text strings not actual numbers they need to be converted into
#numeric types for total_cost and product_price in redshift
def convert_decimal(cost_str):
    if cost_str is None or not cost_str.strip():
      return None
    try:
        return Decimal(cost_str) #takes the import decimal object and create the decimal number
        
    except Exception as e:
        LOGGER.error(f"Cant convert cost string '{cost_str}' to Decimal: {e}")
        return None #catches an error when the conversion happens 

# create a uuid
def create_guid():
    return str(uuid.uuid4())
    
# prepare data for loading into our sql tables
def normalise_data(rows):
    locations = []
    location_lookup = {}
    transactions = []
    products = []
    order_items = []
    product_lookup = {}
    for row in rows:
        
        # locations - create a list of dictionaries of unique locations with corresponding uuids
        for location in locations:
            if location["location_name"] == row["location_name"]:
                break
        else:
            new_location = {"location_id":create_guid() ,
                            "location_name":row["location_name"]
                            }
            locations.append(new_location)
            location_lookup[row["location_name"]] = new_location["location_id"]
                
        # transactions - creates a list of dictionaries with key-value pairs corresponding to our database columns
        transaction_id = create_guid()

        formatted_date = datetime.strptime([row["transaction_date"]], '%d/%m/%Y %H:%M').strftime('%Y-%m-%d %H:%M')
        new_transaction = {"transaction_id":transaction_id, 
                           "transaction_date": formatted_date,
                           "location_id":location_lookup[row["location_name"]],
                           "total_cost":row["total_cost"],
                           "payment_type":row["payment_type"]
                           }
        transactions.append(new_transaction)

        items = split_order(row["products"])
        for item in items:
            # to avoid duplicates (if there are any)
            product_key = (item['product_name'], item.get('product_flavour'), item.get('product_size'))
            if product_key not in product_lookup:
                product_id = create_guid()
                product_lookup[product_key] = product_id
                products.append({
                    "product_id": product_id,
                    "product_name": item["product_name"],
                    "product_flavour": item.get("product_flavour"),
                    "product_size": item.get("product_size"),
                    "product_price": convert_decimal(str(item["product_price"]))if item.get("product_price") else None
                })
            else:
                product_id = product_lookup[product_key]

                #order items is inside the loop
                
            new_order_items = {
                "item_id": create_guid(),
                "transaction_id": transaction_id,
                "product_id": product_id
            }
            order_items.append(new_order_items)


    return locations, transactions, products, order_items

        

def transform(data):
    LOGGER.info('transform: starting')
    data = remove_sensitive_information(data)
    locations, transactions, products, order_items = normalise_data(data)
    
    LOGGER.info(f'transform: done')
    return locations, transactions, products, order_items
