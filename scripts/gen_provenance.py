#!/usr/bin/env python3
"""Generate provenance.md from measured scan data (never hand-typed numbers).

Each template element maps to: measured adoption, threshold rule, and example
trending repos that exhibit the pattern. Re-run after any scan refresh.
"""
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "src"))

from patternplate import data, templates  # noqa: E402


def main():
    meta = data.snapshot_meta()
    lines = [
        "# provenance",
        "",
        "Every emitted element is justified by measured adoption across the",
        f"top-100 weekly trending scan ({meta['fetched_at'][:10]}, pool "
        f"{meta['pool']} repos, {len(data.load_features())} after licensing/"
        "age filters).",
        "",
        "| element | rule | measured adoption | example trending repos |",
        "|---|---|---|---|",
    ]
    for kind in templates.KINDS:
        stats = data.kind_stats()[kind]
        rows = [
            (f"{kind}: test suite", "emitted always; runner is stdlib",
             stats["tests_dir"], data.examples_for(kind, lambda f: f.get("tests_dir"))),
            (f"{kind}: CI workflow", "emitted if adoption >= 50%",
             stats["ci"], data.examples_for(kind, lambda f: f.get("ci_workflows", 0) > 0)),
            (f"{kind}: CONTRIBUTING.md", "emitted if adoption >= 40%",
             stats["contributing"], data.examples_for(kind, lambda f: f.get("contributing"))),
            (f"{kind}: layout", "src/ if src_layout adoption >= 50%, else flat",
             stats["src_layout"], data.examples_for(kind, lambda f: f.get("src_layout"))),
            (f"{kind}: .gitignore", "union of lines appearing in >= 2 same-family repos",
             {"count": len(data.gitignore_lines(kind)),
              "pct": "n/a"}, []),
            (f"{kind}: README sections", "top measured headings "
             "(installation, usage, features, contributing, license)",
             {"count": 5, "pct": "n/a"}, []),
        ]
        for name, rule, adopt, examples in rows:
            ex = ", ".join(f"`{r}`" for r in examples) if examples else "measured lines, see scan/patterns.json"
            pct = adopt["pct"]
            pct_s = f"{pct}%" if isinstance(pct, (int, float)) else pct
            lines.append(f"| {name} | {rule} | {adopt['count']} repos, {pct_s} | {ex} |")
    acts = data.ci_actions()
    lines += [
        "",
        "## CI action pins",
        "",
        "Most commonly pinned major version per action across the scanned "
        "workflows:",
        "",
    ]
    for k in ("actions/checkout", "actions/setup-python", "actions/setup-node"):
        if k in acts:
            lines.append(f"- `{acts[k]}`")
    bb = data.load_patterns().get("build_backends", {})
    lines += ["", "## python build backend", "",
              f"Measured across python-family pyprojects: `{bb}`. "
              f"Decision: `{data.python_backend()}`.", ""]
    with open(os.path.join(ROOT, "provenance.md"), "w") as fh:
        fh.write("\n".join(lines))
    print(f"provenance.md written ({len(lines)} lines)")


if __name__ == "__main__":
    main()
