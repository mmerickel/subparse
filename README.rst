========
subparse
========

A wrapper for argparse that provides decorator-based subcommand support.

Commands can be defined separately from their actual main functions,
enabling faster import times.

Basic Usage
===========

::

    from subparse import CLI

    class MyApp(object):
        def __init__(self, args):
            self.args = args

        def info(self, *msg):
            if not self.args.quiet:
                print('[info]', *msg)

    def app_factory(cli, args):
        return MyApp(args)

    cli = CLI(version='0.0', context_factory=context_factory)

    cli.add_generic_option('--quiet', action='store_true',
                           help='turn of debugging')

    @cli.command(__name__ + ':foo_main')
    def foo(parser):
        """
        a short description ending in a period.

        a longer description
        """
        parser.add_argument('--bar', action='store_true',
                            help='turn on bar')

    def foo_main(app, args):
        app.info('Hello World!')

    result = cli.run()
    sys.exit(result)

Lazy Decorators
===============

Commands can be defined lazily and picked up later. This removes ordering
restrictions between the commands and the cli object.

::

    # myapp/info.py

    from subparse import command

    @command('myapp.info:foo_main')
    def foo(parser):
        """perform foo"""

::

    cli = CLI()
    cli.load_commands('myapp.info')

Entry Points
============

Commands may also be defined in external modules and loaded via entry
points.

::

    from subparse import cli

    cli = CLI()
    cli.load_commands_from_entry_point('myapp.commands')

An extension application would then define the external module that should
be searched for commands. Again this allows the commands themselves to be
defined independently of the main functions, improving import speed.

::

    [myapp.commands]
    barpkg = barpkg.commands

::

    # barpkg/commands.py

    from subparse import command

    @command('barpkg.bar')
    def bar(parser):
        """perform bar"""

::

    # barpkg/bar.py

    def main(app, args):
        pass

