# Scientific scope and reproducibility boundary

## In scope (implemented)
- Strict scalar, whitespace-delimited STO parsing with case-insensitive `endheader`
- Structural checks on declared rows/columns, unique channels, finite scalar values, strictly increasing time
- Inclusive time window selection, sampled statistics and raw input SHA-256 provenance
- Deterministic batch JSON for fully valid inputs only

## Explicitly out of scope
- Running or optimizing simulations; obtaining or circumventing a Hyfydy license
- Converting radians/degrees or applying biomechanical model coordinate conventions
- Estimating gait events, normalizing strides, interpolating endpoints, filtering signals
- Computing validated joint loads, inferential statistics or clinical conclusions

## Interpretation
- `range` = sampled maximum minus minimum; **not automatically a validated joint ROM**
- `mean_sampled` = arithmetic mean of observed points; **not a time-weighted integral**
- `peak_absolute` = largest absolute sampled magnitude, preserving original source units
- The STO time column is assumed to be seconds; researchers must verify that assumption
- `inDegrees` is recorded as header metadata; it does **not** prove the unit of arbitrary channels
- For fixed windows, boundaries are inclusive and no new samples are interpolated
- An input hash verifies which byte sequence was read, not independent numerical correctness
- Multiple files are not independent biological replicates by default

## Independent validation
Tests use fabricated synthetic fixtures and do not establish accuracy against
specific SCONE versions, model families, laboratory kinematics, or subject data.
Real scientific use requires independent model- and study-specific checks.
