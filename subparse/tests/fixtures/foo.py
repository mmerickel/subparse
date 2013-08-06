def main(app, args):
    app['fn'] = 'main'
    app['bar'] = args.bar

def foo_main(app, args):
    app['fn'] = 'foo_main'
    app['bar'] = args.bar
