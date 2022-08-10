from django.core.management.base import BaseCommand
import csv
import logging
import pandas as pd
import sqlite3

class Command(BaseCommand):
    help = 'Process the NAP 5 Commitments files for loading into Solr'
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)
    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)
    logger.addHandler(ch)

    def add_arguments(self, parser):
        parser.add_argument('--csv', type=str, help='The CSV file to be processed', required=True)
        parser.add_argument('--out', type=str, help='The porcessed CSV file', required=True)

    def handle(self, *args, **options):

        # Set up a temp Sqlite3 db to hold the content
        conn = sqlite3.connect("temp_db.sqlite3")
        cur = conn.cursor()
        cur.execute("pragma max_page_count = 2147483646")
        cur.execute("VACUUM")
        cur.execute("PRAGMA synchronous = FULL")
        cur.execute("PRAGMA journal_mode = DELETE")

    # Process the records in the CSV file one at a time
        cur.execute(f'DROP TABLE IF EXISTS nap5')
        cur.execute(f'DROP TABLE IF EXISTS latest')
        cur.execute('create table latest(indicators NVARCHAR, reporting_period NVARCHAR)')
        try:
            for chunk in pd.read_csv(options['csv'], chunksize=500, delimiter=","):
                chunk.columns = chunk.columns.str.replace(' ', '_')  # replacing spaces with underscores for column names
                chunk.to_sql(name="nap5", con=conn, if_exists='append')

            cur.execute("insert into latest select indicators, max(reporting_period) from nap5 group by indicators")
            cur.execute("commit")

            cur.execute("select n.*, l.reporting_period from nap5 n join latest l on n.indicators = l.indicators")
            nap_data = cur.fetchall()
            for row in nap_data:
                print(row)

        except Exception as e:
            self.logger.critical(f'Error processing')
            self.logger.error(e)

        finally:
            cur.execute('VACUUM')
            conn.close()
