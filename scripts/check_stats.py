#!/usr/bin/env python3
"""Verify scan/patterns.json matches an independent recomputation from
scan/features.json. Exits nonzero on any drift. Used by `make verify`."""
import json
import os
import sys
from collections import Counter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCAN = os.path.join(ROOT, "scan")

BOOL_FEATS = ["readme", "license_file", "tests_dir", "makefile", "justfile",
              "dockerfile", "compose", "docs_dir", "examples_dir",
              "contributing", "changelog", "precommit", "env_example",
              "src_layout", "has_app_dir", "has_cli_hint"]


def main():
    feats = json.load(open(os.path.join(SCAN, "features.json")))
    pats = json.load(open(os.path.join(SCAN, "patterns.json")))
    errs = []

    n = len(feats)
    if pats["n_repos"] != n:
        errs.append(f"n_repos {pats['n_repos']} != {n}")

    overall = Counter()
    dirs = Counter()
    gi = Counter()
    sections = Counter()
    actions = Counter()
    backends = Counter()
    for f in feats.values():
        for b in BOOL_FEATS:
            if f.get(b):
                overall[b] += 1
        dirs.update(f["top_dirs"])
        gi.update(f["gitignore_lines"])
        sections.update(f["readme_sections"])
        actions.update(f["ci_uses"])
        if f.get("build_backend"):
            backends[f["build_backend"]] += 1

    for b, c in overall.items():
        got = pats["overall"].get(b, {}).get("count")
        if got != c:
            errs.append(f"overall.{b}: patterns={got} recomputed={c}")

    top_dirs = [(d, c) for d, c in dirs.most_common(20)]
    if [(x["dir"], x["count"]) for x in pats["top_dirs"]] != top_dirs:
        errs.append("top_dirs drift")

    top_gi = [(x["line"], x["count"]) for x in pats["gitignore_top"]]
    if top_gi != [(ln, c) for ln, c in gi.most_common(30)]:
        errs.append("gitignore_top drift")

    top_sec = [(x["section"], x["count"]) for x in pats["readme_sections_top"]]
    if top_sec != [(s, c) for s, c in sections.most_common(25)]:
        errs.append("readme_sections_top drift")

    top_act = [(x["action"], x["count"]) for x in pats["ci_actions_top"]]
    if top_act != [(a, c) for a, c in actions.most_common(60)]:
        errs.append("ci_actions_top drift")

    if pats.get("build_backends", {}) != dict(backends):
        errs.append(f"build_backends drift: {pats.get('build_backends')} vs {dict(backends)}")

    if errs:
        print("VERIFY FAILED:")
        for e in errs:
            print(" -", e)
        return 1
    print(f"verify ok: patterns.json consistent with features.json ({n} repos)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
