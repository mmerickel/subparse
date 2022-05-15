from subparse import command


@command(__name__)
def foo(parser):
    parser.set_defaults(call='foo')
    parser.add_argument('--bar', action='store_true')


@command('.')
def foo_main_dot(parser):
    parser.set_defaults(call='foo_main_dot')
    parser.add_argument('--bar', action='store_true')


@command(__name__ + ':foo_main')
def foo_main_absolute_colon(parser):
    parser.set_defaults(call='foo_main_absolute_colon')
    parser.add_argument('--bar', action='store_true')


@command(__name__ + '.foo_main')
def foo_main_dotted(parser):
    parser.set_defaults(call='foo_main_dotted')
    parser.add_argument('--bar', action='store_true')


@command('.foo_main')
def foo_main_relative_leading_dot(parser):
    parser.set_defaults(call='foo_main_relative_leading_dot')
    parser.add_argument('--bar', action='store_true')


@command(':foo_main')
def foo_main_relative_leading_colon(parser):
    parser.set_defaults(call='foo_main_relative_leading_colon')
    parser.add_argument('--bar', action='store_true')


@command('.foo:bar_main', 'bar')
def bar_options(parser):
    parser.set_defaults(call='bar_options')
    parser.add_argument('--bar', action='store_true')


def main(app, args):
    app['fn'] = 'main'
    app['call'] = getattr(args, 'call', None)
    app['bar'] = args.bar


def foo_main(app, args):
    app['fn'] = 'foo_main'
    app['call'] = getattr(args, 'call', None)
    app['bar'] = args.bar


def bar_main(app, args):
    app['fn'] = 'bar_main'
    app['call'] = getattr(args, 'call', None)
    app['bar'] = args.bar
