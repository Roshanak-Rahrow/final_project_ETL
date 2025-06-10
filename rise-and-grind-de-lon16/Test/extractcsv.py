# Import the CSV module to help read .csv files
import csv

# These are the names of the columns in the CSV file
# We're listing them manually because the file doesn't include headers
columns = [
    'timestamp',         # The date and time of the transaction
    'branch',            # The name of the cafe branch
    'customer_name',     # The customer's full name
    'product_list',      # A list of items purchased
    'total',             # The total amount spent on that transaction
    'payment_method',    # How they paid
    'card_number'        # The customer's card number
]

# This is the name of the CSV file we're reading from
# Make sure the file is saved in the same folder as this Python file
csv_file = 'testdummy.csv'

# Print a message so we know which file we're using
print(f"\n Reading from: {csv_file}")

# Openss the file then reads row by row
with open(csv_file, newline='') as file:
    # creating the reader
    reader = csv.reader(file)

    # We're now going to go through each row in the file
    # 'enumerate' gives us both the row number and the row itself
    for row_number, row in enumerate(reader, start=1):
        # Print the row number so it's easy to keep track
        print(f"\nRow {row_number}")

        # 'zip' lets us match each column name with the actual value from that row
        for column_name, value in zip(columns, row):
            # Show each column and its values
            print(f"{column_name}: {value}")
