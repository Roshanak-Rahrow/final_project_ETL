# Import the CSV module to help read .csv files
import csv

# This is the name of the CSV file we're reading from
# Make sure the file is saved in the same folder as this Python file
csv_file = 'Testdummy.csv'

# Print a message so we know which file we're using
print(f"\n Reading from: {csv_file}")

def read_csv_file():
    # Opens the file then reads row by row
    with open(csv_file, newline='') as file:
        # creating the reader
        reader = csv.reader(file)
    
        list_csv = list(reader)
    
    # Removes sensitive data
    for row in list_csv:
        row.pop(2)
        row.pop(-1)
    
    # return the depersonalised data
    return list_csv