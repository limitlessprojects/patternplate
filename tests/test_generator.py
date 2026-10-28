import io
import json
import os
import re
import sys
import tempfile
import unittest
from contextlib import redirect_stdout

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "src"))

from patternplate import cli, data, templates  # noqa: E402


def run(argv):
    buf = io.StringIO()
    with redirect_stdout(buf):
        code = cli.main(argv)
    return code, buf.getvalue()


class TestKinds(unittest.TestCase):
    def test_lists_all_kinds_with_measured_counts(self):
        code, out = run(["kinds"])
        self.assertEqual(code, 0)
        for kind in templates.KINDS:
            self.assertIn(kind, out)
        stats = data.kind_stats()
        for kind in templates.KINDS:
            self.assertGreater(stats[kind]["count"], 0)
        total = sum(s["count"] for s in stats.values())
        fam_repos = {r["repo"] for r in data.load_repos()
                     if r["lang"] in data.LANG_TO_FAMILY}
        self.assertEqual(total, len(fam_repos & set(data.load_features())))


class TestNew(unittest.TestCase):
    def _gen(self, kind, name="demo"):
        return templates.build(kind, name, author="Tester")

    def test_expected_core_files(self):
        for kind in templates.KINDS:
            files = self._gen(kind)
            for rel in ("README.md", "LICENSE", ".gitignore"):
                self.assertIn(rel, files, f"{kind} missing {rel}")
            if kind.startswith("python"):
                self.assertIn("pyproject.toml", files)
                self.assertIn("tests/test_smoke.py", files)
            else:
                self.assertIn("package.json", files)
                self.assertIn("test/smoke.test.js", files)

    def test_python_cli_entry_point(self):
        files = self._gen("python-cli", "mytool")
        self.assertIn("[project.scripts]", files["pyproject.toml"])
        self.assertIn("mytool = ", files["pyproject.toml"])
        cli_paths = [k for k in files if k.endswith("/cli.py")]
        self.assertTrue(cli_paths, "cli.py missing")
        self.assertIn("def main(", files[cli_paths[0]])

    def test_ts_cli_bin(self):
        files = self._gen("ts-cli", "mytool")
        pkg = json.loads(files["package.json"])
        self.assertIn("bin", pkg)
        self.assertEqual(pkg["bin"]["mytool"], "src/cli.js")

    def test_pyproject_parses_and_smoke_test_imports_module(self):
        files = self._gen("python-lib", "mylib")
        mod = templates.py_module_name("mylib")
        self.assertIn(f"import {mod}", files["tests/test_smoke.py"])
        self.assertIn('name = "mylib"', files["pyproject.toml"])

    def test_no_placeholder_tokens(self):
        banned = re.compile(r"TODO|FIXME|XXX|PLACEHOLDER|<your", re.I)
        for kind in templates.KINDS:
            for rel, content in self._gen(kind, "cleanname").items():
                self.assertIsNone(banned.search(content),
                                  f"placeholder found in {kind}/{rel}")

    def test_gitignore_lines_are_measured(self):
        for kind in templates.KINDS:
            files = self._gen(kind)
            measured = set(data.gitignore_lines(kind))
            emitted = set(files[".gitignore"].strip().splitlines())
            self.assertTrue(emitted.issubset(measured),
                            f"{kind}: {emitted - measured} not measured")

    def test_ci_actions_are_measured(self):
        measured = set(data.ci_actions().values())
        for kind in templates.KINDS:
            files = self._gen(kind)
            wf = files.get(".github/workflows/ci.yml")
            if not wf:
                continue
            uses = re.findall(r"uses:\s*(\S+)", wf)
            for u in uses:
                self.assertIn(u, measured, f"{kind}: {u} not a measured action")

    def test_overwrite_guard(self):
        with tempfile.TemporaryDirectory() as tmp:
            code, _ = run(["new", "python-lib", "guarded", "--path", tmp,
                           "--author", "T"])
            self.assertEqual(code, 0)
            code, _ = run(["new", "python-lib", "guarded", "--path", tmp])
            self.assertEqual(code, 2)
            code, _ = run(["new", "python-lib", "guarded", "--path", tmp,
                           "--force"])
            self.assertEqual(code, 0)

    def test_generated_python_test_actually_passes(self):
        """The scaffold's own smoke test must pass: run it in a subprocess."""
        import subprocess
        with tempfile.TemporaryDirectory() as tmp:
            code, out = run(["new", "python-lib", "runme", "--path", tmp,
                             "--author", "T"])
            self.assertEqual(code, 0)
            root = os.path.join(tmp, "runme")
            env = dict(os.environ)
            env["PYTHONPATH"] = os.path.join(ROOT, "src")
            r = subprocess.run(
                [sys.executable, "-m", "unittest", "discover", "-s", "tests",
                 "-p", "test_*.py"],
                cwd=root, env=env, capture_output=True, text=True)
            self.assertEqual(r.returncode, 0, r.stderr)


class TestWhy(unittest.TestCase):
    def test_matches_patterns_data(self):
        code, out = run(["why", "python-lib", "--json"])
        self.assertEqual(code, 0)
        got = json.loads(out)
        stats = data.kind_stats()["python-lib"]
        self.assertEqual(got["measured"]["tests_dir"], stats["tests_dir"])
        self.assertEqual(got["measured"]["ci"], stats["ci"])
        self.assertTrue(got["elements"]["tests_dir"]["examples"])
        measured_actions = set(data.ci_actions().values())
        for a in got["elements"]["ci_workflow"]["actions"].values():
            if a:
                self.assertIn(a, measured_actions)


class TestStatsConsistency(unittest.TestCase):
    def test_check_stats_script_passes(self):
        import subprocess
        r = subprocess.run([sys.executable,
                            os.path.join(ROOT, "scripts", "check_stats.py")],
                           capture_output=True, text=True)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)


if __name__ == "__main__":
    unittest.main()
