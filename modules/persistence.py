import sys
import os
from enum import IntEnum
from pprint import pprint
from tinydb import TinyDB, Query


dirname = os.path.dirname(__file__)
DB_FILE = f"{dirname}/../data/db.json"
this = sys.modules[__name__]


def init():
    this.db = TinyDB(DB_FILE)

    '''
    {
        'server_id': 123456,
        'channel_id': 123456,
        'weekday': 0,
        'time': 15,
        'message': '...',
        'add_schedule': False
    }
    '''
    this.pings = this.db.table('pings')

    '''
    {
        
        'server_id': 123456,
        '<config_key>': <config_value>
    }
    '''
    this.config = this.db.table('config')


init()


# APIs
def create_ping(server_id, channel_id, weekday, hour, minute, msg, add_schedule):
    ping_id = this.pings.insert(
        {
            'server_id': server_id,
            'channel_id': channel_id,
            'weekday': int(weekday),
            'hour': int(hour),
            'minute': int(minute),
            'message': msg,
            'add_schedule': add_schedule
        }
    )
    print(
        f'Created a schedule check with id {ping_id} on {weekday} at {hour}:{minute} with the following message:'
        f'\n{msg}')
    db_dump()


def get_pings(is_schedule=None, server_id=None):
    if is_schedule is None and server_id is None:
        result = this.pings.all()
    else:
        queries = []
        if is_schedule is not None:
            queries.append((Query().add_schedule == is_schedule))
        if server_id is not None:
            queries.append((Query().server_id == server_id))
        full_query = None
        for query in queries:
            if full_query is None:
                full_query = query
            else:
                full_query = full_query & query
        result = this.pings.search(full_query)
    return result


def delete_ping(ping_id):
    try:
        this.pings.remove(doc_ids=[int(ping_id)])
        return True
    except Exception as e:
        print(e)
        return False


def set_config(server_id, config_key, config_value):
    this.config.upsert(
        {
            'server_id': server_id,
            config_key: config_value
        },
        Query().server_id == server_id
    )
    db_dump()


def get_config(server_id):
    return this.config.get(Query().server_id == server_id)


# Utils
def db_dump():
    pass
    # print('\nDb Dump:')
    # for inner_db in this.db.tables():
    #     print(f'Database [{inner_db}]:')
    #     pprint(this.db.table(inner_db).all())
    #     print('')