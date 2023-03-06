#!/usr/bin/python
import os
import psycopg2
from config import config
from tinyman import fetch_assets, fetch_pools, fetch_algo_stats
from database import save_assets, save_pools, save_algo, save_last_time

print("Fetching assets......")


def connect():
    conn = None
    try:
        config_file = os.getenv('DATABASE_INI') or 'production.ini'
        db_params = config(config_file)

        conn = psycopg2.connect(**db_params)

        cur = conn.cursor()

        stats = fetch_algo_stats()
        save_algo(cur, stats)

        [pools, asset_dict] = fetch_pools()
        save_pools(cur, pools)

        assets = fetch_assets(asset_dict)
        save_assets(cur, assets)

        save_last_time(cur)

        conn.commit()
        cur.close()
    except (Exception, psycopg2.DatabaseError) as error:
        print("Error occurred")
        print(error)
    finally:
        if conn is not None:
            conn.close()


if __name__ == '__main__':
    connect()
