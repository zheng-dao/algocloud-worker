#!/usr/bin/python
import time

def save_algo(cur, stats):
    if stats is None:
        return
    insert_dict(cur, 'algoHistory', stats)


def save_assets(cur, assets):
    if assets is None:
        return
    for asset in assets:
        insert_dict(cur, "algoAssetHistory", asset)


def save_pools(cur, pools):
    if pools is None:
        return
    for pool in pools:
        insert_dict(cur, "algoPoolHistory", pool)

def save_last_time(cur):
    statement = "insert into \"updateHistory\" (\"updatedTime\") values ('{currentTime}');".format(currentTime=int(time.time()))
    cur.execute(statement)


def insert_dict(cur, table_name, my_dict):
    placeholder = ", ".join(["%s"] * len(my_dict))
    columns = ', '.join(f'"{column}"' for column in my_dict.keys())
    statement = "insert into \"{table}\" ({columns}) values ({values});"\
        .format(table=table_name,
                columns=columns,
                values=placeholder)
    cur.execute(statement, list(my_dict.values()))
