from tinydb import TinyDB

DB_FILE = 'db.json'
this = sys.modules[__name__]


def init():
    this.db = TinyDB(DB_FILE)


init()


# APIs
