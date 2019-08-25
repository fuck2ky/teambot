import sys
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
                'message': '...'
            }
        ]
    }
    '''
    this.pings = this.db.table('pings')


init()


# APIs
def create_ping(server_id, channel_id, weekday, time, msg):
    id = pings.insert(
        {
            'server_id': server_id,
            'channel_id': channel_id,
            'weekday': weekday,
            'time': time,
            'message': msg
        }
    )
    print(
        f'\nCreated a schedule check with id {id} on {weekday} at {time}:00 with the following message: \n{msg}')
    db_dump()


# Utils
def db_dump():
    print('Db Dump:')
    for srv in db.tables():
        print(f'Database [{srv}]:')
        pprint(db.table(srv).all())
