import uuid 
import csv 

csv_file = 'testdummy.csv'

with open(csv_file, newline='') as file:
    reader= csv.reader(file)

    for row_number, row in enumerate(reader, start=1):
        transaction_id = uuid.uid4()
        transaction_date = row[0] #timestamp
        location_name = row[1]
        total_cost = row[4]

    

    print(f'Row {row_number}')
    print (f'ID: {transaction_id}')
    print (f'Date: {transaction_date}')
