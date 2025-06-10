from read_csv import list_csv
from utilities import get_connection

#LOAD FROM DATABASE 
def load_list():
     try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("SELECT * FROM transaction")
        return cur.fetchall()
     except Exception as e:
         print("Error loading transactions")
         return []
     finally: 
        cur.close()
        conn.close()
     

# copy data from csv_list relevent to transactions and reorder the items to work with our SQL command
new_transactions = list_csv.copy()

for row in new_transactions:
    row.pop(2)

fixed_transactions = []
for row in new_transactions:
    fixed_transactions.append([row[0], row[2], row[3], row[1]])

# connecting to the database and running an inserted sql code string
def insert_transaction(insert_string, data_to_insert):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(insert_string, data_to_insert)
    conn.commit()
    cur.close()
    conn.close()

# looping through the reordered transactions list to run INSERT sql commands on each transaction
for transaction in fixed_transactions:
    insert_transaction("""INSERT INTO transactions (transaction_date, location_id, total_cost, payment_type) 
    SELECT to_timestamp(%s, 'DD/MM/YYYY HH24:MI'), location_id, %s, %s 
    FROM location 
    WHERE location_name = %s;""", transaction)

