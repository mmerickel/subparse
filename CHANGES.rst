0.6 (2022-05-15)
================

- Drop Python 2.7, 3.4, 3.5, 3.6, 3.7.

- Add Python 3.8, 3.9, 3.10.

- Drop dependency on pkg_resources and use importlib.metadata.

- 100% test coverage.

0.5.3 (2019-03-09)
==================

- Output help to ``sys.stderr`` when parsing fails.

- Support passing ``context_kwargs`` to the ``command`` decorator. These
  arguments will be passed to the ``context_factory`` when the command is
  executed.

0.5.2 (2019-03-09)
==================

- Sort subcommands in help output.

0.5.1 (2019-03-08)
==================

- Use the ``argparse.RawTextHelpFormatter`` formatter class.

0.5 (2019-03-08)
================

- Add Python 3.7 support.

- Fix a deprecation warning coming from setuptools.

- Conform more closely to PEP-257 for docstring parsing.

- Modify how the help text is displayed using the
  ``argparse.RawDescriptionHelpFormatter`` formatter class.

0.4 (2018-05-03)
================

- Drop Python 2.6, 3.2 and 3.3 support.

- Add Python 3.4, 3.5, 3.6 support.

- Allow the ``context_factory`` to be a generator which yields the context.
  This allows the context to wrap the full lifecycle of the CLI.

0.3.3 (2013-08-12)
==================

No functional changes from 0.3.2.

- Improve documentation.

0.3.2 (2013-08-06)
==================

- Add `CLI.run` API for simply executing the command line.

0.3.1 (2013-08-06)
==================

- Improve the help output.

0.3 (2013-08-06)
================

- Rename subcommands to commands in the API.

0.2 (2013-08-06)
================

- Underscores in function names are converted to dashes in their respective
  subcommand names.
- Add `CLI.add_generic_options` API.
- Add a new `help` subcommand, allowing for `myapp help foo`.
- Allow relative imports in the subcommand specification.

0.1 (2013-08-05)
================

- Initial Commits
