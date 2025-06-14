import s3_utils, sql_utils, db_utils
import rise_and_grind_etl
import logging
import os

LOGGER = logging.getLogger()
LOGGER.setLevel(logging.INFO)

SSM_ENV_VAR_NAME = 'SSM_PARAMETER_NAME'


def lambda_handler(event, context):
    LOGGER.info('lambda_handler: starting')
    file_path = 'NOT_SET'  # makes the exception handler compile

    try:
        ssm_param_name = os.environ.get(SSM_ENV_VAR_NAME, 'NOT_SET')
        LOGGER.info(f'lambda_handler: ssm_param_name={ssm_param_name} from ssm_env_var_name={SSM_ENV_VAR_NAME}')

        bucket_name, file_path = s3_utils.get_file_info(event)

        csv_text = s3_utils.load_file(bucket_name, file_path)
        LOGGER.info(f"CSV content preview: {csv_text[:200]}")

        data = rise_and_grind_etl.extract(csv_text)
        LOGGER.info(f"Extracted rows count: {len(data)}")

        # One would not normally log the data directly!!
        # ...there could be loads and it could have PID in it!!
        LOGGER.warning(f'lambda_handler: transformed data')

        redshift_details = db_utils.get_ssm_param(ssm_param_name)
        conn, cur = db_utils.open_sql_database_connection_and_cursor(redshift_details)

        sql_utils.create_db_tables(conn, cur)

        initial_locations = sql_utils.load_locations(conn,cur) 
        initial_products = sql_utils.load_products(conn,cur)
        locations, transactions, products, order_items = rise_and_grind_etl.transform(data, initial_locations, initial_products)
        LOGGER.info(f"Transformed - Locations: {len(locations)}, transactions: {len(transactions)}, products: {len(products)}, order_items: {len(order_items)}")

        if locations != []:
            sql_utils.save_data_in_db_location(conn, cur, bucket_name, file_path, "locations", locations)
        sql_utils.save_data_in_db(conn, cur, bucket_name, file_path, "transactions", transactions)
        if products != []:
            sql_utils.save_data_in_db_products(conn, cur, bucket_name, file_path, "products", products)
        sql_utils.save_data_in_db(conn, cur, bucket_name, file_path, "order_items", order_items)
        cur.close()
        conn.close()

        LOGGER.info(f'lambda_handler: done, file={file_path}')

    except Exception as err:
        LOGGER.error(f'lambda_handler: failure: error={err}, file={file_path}')
        raise err
