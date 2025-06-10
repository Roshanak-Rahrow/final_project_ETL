from read_csv import list_csv
from utilities import get_connection

#GET LOCATION NAMES FROM CSV
new_location = list({row[1] for row in list_csv})

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

#INSERT UNIQUE LOCATIONS
for location in new_location:
    insert_location(location)

#LOAD FROM DATABASE
def load_locations():
        try:
            conn = get_connection()
            cur = conn.cursor()
            cur.execute("SELECT * FROM location")
            return cur.fetchall()
        except Exception as e:
            print("Error loading locations:", e)
            return []
        finally: 
            cur.close()
            conn.close()
            

