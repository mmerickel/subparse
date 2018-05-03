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
