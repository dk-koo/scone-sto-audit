# Maintainer and verification status

- **Project:** SCONE STO Audit; independent Python utility maintained by Dong-Kyun Koo (GitHub: [dk-koo](https://github.com/dk-koo)).
- **Source:** [public repository](https://github.com/dk-koo/scone-sto-audit), Apache-2.0.
- **First public source:** 2026-10-22; current package metadata version is 0.2.0. A formal GitHub Release/tag has **not** been published as of this verification.
- **Automated validation:** [GitHub Actions run 39743298521](https://github.com/dk-koo/scone-sto-audit/actions/runs/39743298521) completed successfully across four matrix jobs (Ubuntu and Windows; Python 3.10 and 3.12). Each job installs the package, runs the unit test suite, and performs a command-line smoke test.
- **Test scope:** 28 tests with fabricated input cases; package installation, time-series parsing, timestamp and STO metadata validation, sampled numerical summaries, report provenance, and CLI behavior. These are **software tests**, not independent biomechanical validation.
- **Tracked maintenance:** [Issue #1](https://github.com/dk-koo/scone-sto-audit/issues/1), for realistic STO dialect fixtures and format compatibility work.
- **Contributions:** [CONTRIBUTING.md](../CONTRIBUTING.md), [SECURITY.md](../SECURITY.md), and [roadmap](ROADMAP.md).

## Limits and evidence gaps

The repository is new. There is no verified evidence yet of substantial third-party usage, broad adoption, sustained issue triage, external pull requests, or a tagged release. No stars, downloads, outside maintainers, SCONE core maintainership, independent scientific validation, or research results should be inferred. The tool only analyzes existing text STO results; it does not run or optimize SCONE models.

## Reproducible baseline

```sh
python -m pip install -e .
python -m unittest discover -s tests -v
python -m scone_sto_audit examples/synthetic.sto --columns hip_flexion_r knee_angle_r --start 0.0 --end 0.2
```

Keep this document aligned with actual GitHub evidence and update it only when milestones are verifiable.
