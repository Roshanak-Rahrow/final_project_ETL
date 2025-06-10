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
            CREATE TABLE location(
                location_id UUID PRIMARY KEY,
                location_name VARCHAR(30) UNIQUE NOT NULL
            );

            CREATE TABLE transactions(
                transaction_id UUID PRIMARY KEY,
                transaction_date TIMESTAMP NOT NULL,
                location_id UUID REFERENCES location(location_id) NOT NULL,
                total_cost DECIMAL(8,2) NOT NULL,
                payment_type VARCHAR(30) NOT NULL
            );

            CREATE TABLE products(
                product_id UUID PRIMARY KEY,
                product_name VARCHAR(30) NOT NULL,
                product_flavour VARCHAR(30) NOT NULL,
                product_size VARCHAR(30) NOT NULL,
                product_price DECIMAL(8,2) NOT NULL
            );

            CREATE TABLE order_items(
                item_id UUID PRIMARY KEY, 
                transaction_id UUID REFERENCES transactions(transaction_id) NOT NULL,
                product_id UUID REFERENCES products(product_id) NOT NULL
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
    LOGGER.info(f'save_data_in_db: started: file_path={file_path}, rows={len(data)}')

    try:
        columns = ', '.join(data[0].keys())
        sql_insert_template = f'INSERT INTO {table_name} ({columns}) VALUES '

        # do len(data[0] + 1) to get length including visit_id for (%s, ?s ...)
        values_placeholder = ', '.join(['%s'] * (len(data[0]) + 1))

        LOGGER.info(
            f'save_data_in_db: columns={columns}, sql_insert_template={sql_insert_template}, values_placeholder={values_placeholder}'
        )

        for row in data:
            values = list(row.values())

            cursor.execute(sql_insert_template + f'({values_placeholder})', values)

        connection.commit()

        LOGGER.info(f'save_data_in_db: done: file_path={file_path}, rows={len(data)}')
    except Exception as ex:
        LOGGER.info(f'save_data_in_db: error: ex={ex}, file_path={file_path}')
        raise ex
