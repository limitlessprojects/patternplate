"""patternplate CLI: kinds / new / why. Offline, stdlib only."""
import argparse
import json
import os
import sys

from . import __version__, data, templates


def cmd_kinds(args):
    stats = data.kind_stats()
    total = sum(s["count"] for s in stats.values())
    print(f"{'kind':12s} {'repos':>5s} {'share':>6s} {'tests%':>7s} {'ci%':>5s}")
    for kind in templates.KINDS:
        s = stats.get(kind)
        if not s:
            continue
        print(f"{kind:12s} {s['count']:5d} {s['share_pct']:5.1f}% "
              f"{s['tests_dir']['pct']:7.1f} {s['ci']['pct']:5.1f}")
    print(f"measured total: {total} repos "
          f"(snapshot {data.snapshot_meta()['fetched_at'][:10]})")
    return 0


def cmd_new(args):
    files = templates.build(args.kind, args.name, author=args.author)
    target = os.path.abspath(args.path)
    root = os.path.join(target, args.name)
    if os.path.exists(root) and os.listdir(root) and not args.force:
        print(f"refusing to overwrite non-empty {root} (use --force)",
              file=sys.stderr)
        return 2
    for rel, content in sorted(files.items()):
        path = os.path.join(root, rel)
        os.makedirs(os.path.dirname(path) or root, exist_ok=True)
        with open(path, "w") as fh:
            fh.write(content)
    n = len(files)
    print(f"created {n} files in {root}")
    print("next: git init && git add -A && git commit -m 'scaffold'")
    return 0


def cmd_why(args):
    kind = args.kind
    stats = data.kind_stats()[kind]
    actions = data.ci_actions()
    out = {
        "snapshot": data.snapshot_meta(),
        "kind": kind,
        "measured": stats,
        "elements": {
            "tests_dir": {
                "adoption": stats["tests_dir"],
                "examples": data.examples_for(kind, lambda f: f.get("tests_dir")),
            },
            "ci_workflow": {
                "adoption": stats["ci"],
                "examples": data.examples_for(
                    kind, lambda f: f.get("ci_workflows", 0) > 0),
                "actions": {
                    "checkout": actions.get("actions/checkout", "actions/checkout@v4"),
                    "setup": (actions.get("actions/setup-python")
                              if kind.startswith("python")
                              else actions.get("actions/setup-node")),
                },
            },
            "gitignore": {
                "lines": data.gitignore_lines(kind),
                "rule": "lines appearing in >= 2 same-family trending repos",
            },
            "layout": {
                "src_layout_adoption": stats["src_layout"],
                "decision": "src/ layout" if stats["src_layout"]["pct"] >= 50
                            else "flat package layout",
            },
        },
    }
    if kind.startswith("python"):
        out["elements"]["build_backend"] = {
            "measured": data.load_patterns().get("build_backends", {}),
            "decision": data.python_backend(),
        }
    if args.json:
        print(json.dumps(out, indent=2))
    else:
        print(f"kind: {kind}  (measured on {stats['count']} repos, "
              f"{stats['share_pct']}% of the licensed trending set)")
        for k, v in out["elements"].items():
            if k == "gitignore":
                print(f"  {k}: {len(v['lines'])} lines, {v['rule']}")
            elif k == "ci_workflow":
                print(f"  {k}: {v['adoption']['pct']}% adoption; "
                      f"e.g. {v['actions']['checkout']}")
            elif k == "layout":
                print(f"  {k}: {v['decision']} (src_layout {v['src_layout_adoption']['pct']}%)")
            elif k == "build_backend":
                print(f"  {k}: {v['decision']} (measured {v['measured']})")
            else:
                print(f"  {k}: {v['adoption']['pct']}% adoption; "
                      f"examples: {', '.join(v['examples'])}")
    return 0


def main(argv=None):
    parser = argparse.ArgumentParser(
        prog="patternplate",
        description="Offline boilerplate generator backed by measured "
                    "patterns from the top 100 weekly trending GitHub repos")
    parser.add_argument("--version", action="version",
                        version=f"%(prog)s {__version__}")
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("kinds", help="list measured archetypes and adoption")

    p_new = sub.add_parser("new", help="scaffold a new project")
    p_new.add_argument("kind", choices=templates.KINDS)
    p_new.add_argument("name")
    p_new.add_argument("--path", default=".")
    p_new.add_argument("--author", default="Anonymous")
    p_new.add_argument("--force", action="store_true")

    p_why = sub.add_parser("why")
    p_why.add_argument("kind", choices=templates.KINDS)
    p_why.add_argument("--json", action="store_true")

    args = parser.parse_args(argv)
    if args.command == "kinds":
        return cmd_kinds(args)
    if args.command == "new":
        return cmd_new(args)
    return cmd_why(args)


if __name__ == "__main__":
    sys.exit(main())
