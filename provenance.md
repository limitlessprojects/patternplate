# provenance

Every emitted element is justified by measured adoption across the
top-100 weekly trending scan (2026-10-28, pool 488 repos, 64 after licensing/age filters).

| element | rule | measured adoption | example trending repos |
|---|---|---|---|
| python-lib: test suite | emitted always; runner is stdlib | 4 repos, 44.4% | `Graphify-Labs/graphify`, `TauricResearch/TradingAgents`, `fastapi/fastapi` |
| python-lib: CI workflow | emitted if adoption >= 50% | 8 repos, 88.9% | `Graphify-Labs/graphify`, `TauricResearch/TradingAgents`, `fastapi/fastapi` |
| python-lib: CONTRIBUTING.md | emitted if adoption >= 40% | 6 repos, 66.7% | `Graphify-Labs/graphify`, `mvanhorn/last30days-skill`, `anthropics/claude-cookbooks` |
| python-lib: layout | src/ if src_layout adoption >= 50%, else flat | 0 repos, 0.0% | `NVIDIA/SkillSpector` |
| python-lib: .gitignore | union of lines appearing in >= 2 same-family repos | 20 repos, n/a | measured lines, see scan/patterns.json |
| python-lib: README sections | top measured headings (installation, usage, features, contributing, license) | 5 repos, n/a | measured lines, see scan/patterns.json |
| python-cli: test suite | emitted always; runner is stdlib | 5 repos, 100.0% | `Graphify-Labs/graphify`, `TauricResearch/TradingAgents`, `fastapi/fastapi` |
| python-cli: CI workflow | emitted if adoption >= 50% | 5 repos, 100.0% | `Graphify-Labs/graphify`, `TauricResearch/TradingAgents`, `fastapi/fastapi` |
| python-cli: CONTRIBUTING.md | emitted if adoption >= 40% | 3 repos, 60.0% | `Graphify-Labs/graphify`, `mvanhorn/last30days-skill`, `anthropics/claude-cookbooks` |
| python-cli: layout | src/ if src_layout adoption >= 50%, else flat | 1 repos, 20.0% | `NVIDIA/SkillSpector` |
| python-cli: .gitignore | union of lines appearing in >= 2 same-family repos | 20 repos, n/a | measured lines, see scan/patterns.json |
| python-cli: README sections | top measured headings (installation, usage, features, contributing, license) | 5 repos, n/a | measured lines, see scan/patterns.json |
| ts-lib: test suite | emitted always; runner is stdlib | 2 repos, 25.0% | `affaan-m/ECC`, `DietrichGebert/ponytail`, `ruvnet/ruflo` |
| ts-lib: CI workflow | emitted if adoption >= 50% | 6 repos, 75.0% | `affaan-m/ECC`, `DietrichGebert/ponytail`, `ruvnet/ruflo` |
| ts-lib: CONTRIBUTING.md | emitted if adoption >= 40% | 5 repos, 62.5% | `affaan-m/ECC`, `ruvnet/ruflo`, `tashfeenahmed/freellmapi` |
| ts-lib: layout | src/ if src_layout adoption >= 50%, else flat | 2 repos, 25.0% | `affaan-m/ECC`, `vercel-labs/skills`, `Renhuai123/ziwei-doushu` |
| ts-lib: .gitignore | union of lines appearing in >= 2 same-family repos | 20 repos, n/a | measured lines, see scan/patterns.json |
| ts-lib: README sections | top measured headings (installation, usage, features, contributing, license) | 5 repos, n/a | measured lines, see scan/patterns.json |
| ts-cli: test suite | emitted always; runner is stdlib | 5 repos, 100.0% | `affaan-m/ECC`, `DietrichGebert/ponytail`, `ruvnet/ruflo` |
| ts-cli: CI workflow | emitted if adoption >= 50% | 5 repos, 100.0% | `affaan-m/ECC`, `DietrichGebert/ponytail`, `ruvnet/ruflo` |
| ts-cli: CONTRIBUTING.md | emitted if adoption >= 40% | 3 repos, 60.0% | `affaan-m/ECC`, `ruvnet/ruflo`, `tashfeenahmed/freellmapi` |
| ts-cli: layout | src/ if src_layout adoption >= 50%, else flat | 3 repos, 60.0% | `affaan-m/ECC`, `vercel-labs/skills`, `Renhuai123/ziwei-doushu` |
| ts-cli: .gitignore | union of lines appearing in >= 2 same-family repos | 20 repos, n/a | measured lines, see scan/patterns.json |
| ts-cli: README sections | top measured headings (installation, usage, features, contributing, license) | 5 repos, n/a | measured lines, see scan/patterns.json |

## CI action pins

Most commonly pinned major version per action across the scanned workflows:

- `actions/checkout@v4`
- `actions/setup-python@v5`
- `actions/setup-node@v4`

## python build backend

Measured across python-family pyprojects: `{'hatchling': 3, 'setuptools>=61': 2, 'setuptools>=83': 1, 'setuptools': 1, 'pdm-backend': 1}`. Decision: `setuptools`.
