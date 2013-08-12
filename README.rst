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

    def context_factory(cli, args):
        return MyApp(args)

    def generic_options(parser):
        parser.add_argument('--quiet', action='store_true',
                            help='turn of debugging')

    cli = CLI(version='0.0', context_factory=context_factory)
    cli.add_generic_options(generic_options)

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

A module containing commands can be defined irrespective of the actual
``CLI`` instance:

::

    # myapp/info.py

    from subparse import command

    @command('myapp.info:foo_main')
    def foo(parser):
        """perform foo"""

Later, when an instance of a ``CLI`` is created, the commands can be loaded
and registered:

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

An extension package should define a module containing the supported
commands:

::

    # barpkg/commands.py

    from subparse import command

    @command('barpkg.bar')
    def bar(parser):
        """perform bar"""

The package should also define the function to be called for each command.
Optionally in a separate module to avoid importing run-time dependencies
during parsing:

::

    # barpkg/bar.py

    def main(app, args):
        pass

The package can then broadcast the module ``barpkg.commands``
containing the supported commands:

::

    [myapp.commands]
    barpkg = barpkg.commands

Now when your extension package is installed the commands will automatically
become available.

