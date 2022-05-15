from subparse import command

@command('.foo')
def foo(parser):
    """Hello world

    This is a long command.
    """
    parser.set_defaults(call='foo')
    parser.add_argument('--bar', action='store_true')
