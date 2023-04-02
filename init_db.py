import os
import psycopg2


def create_table():
    conn = psycopg2.connect(
        host="localhost",
        database="movies_db",
        user='postgres',
        password='new_password')

    # Open a cursor to perform database operations
    cur = conn.cursor()

    # Execute a command: this creates a new table
    cur.execute('DROP TABLE IF EXISTS movies;')
    cur.execute(
        '''
        CREATE TABLE movies (name VARCHAR (150) NOT NULL,
                genre VARCHAR (150) NOT NULL,
                director VARCHAR (100) NOT NULL,
                released DATE NOT NULL,
                synopsis TEXT,
                rating NUMERIC(2,1),
                poster BYTEA,
                posted_by VARCHAR (150) NOT NULL)
                ''')
    conn.commit()

    cur.close()
    conn.close()


# Insert data into the table

#cur.execute('INSERT INTO movies ('name, genre, director, released, synopsis, rating, posted_by)'
#
# cur.execute('INSERT INTO books (title, author, pages_num, review)'
#             'VALUES (%s, %s, %s, %s)',
#             ('Anna Karenina',
#              'Leo Tolstoy',
#              864,
#              'Another great classic!')
#             )
#

