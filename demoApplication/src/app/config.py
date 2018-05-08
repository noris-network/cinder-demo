import os

from tiny.peewee import SqliteDatabase
from tiny.bottle_peewee import PeeweePlugin
from tiny import bottle

print(os.getenv("DATABASE_DIR"))
os.system("ls /app/vol")
db = SqliteDatabase(os.path.join(os.getenv("DATABASE_DIR", os.getcwd()), 'app.sqlite3'))

CONFIG = {'db': db}


app = bottle.Bottle()
app.install(PeeweePlugin(db))

app.config.update(CONFIG)
