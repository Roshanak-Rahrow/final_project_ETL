import s3_utils
import read_csv
import transfrom_load
import logging
import os

LOGGER = logging.getLogger()
LOGGER.setLevel(logging.INFO)


def lambda_handler(event, context):
    LOGGER.info('lambda_handler: starting')
    file_path = 'NOT_SET'  # makes the exception handler compile

    try:
        bucket_name, file_path = s3_utils.get_file_info(event)

        csv_text = s3_utils.load_file(bucket_name, file_path)

        data = read_csv.read_csv_file(csv_text)

        transformed_data = transfrom_load.transform(data)
        # One would not normally log the data directly!!
        # ...there could be loads and it could have PID in it!!
        LOGGER.warn(f'lambda_handler: transformed_data={transformed_data}')

        LOGGER.info(f'lambda_handler: done, file={file_path}')

    except Exception as err:
        LOGGER.error(f'lambda_handler: failure: error={err}, file={file_path}')
        raise err