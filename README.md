# patternplate

Offline boilerplate generator whose every layout decision is backed by
measured adoption across the **top 100 weekly trending GitHub repos**
(October 2026 snapshot: union of official trending pages, 100 repos,
64 surviving license and age filters).

No network calls. No dependencies. Python 3.9+, standard library only.

## Why

Most generators encode one author's taste. patternplate encodes what the
fastest-growing open source projects actually ship right now: flat python
layouts (src/ adoption is 15.6% overall), pytest-style `tests/` dirs,
`.github/workflows` CI (85-93% adoption in both language families),
top-pinned action versions, the measured `.gitignore` lines, and the README
sections that dominate current trending READMEs.

## Install

```bash
pip install .
```

## Use

```bash
# see the measured archetypes
patternplate kinds

# why each element exists, with adoption numbers and example repos
patternplate why python-cli

# scaffold (creates ./<name>/)
patternplate new python-cli mytool --author "Your Name"
patternplate new python-lib mylib
patternplate new ts-cli mycli
patternplate new ts-lib mylib
```

## Kinds (measured)

| kind | repos in scan | share of licensed trending set | tests adoption | CI adoption |
|---|---|---|---|---|
| python-lib | 9 | 33.3% | 44.4% | 88.9% |
| python-cli | 5 | 18.5% | 100.0% | 100.0% |
| ts-lib | 8 | 29.6% | 25.0% | 75.0% |
| ts-cli | 5 | 18.5% | 100.0% | 100.0% |

(`patternplate kinds` recomputes this from the shipped scan data.)

## What gets generated

- package layout chosen by the measured `src_layout` rate (flat wins today)
- `pyproject.toml` / `package.json` with the measured build backend
  (setuptools) and zero runtime dependencies
- test suite wired to the stdlib runner (`unittest` / `node --test`) with a
  real smoke test, not a placeholder
- `.github/workflows/ci.yml` using the most commonly pinned action versions
- `.gitignore` containing exactly the lines that appear in 2+ same-family
  trending repos
- README with the measured top sections (Installation, Usage, Features,
  Contributing, License)
- MIT LICENSE and CONTRIBUTING.md when adoption clears the threshold

`provenance.md` (generated, never hand-typed) maps every element to its
measured adoption and example trending repos.

## Verify

```bash
make verify
```

Runs the test suite (12 tests, including executing the generated scaffold's
own test suite in a subprocess) and recomputes `scan/patterns.json` from
`scan/features.json` to prove no number drifted.

## Scan data

`scan/` contains the snapshot: `repos.csv` (100 trending repos with the
keep/drop decision per repo), `features.json` (extracted per-repo
architecture features), `patterns.json` (aggregated adoption stats),
`trending_snapshot.json` (methodology and pool). The full scan pipeline
lives at `limitlessprojects/trending-pain-study`.
