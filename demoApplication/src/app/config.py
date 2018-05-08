import os

from tiny.peewee import SqliteDatabase
from tiny.bottle_peewee import PeeweePlugin
from tiny import bottle


db = SqliteDatabase(os.path.join(os.getenv("DATABASE_DIR", os.getcwd()), 'app.sqlite3'))
import pdb; pdb.set_trace()
print(db)
CONFIG = {'db': db}


app = bottle.Bottle()
app.install(PeeweePlugin(db))

app.config.update(CONFIG)
