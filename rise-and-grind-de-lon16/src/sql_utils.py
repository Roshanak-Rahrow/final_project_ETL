# This file exists to separate the direct use of psycopg2 in 'connect_to_db.py'
# from functions here that only care about the Connection and Cursor - this makes these easier to unit test.

import logging

LOGGER = logging.getLogger()
LOGGER.setLevel(logging.INFO)


def create_db_tables(connection, cursor):
    LOGGER.info('create_db_tables: started')
    try:

        LOGGER.info('create_db_tables: creating tables')
        cursor.execute(
            '''
            CREATE TABLE IF NOT EXISTS locations(
                location_id VARCHAR(255) PRIMARY KEY,
                location_name VARCHAR(255) UNIQUE NOT NULL
            );

            CREATE TABLE IF NOT EXISTS transactions(
                transaction_id VARCHAR(255) PRIMARY KEY,
                transaction_date TIMESTAMP NOT NULL,
                location_id VARCHAR(255) REFERENCES locations(location_id) NOT NULL,
                total_cost DECIMAL(8,2) NOT NULL,
                payment_type VARCHAR(255) NOT NULL
            );

            CREATE TABLE IF NOT EXISTS products(
                product_id VARCHAR(255) PRIMARY KEY,
                product_name VARCHAR(255) NOT NULL,
                product_flavour VARCHAR(255),
                product_size VARCHAR(255),
                product_price DECIMAL(8,2) NOT NULL
            );

            CREATE TABLE IF NOT EXISTS order_items(
                item_id VARCHAR(255) PRIMARY KEY, 
                transaction_id VARCHAR(255) REFERENCES transactions(transaction_id) NOT NULL,
                product_id VARCHAR(255) REFERENCES products(product_id) NOT NULL
            );
            '''
        )

        LOGGER.info('create_db_tables: committing')
        connection.commit()

        LOGGER.info('create_db_tables: done')
    except Exception as ex:
        LOGGER.info(f'create_db_tables: failed to run sql: {ex}')
        raise ex

#note on bucket_name
def save_data_in_db(connection, cursor, bucket_name, file_path, table_name, data):
    LOGGER.info(f'save_data_in_db: started: file_path={file_path}, rowS={len(data)}')

    try:

        if not data:
            return
    
        columns = ', '.join(data[0].keys())
        sql_insert_template = f'INSERT INTO {table_name} ({columns}) VALUES '
        # sql_insert_template = f'INSERT INTO {table_name} ({','.join(columns)}) VALUES ' [OPTION]

        # do len(data[0] + 1) to get length including visit_id for (%s, ?s ...)
        values_placeholder = ', '.join(['%s'] * len(data[0]))
        # values_placeholder = ', '.join(['%s'] * (len(columns) [OPTION]

        LOGGER.info(
            f'save_data_in_db: columns={columns}, sql_insert_template={sql_insert_template}, values_placeholder={values_placeholder}'
        )

        if table_name == 'locations': 
            for row in data:
                location_id = row ['location_id']
                cursor.excute(f"SELECT COUNT (*) FROM locations  WHERE  location_id = %s", (location_id,))
        else:
            for row in data:
                values= list(row.values())
                
                insert_sql = sql_insert_template + f'({values_placeholder})'
                cursor.execute(insert_sql, values)
        connection.commit()
        
    except Exception as ex:
        raise ex


''' for row in data:
            values = list(row.values())
            # values = [row[col] for col in columns] [OPTION]
            cursor.execute(sql_insert_template + f'({values_placeholder})', values)

        connection.commit()
        LOGGER.info(f'save_data_in_db: done: file_path={file_path}, rows={len(data)}')
    except Exception as ex:
        LOGGER.info(f'save_data_in_db: error: ex={ex}, file_path={file_path}')
        raise ex '''

def save_data_in_db_location(connection, cursor, bucket_name, file_path, table_name, data):
    LOGGER.info(f'save_data_in_db: started: file_path={file_path}, rowS={len(data)}')

    try:
        columns = ', '.join(data[0].keys())
        # coloumns = list(data[0].keys()) [OPTION]
        # sql_insert_template = f'INSERT INTO {table_name} ({','.join(columns)}) VALUES ' [OPTION]

        # do len(data[0] + 1) to get length including visit_id for (%s, ?s ...)
        values_placeholder = ', '.join(['%s'] * len(data[0]))
        # values_placeholder = ', '.join(['%s'] * (len(columns) [OPTION]

        sql_insert_template = f"""INSERT INTO {table_name} ({columns}) 
                                SELECT {values_placeholder} 
                                WHERE NOT EXISTS (
                                    SELECT 1 FROM {table_name} WHERE location_id = %s
                                );
                                """
        LOGGER.info(
            f'save_data_in_db: columns={columns}, sql_insert_template={sql_insert_template}, values_placeholder={values_placeholder}'
        )

        for row in data:
            values = list(row.values())
            # values = [row[col] for col in columns] [OPTION]
            values.append(row['location_id'])
            cursor.execute(sql_insert_template, values)

        connection.commit()
        LOGGER.info(f'save_data_in_db: done: file_path={file_path}, rows={len(data)}')
    except Exception as ex:
        LOGGER.info(f'save_data_in_db: error: ex={ex}, file_path={file_path}')
        raise ex

def save_data_in_db_products(connection, cursor, bucket_name, file_path, table_name, data):
    LOGGER.info(f'save_data_in_db: started: file_path={file_path}, rowS={len(data)}')

    try:
        columns = ', '.join(data[0].keys())
        # coloumns = list(data[0].keys()) [OPTION]
        # sql_insert_template = f'INSERT INTO {table_name} ({','.join(columns)}) VALUES ' [OPTION]

        # do len(data[0] + 1) to get length including visit_id for (%s, ?s ...)
        values_placeholder = ', '.join(['%s'] * len(data[0]))
        # values_placeholder = ', '.join(['%s'] * (len(columns) [OPTION]

        sql_insert_template = f"""INSERT INTO {table_name} ({columns}) 
                                SELECT {values_placeholder} 
                                WHERE NOT EXISTS (
                                    SELECT 1 FROM {table_name} WHERE product_id = %s
                                );
                                """
        LOGGER.info(
            f'save_data_in_db: columns={columns}, sql_insert_template={sql_insert_template}, values_placeholder={values_placeholder}'
        )

        for row in data:
            values = list(row.values())
            # values = [row[col] for col in columns] [OPTION]
            values.append(row['product_id'])
            cursor.execute(sql_insert_template, values)

        connection.commit()
        LOGGER.info(f'save_data_in_db: done: file_path={file_path}, rows={len(data)}')
    except Exception as ex:
        LOGGER.info(f'save_data_in_db: error: ex={ex}, file_path={file_path}')
        raise ex

def load_locations(connection, cursor):
    LOGGER.info(f'load_locations: started:')
    try:
        cursor.execute("SELECT location_id,location_name FROM locations;")
        locations = cursor.fetchall()
        connection.commit()
        LOGGER.info(f'load_locations: done')
        return locations
    except Exception as ex:
        LOGGER.info(f'load_locations: error: ex={ex}')
        raise ex

def load_products(connection, cursor):
    LOGGER.info(f'load_locations: started:')
    try:
        cursor.execute("SELECT product_name,product_flavour,product_size,product_id FROM products;")
        locations = cursor.fetchall()
        connection.commit()
        LOGGER.info(f'load_products: done')
        return locations
    except Exception as ex:
        LOGGER.info(f'load_products: error: ex={ex}')
        raise ex