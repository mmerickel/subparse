from subparse import subcommand

@subcommand(__name__)
def foo(parser):
    parser.add_argument('--bar', action='store_true')

@subcommand(__name__ + ':foo_main')
def foo_bar(parser):
    parser.add_argument('--bar', action='store_true')

@subcommand('.foo:bar_main', 'bar')
def bar_options(parser):
    parser.add_argument('--bar', action='store_true')

def main(app, args):
    app['fn'] = 'main'
    app['bar'] = args.bar

def foo_main(app, args):
    app['fn'] = 'foo_main'
    app['bar'] = args.bar

def bar_main(app, args):
    app['fn'] = 'bar_main'
    app['bar'] = args.bar
