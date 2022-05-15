import argparse
from collections import namedtuple
from contextlib import contextmanager
from importlib import import_module
import importlib.metadata
import inspect
import sys

from .lazydecorator import lazydecorator

command = lazydecorator()

CommandMeta = namedtuple(
    'CommandMeta',
    ['factory', 'main', 'name', 'help', 'description', 'context_kwargs'],
)


class ArgumentParser(argparse.ArgumentParser):
    def error(self, message):
        """Raise errors instead of printing and raising SystemExit."""
        raise argparse.ArgumentError(None, message)


class CLI:
    _ArgumentParser = ArgumentParser
    _namespace_key = '_subparse_meta'

    def __init__(
        self,
        prog=None,
        usage=None,
        description=None,
        version=None,
        add_help_command=True,
        context_factory=None,
    ):
        self.prog = prog
        self.usage = usage
        self.description = description
        self.version = version
        self.add_help_command = add_help_command
        self.generic_options = []
        self.commands = {}
        self.context_factory = context_factory

        if version is not None:
            self.add_generic_option(
                '-V', '--version', action='version', version=version
            )

    def add_generic_options(self, generic_options):
        """
        Register a function containing generic options.

        The function should accept an instance of an
        :class:`argparse.ArgumentParser` and use it to define extra
        arguments and options.

        """
        self.generic_options.append(generic_options)

    def add_generic_option(self, *args, **kwargs):
        def generic_options(parser):
            parser.add_argument(*args, **kwargs)

        self.add_generic_options(generic_options)

    def add_command(self, factory, main, name=None, context_kwargs=None):
        """
        Attach a command directly to the :class:`CLI` object.

        """
        if name is None:
            name = factory.__name__.replace('_', '-')

        if context_kwargs is None:
            context_kwargs = {}

        short_desc, long_desc = parse_docstring(factory.__doc__)
        if long_desc:
            long_desc = short_desc + '\n\n' + long_desc

        # determine the absolute import string if relative
        if isinstance(main, str) and (main.startswith('.') or main.startswith(':')):
            module = __import__(factory.__module__, None, None, ['__doc__'])
            package = package_for_module(module)
            if main in ['.', ':']:
                main = package.__name__
            else:
                main = package.__name__ + main

        self.commands[name] = CommandMeta(
            factory=factory,
            main=main,
            name=name,
            help=short_desc,
            description=long_desc,
            context_kwargs=context_kwargs,
        )

    def command(self, *args, **kwargs):
        """
        Attach a command to the current :class:`CLI` object.

        The function should accept an instance of an
        :class:`argparse.ArgumentParser` and use it to define extra
        arguments and options. These options will only affect the specified
        command.

        """

        def wrapper(func):
            self.add_command(func, *args, **kwargs)
            return func

        return wrapper

    def load_commands(self, obj):
        """
        Load commands defined on an arbitrary object.

        All functions decorated with the :func:`subparse.command` decorator
        attached the specified object will be loaded. The object may
        be a dictionary, an arbitrary python object, or a dotted path.

        The dotted path may be absolute, or relative to the current package
        by specifying a leading '.' (e.g. ``'.commands'``).

        """
        if isinstance(obj, str):
            obj = obj.replace(':', '.')
            package = caller_package().__name__ if obj.startswith('.') else None
            obj = import_module(obj, package)
        command.discover_and_call(obj, self.command)

    def load_commands_from_entry_point(self, specifier):
        """
        Load commands defined within a distribution entry point.

        Each entry will be a module that should be searched for functions
        decorated with the :func:`subparse.command` decorator. This
        operation is not recursive.

        """
        eps = importlib.metadata.entry_points()

        # getitem is deprecated in 3.10, so test for select and fallback
        # gracefully for 3.8/3.9
        entries = (
            eps.select(group=specifier) if hasattr(eps, 'select') else eps[specifier]
        )

        for ep in entries:
            module = ep.load()
            command.discover_and_call(module, self.command)

    def run(self, argv=None):
        """
        Run the command-line application.

        This will dispatch to the specified function or raise a
        ``SystemExit`` and output the appropriate usage information
        if there is an error parsing the arguments.

        The default ``argv`` is equivalent to ``sys.argv[1:]``.

        """
        if argv is None:  # pragma: no cover
            argv = sys.argv[1:]
        argv = [str(v) for v in argv]
        meta, args = parse_args(self, argv)
        context_factory = contextmanager(make_generator(self.context_factory))
        with context_factory(self, args, **meta.context_kwargs) as context:
            main = load_main(meta)
            return main(context, args) or 0


