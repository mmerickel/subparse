import pytest

def make_cli(*args, **kwargs):
    from subparse import CLI

    context_factory = kwargs.pop('context_factory', None)
    if context_factory is None:
        context = kwargs.pop('context', None)
        context_factory = lambda a, b: context

    return CLI(*args, context_factory=context_factory, **kwargs)

def test_basic():
    app = {}
    cli = make_cli(context=app)

    @cli.command('subparse.tests.fixtures.foo')
    def foo(parser):
        parser.add_argument('--bar', action='store_true')

    result = cli.run(['foo', '--bar'])
    assert app['bar'] is True
    assert result == 0

def test_context_generator():
    out = []
    def context_factory(cli, args):
        out.append(1)
        yield {}
        out.append(2)
    cli = make_cli(context_factory=context_factory)

    @cli.command('subparse.tests.fixtures.foo')
    def foo(parser):
        parser.add_argument('--bar', action='store_true')

    result = cli.run(['foo', '--bar'])
    assert result == 0
    assert out == [1, 2]

def test_basic_decorator_dict():
    from subparse import command

    @command('subparse.tests.fixtures.foo')
    def foo(parser):
        parser.add_argument('--bar', action='store_true')

    app = {}
    cli = make_cli(context=app)
    cli.load_commands(locals())

    result = cli.run(['foo', '--bar'])
    assert app['bar'] is True
    assert result == 0

def test_load_module():
    from subparse.tests.fixtures import foo

    app = {}
    cli = make_cli(context=app)
    cli.load_commands(foo)

    result = cli.run(['bar'])
    assert app['fn'] == 'bar_main'
    assert app['bar'] is False
    assert result == 0

def test_load_module_dotted():
    cli = make_cli()
    cli.load_commands('subparse.tests.fixtures.foo')
    assert len(cli.commands) > 0

def test_load_module_dotted_relative():
    cli = make_cli()
    cli.load_commands('.fixtures.foo')
    assert len(cli.commands) > 0

def test_main_callable():
    from subparse.tests.fixtures.foo import main

    app = {}
    cli = make_cli(context=app)

    @cli.command(main)
    def foo(parser):
        parser.add_argument('--bar', action='store_true')

    result = cli.run(['foo', '--bar'])
    assert app['fn'] == 'main'
    assert app['bar'] is True
    assert result == 0

def test_main_dotted_relative():
    app = {}
    cli = make_cli(context=app)

    @cli.command('.fixtures.foo:foo_main')
    def foo(parser):
        parser.add_argument('--bar', action='store_true')

    result = cli.run(['foo', '--bar'])
    assert app['fn'] == 'foo_main'
    assert app['bar'] is True
    assert result == 0

def test_underscore_command_name_converted_to_dash():
    app = {}
    cli = make_cli(context=app)

    @cli.command('subparse.tests.fixtures.foo')
    def foo_bar(parser):
        parser.add_argument('--bar', action='store_true')

    result = cli.run(['foo-bar', '--bar'])
    assert app['bar'] is True
    assert result == 0

def test_underscore_command_name_preserved():
    app = {}
    cli = make_cli(context=app)

    @cli.command('subparse.tests.fixtures.foo', 'foo_bar')
    def foo_bar(parser):
        parser.add_argument('--bar', action='store_true')

    result = cli.run(['foo_bar', '--bar'])
    assert app['bar'] is True
    assert result == 0

def test_override_command_name():
    app = {}
    cli = make_cli(context=app)

    @cli.command('subparse.tests.fixtures.foo', 'baz')
    def foo_bar(parser):
        parser.add_argument('--bar', action='store_true')

    result = cli.run(['baz', '--bar'])
    assert app['bar'] is True
    assert result == 0

def test_alternate_main():
    app = {}
    cli = make_cli(context=app)

    @cli.command('subparse.tests.fixtures.foo:foo_main')
    def foo(parser):
        parser.add_argument('--bar', action='store_true')

    result = cli.run(['foo', '--bar'])
    assert app['fn'] == 'foo_main'
    assert app['bar'] is True
    assert result == 0

def test_help_command(capsys):
    cli = make_cli()

    @cli.command('subparse.tests.fixtures.foo')
    def foo(parser):
        parser.add_argument('--bar', action='store_true')

    pytest.raises(SystemExit, cli.run, ['help', 'foo'])
    out, err = capsys.readouterr()
    assert 'usage:' in out

def test_bad_options(capsys):
    cli = make_cli()

    @cli.command('subparse.tests.fixtures.foo')
    def foo(parser):
        parser.add_argument('--bar', action='store_true')

    pytest.raises(SystemExit, cli.run, ['foo', '--missing'])
    out, err = capsys.readouterr()
    assert 'usage:' in out

def test_version_default(capsys):
    cli = make_cli(version='foo')

    pytest.raises(SystemExit, cli.run, ['--version'])
    out, err = capsys.readouterr()
    assert err + out == 'foo\n'

def test_docstring(capsys):
    app = {}
    cli = make_cli(context=app)

    @cli.command('subparse.tests.fixtures.foo')
    def foo(parser):
        """foo. bar"""

    pytest.raises(SystemExit, cli.run, ['--help'])
    out, err = capsys.readouterr()
    assert 'foo.' in out
    assert 'bar' not in out

    pytest.raises(SystemExit, cli.run, ['foo', '--help'])
    out, err = capsys.readouterr()
    assert 'foo.' in out
    assert 'bar' in out
