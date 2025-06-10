from read_csv import list_csv
from utilities import get_connection
import psycopg2
from decimal import Decimal


#INSERT FUNCTION 
def insert_location(location_name):
    insert = """INSERT INTO location (location_name)
    VALUES (%s)
    ON CONFLICT (location_name) DO NOTHING;
    """
    try: 
        conn = get_connection()
        cur = conn.cursor()
        cur.execute(insert, (location_name,))
        conn.commit()
    except Exception as e: 
        print(f"Error inserting location '{location_name}': {e}")
        conn.rollback()
    finally:
        cur.close()
        conn.close()

# reorder the items to work with our SQL command
def reorder_transaction_data(original_row):
    row = original_row.copy()
    row.pop(2)

    fixed_transactions = []
    fixed_transactions.append([row[0], row[2], row[3], row[1]])

    return fixed_transactions[0]

# connecting to the database and running an inserted sql code string
def insert_transaction(insert_string, data_to_insert):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(insert_string, data_to_insert)
    transaction_id = cur.fetchone()[0]
    conn.commit()
    cur.close()
    conn.close()
    return transaction_id

def get_or_create_product_id(cursor, product_name, product_price):
    product_id = None
    try:
        sql_select = "SELECT product_id FROM products WHERE product_name = %s AND product_price = %s;"
        cursor.execute(sql_select, (product_name, product_price))
        result = cursor.fetchone()
        if result:
            product_id = result[0]
        else:
            sql_insert = "INSERT INTO products (product_name, product_price) VALUES (%s, %s) RETURNING product_id;"
            cursor.execute(sql_insert, (product_name, product_price))
            new_result = cursor.fetchone()
            if new_result:
                product_id = new_result[0]
        return product_id
    except psycopg2.Error as error:
        return None

def create_order_item(cursor, transaction_id, product_id):
    try:
        sql_insert = "INSERT INTO order_items (transaction_id, product_id) VALUES (%s, %s);"
        cursor.execute(sql_insert, (transaction_id, product_id,))
        return True
    except psycopg2.Error as error:
        return False
conn = None
cur = None

# run transformation functions on input data in a for loop
def transform_data(list_csv):
    for row in list_csv:
        insert_location(row[1])

        transaction_data = reorder_transaction_data(row)

        # looping through the reordered transactions list to run INSERT sql commands on each transaction
        transaction_id = insert_transaction("""INSERT INTO transactions (transaction_date, location_id, total_cost, payment_type) 
        SELECT to_timestamp(%s, 'DD/MM/YYYY HH24:MI'), location_id, %s, %s 
        FROM location 
        WHERE location_name = %s RETURNING transaction_id;""", transaction_data)

        try:
            conn = get_connection()

            if conn:
                cur = conn.cursor()

                product_list_string = row[2]
                individual_items = [item.strip() for item in product_list_string.split(',') if item.strip()]
                for item_description in individual_items:
                    try:
                        parts = item_description.rsplit('-', 1)

                        if len(parts) == 2:
                            product_name = parts[0].strip()
                            product_price = Decimal(parts[1].strip())

                            product_id = get_or_create_product_id(cur, product_name, product_price)
                            if product_id:
                                create_order_item(cur,transaction_id, product_id)

                    except ValueError as error:
                        continue
                    except Exception as general_item_error:
                        continue
                conn.commit()
            else:
                print("error")
        except psycopg2.Error as db_error:
            if conn:
                conn.rollback()
        except Exception as general_error:
            if conn:
                conn.rollback()
        finally:
            if cur:
                cur.close()
            if conn:
                conn.close()


