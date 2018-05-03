import argparse
from contextlib import contextmanager
import inspect
import pkg_resources
import sys

from .lazydecorator import lazydecorator

command = lazydecorator()

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
                 context_factory=None,
                 ):
        self.prog = prog
        self.usage = usage
        self.description = description
        self.version = version
        self.add_help_command = add_help_command
        self.generic_options = []
        self.commands = []
        self.context_factory = context_factory

        if version is not None:
            self.add_generic_option(
                '-V', '--version', action='version', version=version)

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

    def command(self, *args, **kwargs):
        """
        Attach a command to the current :class:`CLI` object.

        The function should accept an instance of an
        :class:`argparse.ArgumentParser` and use it to define extra
        arguments and options. These options will only affect the specified
        command.

        """
        def wrapper(func):
            self.commands.append((func, args, kwargs))
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
            if obj.startswith('.') or obj.startswith(':'):
                package = caller_package()
                if obj in ['.', ':']:
                    obj = package.__name__
                else:
                    obj = package.__name__ + obj
            obj = pkg_resources.EntryPoint.parse(
                'x=%s' % obj).load(False)
        command.discover_and_call(obj, self.command)

    def load_commands_from_entry_point(self, specifier):
        """
        Load commands defined within a pkg_resources entry point.

        Each entry will be a module that should be searched for functions
        decorated with the :func:`subparse.command` decorator. This
        operation is not recursive.

        """
        for ep in pkg_resources.iter_entry_points(specifier):
            module = ep.load()
            command.discover_and_call(module, self.command)

    def parse(self, argv=None):
        if argv is None:  # pragma: no cover
            argv = sys.argv[1:]
        argv = [str(v) for v in argv]
        parser = MyArgumentParser(
            prog=self.prog,
            usage=self.usage,
            description=self.description,
        )
        add_generic_options(parser, self.generic_options)
        add_commands(parser, self.commands)
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
        if isinstance(args.mainloc, str):
            mod = args.mainloc
            func = 'main'
            if ':' in mod:
                mod, func = mod.split(':')
            mod = __import__(mod, None, None, ['__doc__'])
            method = getattr(mod, func)
        else:
            method = args.mainloc
        return method(context, args) or 0

    def run(self, argv=None):
        """
        Run the command-line application.

        This will dispatch to the specified function or raise a
        ``SystemExit`` and output the appropriate usage information
        if there is an error parsing the arguments.

        The default ``argv`` is equivalent to ``sys.argv[1:]``.

        """
        args = self.parse(argv)
        context_factory = contextmanager(make_generator(self.context_factory))
        with context_factory(self, args) as context:
            return self.dispatch(args, context=context)


def make_generator(fn):
    if inspect.isgeneratorfunction(fn):
        return fn
    def wrapper(*a, **kw):
        ctx = None
        if fn is not None:
            ctx = fn(*a, **kw)
        yield ctx
    return wrapper


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

def add_commands(parser, commands):
    subparsers = parser.add_subparsers(title='commands', metavar='<command>')
    for func, args, kwargs in commands:
        if len(args) > 1:
            name = args[1]
        else:
            name = func.__name__.replace('_', '-')
        doc, description = parse_docstring(func.__doc__)
        subparser = subparsers.add_parser(
            name, description=description, help=doc)
        func(subparser)
        mainloc = args[0]
        if isinstance(mainloc, str):
            if mainloc.startswith('.') or mainloc.startswith(':'):
                module = __import__(func.__module__, None, None, ['__doc__'])
                package = package_for_module(module)
                if mainloc in ['.', ':']:
                    mainloc = package.__name__
                else:
                    mainloc = package.__name__ + mainloc
        subparser.set_defaults(mainloc=mainloc)

# stolen from pyramid.path
def caller_module(level=2):
    module_globals = sys._getframe(level).f_globals
    module_name = module_globals.get('__name__') or '__main__'
    module = sys.modules[module_name]
    return module

# stolen from pyramid.path
def package_for_module(module):
    f = getattr(module, '__file__', '')
    if (('__init__.py' in f) or ('__init__$py' in f)):  # empty at >>>
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
