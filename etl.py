import configparser
import psycopg2
from sql_queries import copy_table_queries
from sql_queries import insert_table_queries


def load_staging_tables(cur, conn):
    for query in copy_table_queries:
        print(query)
        cur.execute(query)
        conn.commit()


def insert_tables(cur, conn):
    for query in insert_table_queries:
        print('Executing insert statement:')
        print(query)
        print('***************************')
        cur.execute(query)
        conn.commit()


def main():
    """
    This module loads the data from S3 into the staging tables, then executes the insert tables statements to load data ino the fact and dimension tables.
    """
    config = configparser.ConfigParser()
    config.read('dwh.cfg')

    conn = psycopg2.connect("host={} dbname={} user={} password={} port={}".format(*config['CLUSTER'].values()))
    cur = conn.cursor()

    load_staging_tables(cur, conn)
    insert_tables(cur, conn)

    conn.close()


if __name__ == "__main__":
    main()