def parse_args(cli, argv):
    parser = cli._ArgumentParser(
        prog=cli.prog,
        usage=cli.usage,
        description=cli.description,
        formatter_class=argparse.RawTextHelpFormatter,
    )
    add_generic_options(parser, cli.generic_options)
    add_commands(parser, cli.commands, cli._namespace_key)
    try_argcomplete(parser)
    try:
        if cli.add_help_command:
            if argv and argv[0] == 'help':
                argv.pop(0)
                argv.append('--help')

        args = parser.parse_args(argv)
        meta = getattr(args, cli._namespace_key, None)
        if not meta:
            parser.print_help(file=sys.stderr)
            parser.exit(2)
        return meta, args

    except argparse.ArgumentError as e:
        parser.print_help(file=sys.stderr)
        parser.exit(2, f'{parser.prog}: error: {str(e)}\n')


def load_main(meta):
    main = meta.main
    if isinstance(main, str):
        mod = main
        func = 'main'
        if ':' in mod:
            mod, func = mod.split(':')
        mod = __import__(mod, None, None, ['__doc__'])
        main = getattr(mod, func)
    return main


def make_generator(fn):
    if inspect.isgeneratorfunction(fn):
        return fn

    def wrapper(*a, **kw):
        ctx = None
        if fn is not None:
            ctx = fn(*a, **kw)
        yield ctx

    return wrapper


def trim(docstring):
    """Trim function from PEP-257."""
    if not docstring:  # pragma: no cover
        return ''
    # Convert tabs to spaces (following the normal Python rules)
    # and split into a list of lines:
    lines = docstring.expandtabs().splitlines()
    # Determine minimum indentation (first line doesn't count):
    indent = sys.maxsize
    for line in lines[1:]:
        stripped = line.lstrip()
        if stripped:
            indent = min(indent, len(line) - len(stripped))
    # Remove indentation (first line is special):
    trimmed = [lines[0].strip()]
    if indent < sys.maxsize:
        for line in lines[1:]:
            trimmed.append(line[indent:].rstrip())
    # Strip off trailing and leading blank lines:
    while trimmed and not trimmed[-1]:
        trimmed.pop()
    while trimmed and not trimmed[0]:
        trimmed.pop(0)
    # Return a single string:
    return '\n'.join(trimmed)


def parse_docstring(docstring):
    """
    Parse a PEP-257 docstring.

    SHORT -> blank line -> LONG

    """
    short_desc = long_desc = ''
    if docstring:
        docstring = trim(docstring)
        lines = docstring.split('\n\n', 1)
        short_desc = lines[0].strip().replace('\n', ' ')

        if len(lines) > 1:
            long_desc = lines[1].strip()
    return short_desc, long_desc


def try_argcomplete(parser):  # pragma: no cover
    try:
        import argcomplete
    except ImportError:
        pass
    else:
        argcomplete.autocomplete(parser)


def add_generic_options(parser, fns):
    for func in fns:
        func(parser)


def add_commands(parser, commands, namespace_key):
    subparsers = parser.add_subparsers(title='commands', metavar='<command>')
    for meta in sorted(commands.values(), key=lambda m: m.name):
        subparser = subparsers.add_parser(
            meta.name,
            help=meta.help,
            description=meta.description,
            formatter_class=argparse.RawTextHelpFormatter,
        )
        meta.factory(subparser)
        subparser.set_defaults(**{namespace_key: meta})


# stolen from pyramid.path
def caller_module(level=2):
    module_globals = sys._getframe(level).f_globals
    module_name = module_globals.get('__name__') or '__main__'
    module = sys.modules[module_name]
    return module


# stolen from pyramid.path
def package_for_module(module):  # pragma: no cover
    f = getattr(module, '__file__', '')
    if ('__init__.py' in f) or ('__init__$py' in f):  # empty at >>>
        # Module is a package
        return module
    # Go up one level to get package
    package_name = module.__name__.rsplit('.', 1)[0]
    return sys.modules[package_name]


# stolen from pyramid.path
def caller_package(level=2):
    # caller_module in arglist for tests
    module = caller_module(level + 1)
    return package_for_module(module)
