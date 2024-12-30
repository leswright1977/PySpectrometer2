import os
import sys
import time
import sqlite3
import argparse
import psycopg2
from dotenv import load_dotenv
from psycopg2.extras import execute_values

load_dotenv()

SQLITE3_DB = 'spectrometer_data.db'
DB_TYPE = os.getenv('DB_TYPE', 'sqlite3')

if DB_TYPE != 'sqlite3':
    DB_HOST = os.environ.get('DB_HOST', 'localhost')
    DB_PORT = os.environ.get('DB_PORT', '5432')
    DB_NAME = os.environ.get('DB_NAME', 'postgres')
    DB_USERNAME = os.environ.get('DB_USERNAME', 'postgres')
    DB_PASSWORD = os.environ.get('DB_PASSWORD', 'postgres')


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '-i', '--initialize', action='store_true', help='Initialize SQLite3 database',
    )
    parser.add_argument(
        '-t', '--test', action='store_true', help='Test SQLite3 database measurements insertion.',
    )
    return parser.parse_args()


def snapshot_database(timestamp, wavelengths, intensities):
    data_to_insert = prepare_snapshot_db_data(timestamp, wavelengths, intensities)

    if DB_TYPE == "postgresql":
        save_measurements_to_postgresql(
            '''
                    INSERT INTO measurements (timestamp, wavelength, intensity)
                    VALUES %s
                ''' % data_to_insert,
            data_to_insert,
        )
    else:
        save_measurements_to_sqlite3(
            '''INSERT INTO measurements (timestamp, wavelength, intensity) VALUES (?, ?, ?)''',
            data_to_insert,
        )


def prepare_snapshot_db_data(timestamp, wavelengths, intensities):
    return [(timestamp, wl, inten) for wl, inten in zip(wavelengths, intensities)]


def connect_to_sqlite3() -> sqlite3.Connection:
    return sqlite3.connect(SQLITE3_DB)


def connect_to_postgresql() -> psycopg2.connect:
    return psycopg2.connect(
        host=DB_HOST,
        database=DB_NAME,
        user=DB_USERNAME,
        password=DB_PASSWORD,
        port=DB_PORT,
    )


def save_measurements_to_sqlite3(query, data_to_insert):
    conn = connect_to_sqlite3()
    cursor = conn.cursor()
    cursor.executemany(query, data_to_insert)
    conn.commit()
    conn.close()


def save_measurements_to_postgresql(query, data_to_insert):
    conn = connect_to_postgresql()
    cursor = conn.cursor()
    execute_values(cursor, query, data_to_insert)
    conn.commit()
    cursor.close()
    conn.close()


def create_sqlite3_db():
    conn = connect_to_sqlite3()
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS measurements (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            wavelength REAL,
            intensity REAL
        )
    ''')

    conn.commit()
    conn.close()


if __name__ == '__main__':
    args = parse_arguments()
    if args.initialize:
        create_sqlite3_db()
    elif args.test:
        test_data = prepare_snapshot_db_data(
            time.strftime("%Y%m%d--%H%M%S"),  # <- timestamp
            [395.6, 396.1],  # <- wavelengths
            [2, 1]  # <- intensities
        )

        save_measurements_to_sqlite3(
            '''INSERT INTO measurements (timestamp, wavelength, intensity) VALUES (?, ?, ?)''',
            test_data,
        )

    sys.exit(0)
