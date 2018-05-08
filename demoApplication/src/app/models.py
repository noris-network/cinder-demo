from app.config import db as database
from tiny.peewee import (Model, CharField, BlobField, TextField,
                         DateTimeField, BooleanField)


class BaseModel(Model):
    class Meta:
        database = database


class User(BaseModel):
    name = CharField(unique=True)  # adding unique true creates an index
    email = CharField(255)
    password = BlobField(255)
    
    def __str__(self):
        return "%s|%s" % (self.name, self.email)

    def __repr__(self):
        return "<%s|%s>" % (self.name, self.email)


def _init_db():
    with database:
        database.create_tables([User])


def _add_user(name, email, password):
    user = User(name=name, email=email, password=password)
    user.save()
