import argparse
import pkg_resources
import sys

from .lazydecorator import lazydecorator

__version__ = pkg_resources.get_distribution('subparse').version

subcommand = lazydecorator()

class MyArgumentParser(argparse.ArgumentParser):
    class ArgumentError(Exception):
        """An error from the argparse subsystem."""

    def error(self, message):
        """Raise errors instead of printing and raising SystemExit."""
        raise self.ArgumentError(message)

class CLI(object):

    def __init__(self,
                 prog=None,
                 usage=None,
                 description=None,
                 version=None,
                 add_help_command=True,
                 ):
        self.prog = prog
        self.usage = usage
        self.description = description
        self.version = version
        self.add_help_command = add_help_command
        self.generic_options = []
        self.subcommands = []

        if version is not None:
            self.add_generic_option(
                '-V', '--version', action='version', version=version)

    def add_generic_options(self, generic_options):
        self.generic_options.append(generic_options)

    def add_generic_option(self, *args, **kwargs):
        def generic_options(parser):
            parser.add_argument(*args, **kwargs)
        self.add_generic_options(generic_options)

    def subcommand(self, *args, **kwargs):
        def wrapper(func):
            self.subcommands.append((func, args, kwargs))
            return func
        return wrapper

    def load_commands(self, obj):
        subcommand.discover_and_call(obj, self.subcommand)

    def load_commands_from_entry_point(self, specifier):
        for ep in pkg_resources.iter_entry_points(specifier):
            module = ep.load()
            subcommand.discover_and_call(module, self.subcommand)

    def parse(self, argv=None):
        if argv is None:
            argv = sys.argv[1:]
        argv = map(str, argv)
        parser = MyArgumentParser(
            prog=self.prog,
            usage=self.usage,
            description=self.description,
        )
        add_generic_options(parser, self.generic_options)
        add_subcommands(parser, self.subcommands)
        try_argcomplete(parser)
        try:
            if self.add_help_command:
                if argv and argv[0] == 'help':
                    argv.pop(0)
                    argv.append('--help')

            args = parser.parse_args(argv)
            if not hasattr(args, 'mainloc'):
                return parser.parse_args(['-h'])
            return args
        except parser.ArgumentError as e:
            if not argv:
                return parser.parse_args(['-h'])
            parser.print_help()
            parser.exit(2, '{0}: error: {1}\n'.format(parser.prog, e.args[0]))

    def dispatch(self, args, context=None):
        mod = args.mainloc
        func = 'main'
        if ':' in mod:
            mod, func = mod.split(':')
        mod = __import__(mod, None, None, ['__doc__'])
        method = getattr(mod, func)
        return method(context, args) or 0

def parse_docstring(txt):
    description = txt
    if txt is None:
        txt = ''
    i = txt.find('.')
    if i == -1:
        doc = txt
    else:
        doc = txt[:i + 1]
    return doc, description

def try_argcomplete(parser):
    try:
        import argcomplete
    except ImportError:
        pass
    else:
        argcomplete.autocomplete(parser)

def add_generic_options(parser, fns):
    for func in fns:
        func(parser)

def add_subcommands(parser, subcommands):
    subparsers = parser.add_subparsers()
    for func, args, kwargs in subcommands:
        if len(args) > 1:
            name = args[1]
        else:
            name = func.__name__.replace('_', '-')
        doc, description = parse_docstring(func.__doc__)
        subparser = subparsers.add_parser(
            name, description=description, help=doc)
        func(subparser)
        mainloc = args[0]
        subparser.set_defaults(mainloc=mainloc)
