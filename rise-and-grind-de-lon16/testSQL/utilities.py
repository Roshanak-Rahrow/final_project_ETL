import os 
import psycopg2
from dotenv import load_dotenv

load_dotenv()

# function for connecting to the postgreSQL database
def get_connection():
    try: 
        connection = psycopg2.connect(
            host = os.environ.get("POSTGRES_HOST"),
            dbname = os.environ.get("POSTGRES_DB"),
            user = os.environ.get("POSTGRES_USER"),
            password = os.environ.get("POSTGRES_PASSWORD"),
            port=os.environ.get("POSTGRES_PORT", "5432")
        )
        return connection
    except psycopg2.Error as e:
        print(f"Error connecting: {e}")
        return None
