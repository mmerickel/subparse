import pytest

def test_basic():
    from subparse import CLI

    cli = CLI()

    @cli.subcommand('subparse.tests.fixtures.foo')
    def foo(parser):
        parser.add_argument('--bar', action='store_true')

    args = cli.parse(['foo', '--bar'])
    assert args.bar is True

    app = {}
    result = cli.dispatch(args, context=app)
    assert app['bar'] is True
    assert result == 0

def test_basic_decorator_dict():
    from subparse import CLI, subcommand

    @subcommand('subparse.tests.fixtures.foo')
    def foo(parser):
        parser.add_argument('--bar', action='store_true')

    cli = CLI()
    cli.load_commands(locals())

    args = cli.parse(['foo', '--bar'])
    assert args.bar is True

    app = {}
    result = cli.dispatch(args, context=app)
    assert app['bar'] is True
    assert result == 0

def test_underscore_command_name_converted_to_dash():
    from subparse import CLI

    cli = CLI()

    @cli.subcommand('subparse.tests.fixtures.foo')
    def foo_bar(parser):
        parser.add_argument('--bar', action='store_true')

    args = cli.parse(['foo-bar', '--bar'])
    assert args.bar is True

    app = {}
    result = cli.dispatch(args, context=app)
    assert app['bar'] is True
    assert result == 0

def test_override_command_name():
    from subparse import CLI

    cli = CLI()

    @cli.subcommand('subparse.tests.fixtures.foo', 'baz')
    def foo_bar(parser):
        parser.add_argument('--bar', action='store_true')

    args = cli.parse(['baz', '--bar'])
    assert args.bar is True

    app = {}
    result = cli.dispatch(args, context=app)
    assert app['bar'] is True
    assert result == 0

def test_alternate_main():
    from subparse import CLI

    cli = CLI()

    @cli.subcommand('subparse.tests.fixtures.foo:foo_main')
    def foo(parser):
        parser.add_argument('--bar', action='store_true')

    args = cli.parse(['foo', '--bar'])
    assert args.bar is True

    app = {}
    result = cli.dispatch(args, context=app)
    assert app['fn'] == 'foo_main'
    assert app['bar'] is True
    assert result == 0

def test_help_command(capsys):
    from subparse import CLI

    cli = CLI()

    @cli.subcommand('subparse.tests.fixtures.foo')
    def foo(parser):
        parser.add_argument('--bar', action='store_true')

    pytest.raises(SystemExit, cli.parse, ['help', 'foo'])
    out, err = capsys.readouterr()
    assert 'usage:' in out

def test_bad_options(capsys):
    from subparse import CLI

    cli = CLI()

    @cli.subcommand('subparse.tests.fixtures.foo')
    def foo(parser):
        parser.add_argument('--bar', action='store_true')

    pytest.raises(SystemExit, cli.parse, ['foo', '--missing'])
    out, err = capsys.readouterr()
    assert 'usage:' in out

def test_version_default(capsys):
    from subparse import CLI

    cli = CLI(version='foo')

    pytest.raises(SystemExit, cli.parse, ['--version'])
    out, err = capsys.readouterr()
    assert err == 'foo\n'
