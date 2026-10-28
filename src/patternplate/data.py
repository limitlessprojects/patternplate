"""Load and query the measured scan data shipped in scan/."""
import csv
import json
import os
from collections import Counter, defaultdict

SCAN_DIR = os.path.join(os.path.dirname(os.path.dirname(
    os.path.dirname(os.path.abspath(__file__)))), "scan")

LANG_TO_FAMILY = {
    "Python": "python", "Jupyter Notebook": "python",
    "TypeScript": "ts", "JavaScript": "ts",
}
FAMILY_FEATURE = {
    "python": {"pkg": "pyproject", "entry": "project.scripts"},
    "ts": {"pkg": "package_json", "entry": "package_json:bin"},
}


def load_patterns():
    with open(os.path.join(SCAN_DIR, "patterns.json")) as fh:
        return json.load(fh)


def load_features():
    with open(os.path.join(SCAN_DIR, "features.json")) as fh:
        return json.load(fh)


def load_repos():
    with open(os.path.join(SCAN_DIR, "repos.csv")) as fh:
        return list(csv.DictReader(fh))


def snapshot_meta():
    with open(os.path.join(SCAN_DIR, "trending_snapshot.json")) as fh:
        d = json.load(fh)
    return {"fetched_at": d["fetched_at_utc"], "method": d["method"],
            "pool": d["pool_size"]}


def kind_stats():
    """Measured per-kind facts: count, share, feature adoption, examples."""
    repos = {r["repo"]: r for r in load_repos() if r["kept"] == "1"}
    feats = load_features()
    kinds = defaultdict(list)
    for repo, f in feats.items():
        meta = repos.get(repo)
        if not meta:
            continue
        fam = LANG_TO_FAMILY.get(meta["lang"])
        if fam is None:
            continue
        cli = f.get("has_cli_hint", False)
        kinds[f"{fam}-cli" if cli else f"{fam}-lib"].append((repo, f, meta))
    out = {}
    total = sum(len(v) for v in kinds.values())
    for kind, members in kinds.items():
        fam = kind.split("-")[0]
        n = len(members)
        def pct(pred):
            c = sum(1 for _, f, _ in members if pred(f))
            return {"count": c, "pct": round(100 * c / n, 1) if n else 0.0}
        out[kind] = {
            "count": n,
            "share_pct": round(100 * n / total, 1) if total else 0.0,
            "tests_dir": pct(lambda f: f.get("tests_dir")),
            "ci": pct(lambda f: f.get("ci_workflows", 0) > 0),
            "src_layout": pct(lambda f: f.get("src_layout")),
            "dockerfile": pct(lambda f: f.get("dockerfile")),
            "env_example": pct(lambda f: f.get("env_example")),
            "contributing": pct(lambda f: f.get("contributing")),
            "docs_dir": pct(lambda f: f.get("docs_dir")),
        }
    return out


def gitignore_lines(kind, min_count=2):
    fam = kind.split("-")[0]
    pats = load_patterns()
    rows = pats["gitignore_top_by_lang"].get(fam, [])
    return [r["line"] for r in rows if r["count"] >= min_count]


def ci_actions():
    """Map action -> most common pinned version, from measured workflows."""
    pats = load_patterns()
    best = {}
    for row in pats["ci_actions_top"]:
        name, _, ver = row["action"].partition("@")
        if not ver or len(ver) > 12 or not ver.startswith("v"):
            continue  # skip sha pins for readability
        if name not in best or row["count"] > best[name][1]:
            best[name] = (row["action"], row["count"])
    return {k: v[0] for k, v in best.items()}


def python_backend():
    backends = load_patterns().get("build_backends", {})
    norm = Counter()
    for name, c in backends.items():
        base = name.split(">")[0].split("=")[0]
        norm[base] += c
    return norm.most_common(1)[0][0] if norm else "setuptools"


def examples_for(kind, pred, limit=3):
    repos = {r["repo"]: r for r in load_repos() if r["kept"] == "1"}
    feats = load_features()
    fam = kind.split("-")[0]
    hits = []
    for repo, f in feats.items():
        meta = repos.get(repo)
        if not meta or LANG_TO_FAMILY.get(meta["lang"]) != fam:
            continue
        if pred(f):
            hits.append((int(meta["stars_total"]), repo))
    hits.sort(reverse=True)
    return [r for _, r in hits[:limit]]
