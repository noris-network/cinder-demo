"""
This is based on the code from Indra Gunawan originally licensed under MIT.
"""

import inspect

import tiny.peewee as pw

from tiny import bottle


class PeeweePlugin:
    ''' This plugin passes an Peewee database handle to route callbacks
    that accept a `db` keyword argument. If a callback does not expect
    such a parameter, no connection is made. You can override the database
    settings on a per-route basis. '''

    name = 'peewee'
    api = 2

    def __init__(self, db, keyword='db'):
        self.db = db
        self.keyword = keyword

    def setup(self, app):
        ''' Make sure that other installed plugins don't affect the same
            keyword argument.'''
        for other in app.plugins:
            if not isinstance(other, PeeweePlugin):
                continue
            if other.keyword == self.keyword:
                raise bottle.PluginError(
                    "Found another peewee plugin with "
                    "conflicting settings (non-unique keyword).")

    def apply(self, callback, context):
        # Override global configuration with route-specific values.

        conf = context.config
        db = conf.get('db', self.db)
        keyword = conf.get('keyword', self.keyword)

        # Test if the original callback accepts a 'db' keyword.
        # Ignore it if it does not need a database handle.
        # args = inspect.getargspec(context['callback'])[0]
        args = inspect.getargspec(context.callback)[0]
        if keyword not in args:
            return callback

        def wrapper(*args, **kwargs):
            # Connect to the database
            try:
                db.connect()
            except pw.OperationalError:
                # the db is already open
                pass

            # Add the connection handle as a keyword argument.
            kwargs[keyword] = db

            try:
                rv = callback(*args, **kwargs)
            except pw.PeeweeException as e:
                db.rollback()
                raise
            finally:
                db.close()
            return rv

        # Replace the route callback with the wrapped one.
        return wrapper
