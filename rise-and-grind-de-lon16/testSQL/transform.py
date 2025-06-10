import psycopg2
from decimal import Decimal
from utilities import get_connection
from read_csv import list_csv

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

def create_order_item(cursor, product_id):
    try:
        sql_insert = "INSERT INTO order_items (transaction_id, product_id) VALUES (NULL, %s);"
        cursor.execute(sql_insert, (product_id,))
        return True
    except psycopg2.Error as error:
        return False
conn = None
cur = None

try:
    conn = get_connection()

    if conn:
        cur = conn.cursor()

        data_rows = list_csv[1:] if list_csv and len(list_csv) > 0 else []
        for row_number, row in enumerate(data_rows, start=2):
            if not row or len(row) < 3:
                 continue
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
                            create_order_item(cur, product_id)

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