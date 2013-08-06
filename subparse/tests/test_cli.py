import pytest

def test_basic():
    from subparse import CLI

    cli = CLI()

    @cli.subcommand('subparse.tests.test_cli:foo_main')
    def foo(parser):
        """
        short help
        """
        parser.add_argument('--bar', action='store_true')

    args = cli.parse(['foo', '--bar'])
    assert args.bar is True

    app = {}
    result = cli.dispatch(args, context=app)
    assert app['bar'] is True
    assert result == 0

def foo_main(app, args):
    app['bar'] = args.bar

def test_basic_decorator_dict():
    from subparse import CLI, subcommand

    @subcommand('subparse.tests.test_cli:foo_main')
    def foo(parser):
        """
        short help
        """
        parser.add_argument('--bar', action='store_true')

    cli = CLI()
    cli.load_commands(locals())

    args = cli.parse(['foo', '--bar'])
    assert args.bar is True

    app = {}
    result = cli.dispatch(args, context=app)
    assert app['bar'] is True
    assert result == 0
