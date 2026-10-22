# Contributing

This is a small independent open-source research utility. Bug reports, documentation fixes, and focused pull requests are welcome.

1. Use **fabricated/synthetic or fully permission-cleared STO data** in issues. Never upload participant records, private study data, unpublished manuscripts, proprietary models, passwords or license keys.
2. Report Python version, operating system, a small reproducible input, expected behavior and actual behavior.
3. Open a PR with one focused change and regression tests. Run `python -m pip install -e .` then `python -m unittest discover -s tests -v`.
4. For any metric or parsing change, identify units, time-window behavior, failure cases, and assumptions. Do not infer missing scientific data or claim validated biological effects.
5. The project maintainer reviews and merges changes when technically and scientifically appropriate. Participation is under the Apache-2.0 license.

See [docs/ROADMAP.md](docs/ROADMAP.md). This project is not the upstream SCONE repository.
