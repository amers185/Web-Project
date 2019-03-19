'''
    psycopg2-test.py
    Jeff Ondich, 1 Oct 2013
    Modified by Amy Csizmar Dalal, 24 January 2018
    This is a short example of how to access a PostgreSQL database in Python.
'''

import psycopg2
import getpass

# Get the database login info. *** REPLACE THE DATABASE NAME AND USER WITH YOUR USERNAME ***
db = 'bremerw'
usr = 'bremerw'
pswd = getpass.getpass()

# Login to the database
try:
    connection = psycopg2.connect(database=db, user=usr, password=pswd)
except Exception as e:
    print('Connection error: ', e)
    exit()

# Query the database
try:
    cursor = connection.cursor()
    query = 'SELECT * FROM sightings WHERE latitude=0'
    cursor.execute(query)
    for row in cursor.fetchall():
        print(row)

    # An alternative to "for row in cursor.fetchall()" is "for row in cursor". The former
    # brings all the data into memory in your program, while the latter brings data in
    # small pieces (one row at a time, I think, but I haven't verified it yet).

except Exception as e:
    print('Cursor error', e)
    connection.close()
    exit()

connection.close()

