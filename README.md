# SCONE STO Audit

[![CI](https://github.com/dk-koo/scone-sto-audit/actions/workflows/ci.yml/badge.svg)](https://github.com/dk-koo/scone-sto-audit/actions/workflows/ci.yml)
[![License: Apache-2.0](https://img.shields.io/badge/license-Apache--2.0-blue.svg)](LICENSE)

**Small, independently maintained Python utility for auditing existing SCONE/OpenSim `.sto` time-series files.** It verifies structural validity and timestamps, computes source-unit descriptive metrics within a specified time window, and records SHA-256 input hashes for reproducibility. No SCONE executable or paid license is needed to analyze existing outputs.

> **Status: experimental (v0.2.0).** This is not upstream SCONE, a scientific validation package, an optimization engine, or medical software. It is a focused open-source analysis tool built by [dk-koo](https://github.com/dk-koo) to address reproducibility needs arising from predictive neuromusculoskeletal simulation research. Its software behavior is tested with synthetic data; independent biomechanical validation is not claimed.

## Features

- Parse UTF-8, whitespace-delimited scalar `.sto` tables with an `endheader` marker
- Reject missing/malformed table columns, bad row counts, duplicate channels, NaN/Inf values, nonincreasing timestamps, and unsupported unit-header values
- Compute sampled minimum, maximum, **range = max − min**, peak absolute value, and sample arithmetic mean
- Analyze inclusive user-selected time windows without interpolation or filtering
- Process several files in one command; retain an input SHA-256 for each result
- Generate human-readable, deterministic JSON reports; fail closed if any input is invalid
- Run with the Python standard library (no NumPy, SCONE binary, network calls or API key)

## Quickstart

Python **3.10+**. From the repository root:

```bash
python -m pip install -e .
python -m scone_sto_audit examples/synthetic.sto --columns hip_flexion_r knee_angle_r --start 0.0 --end 0.2 --output report.json
python -m unittest discover -s tests -v
```

Alternative installed CLI:

```bash
scone-sto-audit examples/synthetic.sto --columns knee_angle_r
```

The `examples/synthetic.sto` file is **fabricated demonstration data**, not a real participant or simulation. The commands operate on files locally; no user file is uploaded.

## Folder structure

```text
src/scone_sto_audit/   Parser, descriptive analysis and CLI
tests/                 Synthetic unit and CLI regression tests
examples/              Synthetic STO demonstration (no research results)
docs/                  Scientific scope, limitations and maintenance plans
.github/               GitHub Actions CI and issue-report template
pyproject.toml         Package metadata and CLI entry point
LICENSE                Apache-2.0 license for original utility
```

## Output interpretation and limitations

- `inDegrees` is recorded verbatim from the STO header but does **not** cause automatic conversion; every metric uses the original channel's source units. Joint-angle units and signs require verification against the generating model.
- The `range` statistic is **max minus min** of sampled points; it is **not automatically a clinically validated joint ROM**.
- No interpolation at window endpoints, gait-cycle normalization, missing-value imputation, filtering, hypothesis tests, muscle-force or joint-contact-force normalization.
- The `files_analyzed` field counts files only, **not independent subjects, model conditions, replications or participants**.
- No SCONE/Hyfydy execution, CMA-ES, scientific convergence testing, or automated scientific hypothesis verification.
- JSON reports store an input basename and SHA-256 but never serialize absolute source paths.

Read [Scientific scope](docs/SCIENTIFIC_SCOPE.md) before interpreting outputs for research.

## Development and community

Contributions, issues and corrections are welcome; see [CONTRIBUTING.md](CONTRIBUTING.md), [Roadmap](docs/ROADMAP.md), [Changelog](CHANGELOG.md) and [Security policy](SECURITY.md). The repository contains its own original implementation, separate from upstream [SCONE](https://github.com/tgeijten/scone-core), and does not claim to maintain the upstream solver.

Maintainer: **Dong-Kyun Koo** ([dk-koo](https://github.com/dk-koo)). License: [Apache-2.0](LICENSE). To cite the software, see [CITATION.cff](CITATION.cff). No published adoption metrics or research results are claimed.

## Public maintenance and verification evidence

The [CI workflow](https://github.com/dk-koo/scone-sto-audit/actions/workflows/ci.yml) installs the package and runs its synthetic regression suite plus CLI smoke checks on Linux and Windows with Python 3.10 and 3.12. The [verified four-job run](https://github.com/dk-koo/scone-sto-audit/actions/runs/39743298521) succeeded on 2026-10-22. See [maintenance evidence and limitations](docs/MAINTENANCE_STATUS.md) for traceable scope and current gaps.

