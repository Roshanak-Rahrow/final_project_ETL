02.04.2025
**Setup script file to create network of container**
    - docker-compose.yml created with credentials of postgres and adminer
    - docker pull docker.io/postgres
    - docker pul docker.io/adminer
    - docker-compose up -d
    - set up env file with credentials
        POSTGRES_HOST=
        POSTGRES_USER=
        POSTGRES_DB=
        POSTGRES_PASSWORD=
    - http://localhost:8080/ to check

**Extract data from CSV file**
    - Sample CSV (Fromm a full CSV file from a coffee branch)
    - Cut-down to a test version.. CSV file with around 6 rows of data
    - Get a Python Script that can open and read CSV file
    - Making sure the rows and columns are split correctly
    - The data makes sense (readable) and it works (printed correctly by python) (At this stage the dummy data does not need to be privatised)

**Design schema to model data**
    - Create a schema for
        locations:
            - location_id uuid
            - Name
        products
            - product_id uuid
            - Name
            - price
        transactions
            - transaction_id uuid
            - transaction_date_time
            - location_id uuid
            - total price
            - payment_type
        order_items
            - item_id uuid
            - transaction_id
            - product uuid

ISSUES:
        Saw requirements needed a GUID for each of the tables (UUID)
        Had to read online about how to implement found a few solutions and decided to test them in 'TestSQL'
        writing python script to test the dummy CSV
        should produce transaction id for the CSV file to test if the uuid works. see TestSQL.py

ISSUES:
        sql initallise is not letting docker start the postgres sql container
        WORKING

    Websites used for uuid:
        https://www.uuidgenerator.net/dev-corner/python
        import uuid my_uuid = uuid.uuid4()
        CREATE TABLE IF NOT EXISTS
        https://neon.tech/postgresql/postgresql-tutorial/postgresql-uuid
        https://neon.tech/docs/data-types/uuid
        https://www.postgresql.org/docs/current/functions-uuid.html
        https://www.postgresql.org/docs/current/uuid-ossp.html

10/04/25

* work on ticket created 'Single sting values'
* Added acceptace critea for stickets
* Preparing data for the products table
* sepeate sting of multiple purchesed items
* testing for implimenting data shcema

**Transform - Normalise data to match your schema**
Location table:
    * from read_csv.py to import the testdummy.csv with few datasets from each location
    * created an empty list for locations and a for loop to add any new locations into the list for row 1 (location_name)
    * fetching the database connection (load_dotevn())
    * created a function to insert the correct information into database (INSERT INTO) access and execute connection.cursor
    * return contents in database and fetch everything to print as a list
    * for loop to write locations in table

Transaction table:
    * import from read_csv, location and utilities#
    * load list from database and fetch all to return
    * removed products from data set
    * function to insert transaction into database
    * for loop iterates through item in transaction and inserts into database

Utilities.py:
    created for loading database and selecting to view for less coding and better readability

Difficulties faced:
    *We were trying write sql code that would automatically populate the location_id column of the transactions database based on the location string and location database. We found sql statements and functions that we could use to accomplish this but had to deal with constant errors as the data was attempting to be inserted into the wrong columns, to solve this we ultimately wrote code to reorder the sequence the data was in.
    *We also had to deal with the date format not being compatible with the postgreSQL timestamp format, for which I found the to_timestamp() function that will convert the data to an appropriate format as the data is sent to the SQL database.

>>>>>>> cc28067b2d16f14cbb541a6ecf6790af8fce5b0c
>>>>>>> 09.04.25
>>>>>>>
>>>>>>
>>>>>
>>>>
>>>
>>

**Transform - Remove sensitive data**
    - printing(list_csv) to see visual of list we are working with

    - made a branch to test extracting the data

    - Data extracted into lists

    - for loop to remove row 2 & and -1
        for row in list_csv
        row.pop(2)
        row.pop(-1)

10.04.25

**location.py**

* creating inital list
* added different location ata to test dummy,
* for loop if not in inital list and to add it
* print(initial list) to test
* connect to databas
* changed location table 'location_name' to unique

24.04.25

- After completing tickets #21 & #22 we needed to discus how we were going to intergrate our data to fit our testing
- We decided that we need to edit the ETL and focus on cleaning and transforming the data (how we would structure it, we need to create headers and a list of what our headers are to be able to remove data)
- We discussed what data we needed to remove and if we wanted to remove them completly or hid them depending on what metrics the product owner would like
- We decided that we wanted to ask the product owner exact metrics so we can complete our design after our break
- Planning by lunch to complete the code for refactoring ~ make a TO DO list for tasks
