# Contributing to Orca

## Filing Issues

[Issues](https://gitlab.gnome.org/GNOME/orca/-/work_items) should always be filed
for bug reports and proposed features. Please do not use the issue tracker for
support questions. If you need help or have questions about Orca, the [Orca mailing list](https://www.freelists.org/list/orca) is a great place to ask.

When filing an issue, please provide the following:

* Version details:
   * Output of `orca -v`
   * For bugs, and if known, the version or commit of Orca where the bug is not present
* Concrete and concise steps to reproduce the bug
* Expected and actual results
* If appropriate, a test page, document, or other reproducer
* If appropriate, [a debug log](https://orca.gnome.org/debugging.html) captured showing
  the problem

These details make it much easier for maintainers to understand and reproduce the
issue you are reporting.

It is not necessary to provide detailed analysis. The developers working on your
issue will perform their own analysis regardless of whether you provide one or not.

## Submitting Merge Requests

For non-trivial bug fixes and feature contributions, please file an issue first.
This helps the maintainers better understand your proposed change. Merge requests
for non-trivial changes that are submitted without an issue may be ignored or closed
by the maintainers.

Please keep in mind that while Orca is the screen reader of all desktop environments,
it is part of the GNOME project. As such, merge requests for new features that do not
work in Wayland will not be accepted.

Be prepared to explain your changes yourself. Do not submit changes that you do not
fully understand. If you cannot be certain that your contribution complies with Orca's
license (LGPL 2.1 or later), it should not be submitted.

Smaller changes are highly preferred. The bigger the change, the longer it will take
the maintainers to review it.

Prefer self-documenting code over code comments. When code comments are needed, they
should be clear and concise.

Provide integration tests wherever possible. Integration tests provide coverage for
actual Orca usage with applications and are much more likely to catch regressions than
a heavily-mocked unit test. Your integration test(s) should fail without your change
and pass with it. If you are able to provide an integration test that covers your change,
there is no need to also provide a unit test.

Note that Orca's integration test suite is still growing. If adding integration test
coverage cannot be done due to the current lack of the necessary app needed to reproduce
the bug, please check with the maintainers regarding how to proceed. See
[tests/README.md](tests/README.md) for the current state and documentation related to
Orca's tests.

Be sure that the issue you are addressing is still reproducible in Orca's main branch.
If you have identified a bug in an earlier version of Orca and have a proposed fix
based on that version, there is a possibility that the issue has since been addressed
through a different solution. The integration tests make that easy to detect, but if
writing an integration test was not possible, you must manually verify that your change
is still needed.

Orca provides pre-commit hooks for formatting, linting, spelling, project-specific
rules, and type checking. Most distros provide a `pre-commit` package. Otherwise you
can install it via `pip`. Run `pre-commit install` after installing the package.
The hooks run automatically when you commit, and some modify files. If the pre-commit
hooks prevent your commit from succeeding, read the output, address any failures that
the hooks didn't address automatically, and retry the commit.

Merge requests must be submitted as drafts unless and until they are ready for
maintainer review. Do not mark a merge request as ready for review until you have
reviewed and tested your changes, completed the applicable checks described above,
and are prepared to address technical questions about your implementation. A change
appearing to work as intended does not necessarily mean it is ready for review.

Commit messages should be in the following format:

```
Title of the commit

Explanation of the commit. This should be concise, but provide enough
details for the maintainers reviewing your change. Any other information
should be contained in the issue you filed for the change.

XXX issue #1234 (where XXX is "Closes" or "See")
```

## Consider Writing a User Extension

Orca v51 and later support User Extensions. User Extensions make it possible for you
to develop and share features which may fall beyond the scope of Orca itself. See
[docs/user-extensions.md](docs/user-extensions.md) for more information.
