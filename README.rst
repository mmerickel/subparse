========
subparse
========

A wrapper for argparse that provides decorator-based subcommand support.

Subcommands can be defined separately from their actual main functions,
enabling faster import times.

Basic Usage
===========

::

    from subparse import CLI

    cli = CLI(version='0.0')
    cli.add_generic_option('--quiet', action='store_true',
                           help='turn of debugging')

    @cli.subcommand(__name__ + ':foo_main')
    def foo(parser):
        """
        a short description ending in a period.

        a longer description
        """
        parser.add_argument('--bar', action='store_true',
                            help='turn on bar')

    def foo_main(app, args):
        pass

    args = cli.parse()
    app = MyApp(args)
    cli.dispatch(args, context=app)

Lazy Decorators
===============

Subcommands can be defined lazily and picked up later. This removes ordering
restrictions between the subcommands and the cli object.

::

    # myapp/info.py

    from subparse import subcommand

    @subcommand('myapp.info:foo_main')
    def foo(parser):
        """perform foo"""

::

    import myapp.info

    cli = CLI()
    cli.load_commands(myapp.info)

Entry Points
============

Subcommands may also be defined in external modules and loaded via entry
points.

::

    from subparse import cli

    cli = CLI()
    cli.load_commands_from_entry_point('myapp.subcommands')

An extension application would then define the external module that should
be searched for subcommands. Again this allows the commands themselves
to be defined independently of the main functions, improving import speed.

::

    [myapp.subcommands]
    barpkg = barpkg.subcommands

::

    # barpkg/subcommands.py

    from subparse import subcommand

    @subcommand('barpkg.bar')
    def bar(parser):
        """perform bar"""

::

    # barpkg/bar.py

    def main(app, args):
        pass

