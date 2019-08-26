import sys
from enum import IntEnum
from pprint import pprint
from tinydb import TinyDB, Query

DB_FILE = 'data/db.json'
this = sys.modules[__name__]


def init():
    this.db = TinyDB(DB_FILE)

    '''
    {
        'pings': [
            {
                'server_id': '123456',
                'channel_id': '123456',
                'weekday': 0,
                'time': 15,
                'message': '...',
                'add_schedule': False
            }
        ]
    }
    '''
    this.pings = this.db.table('pings')

    '''
    {
        '<config_name>': <config_value>
    }
    '''
    this.config = this.db.table('config')


init()


class ConfigName(IntEnum):
    PINGS = 1


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
        f'\nCreated a schedule check with id {ping_id} on {weekday} at {hour}:{minute} with the following message:'
        f'\n{msg}')
    db_dump()


def get_pings():
    return this.pings.all()


def set_config(config_name, config_key, config_value):
    this.config.upsert(
        {
            'config_name': config_name,
            config_key: config_value
        },
        Query().config_name == ConfigName.PINGS
    )
    db_dump()


def get_config(config_name):
    return this.config.get(Query().config_name == config_name)


# Utils
def db_dump():
    print('\nDb Dump:')
    for inner_db in this.db.tables():
        print(f'Database [{inner_db}]:')
        pprint(this.db.table(inner_db).all())
        print('')
