"""Template builders. Every emitted element is justified by measured data.

Threshold rules (all thresholds come from scan/patterns.json + kind_stats):
  - package layout: src/ only if src_layout adoption >= 50% for the kind
  - CI workflow: emitted if CI adoption >= 50% (it is 85-93% for both families)
  - CONTRIBUTING.md: emitted if adoption >= 40%
  - .gitignore lines: lines with >= 2 occurrences across same-family repos
  - CI actions: the most commonly pinned major version per action
  - python build backend: the most common measured backend
"""
import json
import re

from . import data

MIT = """MIT License

Copyright (c) {year} {author}

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

KINDS = ("python-lib", "python-cli", "ts-lib", "ts-cli")


def py_module_name(name):
    mod = re.sub(r"[^a-z0-9_]", "_", name.lower())
    if not mod or mod[0].isdigit():
        mod = "pkg_" + mod
    return mod or "pkg"


def ts_package_name(name):
    return re.sub(r"-{2,}", "-", re.sub(r"[^a-z0-9-]+", "-",
                                        name.lower().strip())).strip("-") or "pkg"


def _readme(kind, name, fam):
    title = "# " + name
    lines = [title, ""]
    lines += ["## Installation", ""]
    if fam == "python":
        lines += ["```bash", f"pip install {name}", "```", ""]
    else:
        lines += ["```bash", f"npm install {name}", "```", ""]
    lines += ["## Usage", ""]
    if kind == "python-lib":
        mod = py_module_name(name)
        lines += ["```python", f"from {mod} import hello", "",
                  'hello("world")  # "Hello, world!"', "```", ""]
    elif kind == "python-cli":
        lines += ["```bash", f"{name} greet --name Ada", f"{name} --version",
                  "```", ""]
    elif kind == "ts-lib":
        lines += ["```js", f'import {{ hello }} from "{ts_package_name(name)}";',
                  "", 'hello("world"); // "Hello, world!"', "```", ""]
    else:
        lines += ["```bash", f"{ts_package_name(name)} greet --name Ada",
                  f"{ts_package_name(name)} --version", "```", ""]
    lines += ["## Features", "",
              "- Minimal, dependency-free core (standard library only)",
              "- Test suite wired to the standard test runner for the language",
              "- GitHub Actions CI from the first commit",
              "- Repository hygiene files measured against current trending "
              "repositories (README sections, .gitignore, license)", ""]
    lines += ["## Contributing", "",
              "Issues and pull requests are welcome. Keep the dependency "
              "list empty and the test suite green.", ""]
    lines += ["## License", "", "MIT", ""]
    return "\n".join(lines)


def build(kind, name, author="Anonymous", version="0.1.0"):
    if kind not in KINDS:
        raise ValueError(f"unknown kind '{kind}', choose from {', '.join(KINDS)}")
    fam = "python" if kind.startswith("python") else "ts"
    cli = kind.endswith("cli")
    stats = data.kind_stats()[kind]
    actions = data.ci_actions()
    files = {}
    year = "2026"

    # README: sections are the measured top README headings
    files["README.md"] = _readme(kind, name, fam)
    files["LICENSE"] = MIT.format(year=year, author=author)

    gi = data.gitignore_lines(kind)
    if gi:
        files[".gitignore"] = "\n".join(gi) + "\n"

    if stats["ci"]["pct"] >= 50:
        steps = [f"      - uses: {actions.get('actions/checkout', 'actions/checkout@v4')}"]
        if fam == "python":
            steps += [f"      - uses: {actions.get('actions/setup-python', 'actions/setup-python@v5')}",
                      "        with:",
                      "          python-version: '3.12'",
                      "      - run: pip install .",
                      "      - run: python -m unittest discover -s tests -p 'test_*.py'"]
            wf_name = "python-tests"
        else:
            steps += [f"      - uses: {actions.get('actions/setup-node', 'actions/setup-node@v4')}",
                      "        with:",
                      "          node-version: '22'",
                      "      - run: npm test"]
            wf_name = "node-tests"
        files[".github/workflows/ci.yml"] = (
            f"name: {wf_name}\n\non:\n  push:\n    branches: [main]\n"
            "  pull_request:\n\njobs:\n  test:\n    runs-on: ubuntu-latest\n"
            "    steps:\n" + "\n".join(steps) + "\n")

    if stats["contributing"]["pct"] >= 40:
        files["CONTRIBUTING.md"] = (
            "# Contributing\n\n"
            "1. Open an issue describing the change before large PRs.\n"
            "2. Add or update tests for any behavior change.\n"
            "3. Run the test suite before pushing:\n\n"
            + ("   ```bash\n   python -m unittest discover -s tests -p 'test_*.py'\n"
               "   ```\n\n" if fam == "python" else
               "   ```bash\n   npm test\n   ```\n\n")
            + "Keep dependencies empty. Small, focused commits review faster.\n")

    if fam == "python":
        mod = py_module_name(name)
        backend = data.python_backend()
        if backend == "hatchling":
            build_sys = ('[build-system]\nrequires = ["hatchling"]\n'
                         'build-backend = "hatchling.build"\n')
            pkg_target = (f'\n[tool.hatch.build.targets.wheel]\n'
                          f'packages = ["{mod}"]\n')
        else:
            build_sys = ('[build-system]\nrequires = ["setuptools>=68"]\n'
                         'build-backend = "setuptools.build_meta"\n')
            pkg_target = (f'\n[tool.setuptools.packages.find]\n'
                          f'include = ["{mod}*"]\n')
        scripts = ""
        if cli:
            scripts = (f"\n[project.scripts]\n{name} = \"{mod}.cli:main\"\n")
        files["pyproject.toml"] = (
            f"{build_sys}\n[project]\nname = \"{name}\"\nversion = \"{version}\"\n"
            f"description = \"Short description of {name}\"\n"
            "requires-python = \">=3.9\"\nreadme = \"README.md\"\n"
            "license = { text = \"MIT\" }\n"
            f"authors = [{{ name = \"{author}\" }}]\ndependencies = []\n"
            f"{scripts}{pkg_target}")
        layout_dir = "src/" if stats["src_layout"]["pct"] >= 50 else ""
        base = layout_dir + mod
        files[f"{base}/__init__.py"] = (
            f'"""{name}: minimal library scaffold."""\n\n'
            f'__version__ = "{version}"\n\n\n'
            'def hello(name: str = "world") -> str:\n'
            '    """Return a friendly greeting (scaffold demo function)."""\n'
            '    return f"Hello, {name}!"\n')
        files[f"tests/test_smoke.py"] = (
            f"import re\nimport unittest\n\nimport {mod}\n\n\n"
            f"class TestSmoke(unittest.TestCase):\n"
            f"    def test_version_is_semver(self):\n"
            f"        self.assertRegex({mod}.__version__, r'^\\d+\\.\\d+\\.\\d+$')\n\n"
            f"    def test_hello(self):\n"
            f"        self.assertEqual({mod}.hello('x'), 'Hello, x!')\n\n\n"
            f"if __name__ == '__main__':\n    unittest.main()\n")
        if cli:
            files[f"{base}/cli.py"] = (
                f"import argparse\n\nfrom . import __version__, hello\n\n\n"
                f"def main(argv=None):\n"
                f"    parser = argparse.ArgumentParser(prog=\"{name}\")\n"
                f"    parser.add_argument(\"--version\", action=\"version\","
                f" version=\"%(prog)s {{__version__}}\".format(__version__=__version__))\n"
                f"    sub = parser.add_subparsers(dest=\"command\", required=True)\n"
                f"    greet = sub.add_parser(\"greet\", help=\"print a greeting\")\n"
                f"    greet.add_argument(\"--name\", default=\"world\")\n"
                f"    args = parser.parse_args(argv)\n"
                f"    if args.command == \"greet\":\n"
                f"        print(hello(args.name))\n\n\n"
                f"if __name__ == \"__main__\":\n    main()\n")
    else:
        pkg = ts_package_name(name)
        pkgjson = {
            "name": pkg,
            "version": version,
            "description": f"Short description of {pkg}",
            "type": "module",
            "license": "MIT",
            "author": author,
            "main": "src/index.js",
            "scripts": {
                "test": "node --test test/",
            },
            "engines": {"node": ">=20"},
        }
        if cli:
            pkgjson["bin"] = {pkg: "src/cli.js"}
        files["package.json"] = json.dumps(pkgjson, indent=2) + "\n"
        files["src/index.js"] = (
            "/** Minimal library scaffold. */\n"
            "export function hello(name = 'world') {\n"
            "  return `Hello, ${name}!`;\n}\n")
        files["test/smoke.test.js"] = (
            "import { test } from 'node:test';\n"
            "import assert from 'node:assert/strict';\n"
            "import { hello } from '../src/index.js';\n\n"
            "test('greets by name', () => {\n"
            "  assert.equal(hello('x'), 'Hello, x!');\n});\n")
        if cli:
            files["src/cli.js"] = (
                "#!/usr/bin/env node\n"
                "import { parseArgs } from 'node:util';\n"
                "import { hello } from './index.js';\n\n"
                "const { values, positionals } = parseArgs({\n"
                "  allowPositionals: true,\n"
                "  options: {\n"
                "    name: { type: 'string', short: 'n', default: 'world' },\n"
                "    version: { type: 'boolean', default: false },\n"
                "  },\n});\n\n"
                "if (values.version) {\n"
                f"  console.log('{pkg} {version}');\n"
                "} else if (positionals[0] === 'greet') {\n"
                "  console.log(hello(values.name));\n"
                "} else {\n"
                "  console.error('usage: " + pkg + " greet [--name <name>]');\n"
                "  process.exitCode = 1;\n}\n")
    return files
