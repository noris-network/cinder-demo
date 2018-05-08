#!/usr/bin/env python3
import os

from argparse import ArgumentParser
from tiny import bottle

cli = ArgumentParser()
subparsers = cli.add_subparsers(dest="subcommand")


def argument(*name_or_flags, **kwargs):
    """Convenience function to properly format arguments to pass to the
    subcommand decorator.
    """
    return ([*name_or_flags], kwargs)


def subcommand(args=[], parent=subparsers):
    """Decorator to define a new subcommand in a sanity-preserving way.
    The function will be stored in the ``func`` variable when the parser
    parses arguments so that it can be called directly like so::
        args = cli.parse_args()
        args.func(args)
    Usage example::
        @subcommand([argument("-d", help="Enable debug mode", action="store_true")])
        def subcommand(args):
            print(args)
    Then on the command line::
        $ python cli.py subcommand -d
    """
    def decorator(func):
        parser = parent.add_parser(func.__name__, description=func.__doc__)
        for arg in args:
            parser.add_argument(*arg[0], **arg[1])
        parser.set_defaults(func=func)
    return decorator


@subcommand([argument("-r", "--reload", action="store_true",
                      help="enable reloader"),
             argument("-d", "--debug", action="store_true",
                      help="enable degugger"),
             argument('-H', help="host to bind", default="127.0.0.1", dest="host"),
             argument("-p", "--port",  type=int, default='8080')])
def serve(args):
    """
    run local development server

    To run with gunicorn GUNICORN_CMD_ARGS="--bind=127.0.0.1:8080 --workers=3"
    """
    from app.views import app as home_app
    print(home_app.plugins)
    main_app = bottle.Bottle()

    main_app.mount("/", home_app)
    print("DEBUG %s:" % main_app.routes)
    bottle.debug(args.debug)
    bottle.run(main_app, host=args.host,
               port=args.port, reloader=args.reload)


@subcommand([argument("name", type=str), argument("email", type=str),
             argument("password", type=str)])
def adduser(args):
    from app.models import _add_user
    _add_user(args.name, args.email, args.password)


@subcommand()
def initdb(args):
    from app.models import _init_db
    _init_db()


@subcommand([argument("--ipython", action='store_true',
                      help='starts IPython with modules loaded')])
def dbshell(args):
    from app.models import User # noqa
    if args.ipython:
        try:
            from IPython import embed
            embed()
        except ImportError:
            print("You need to install IPython")
            sys.exit(1)
    else:
        import readline
        from rlcompleter import Completer
        readline.parse_and_bind("tab: complete")
        import code
        variables = globals().copy()
        variables.update(locals())
        readline.set_completer(Completer(variables).complete)
        shell = code.InteractiveConsole(variables)
        shell.interact()


args = cli.parse_args()
if args.subcommand is None:
    cli.print_help()
else:
    args.func(args)
