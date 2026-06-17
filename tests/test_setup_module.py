"""Guards for the start-anywhere bootstrap (setup_module.py).

Proves, for every module N: the manifest names real symbols, the generated
my_agent imports cleanly, the build targets are genuinely stubbed (raise
NotImplementedError), and the reference src/agent fills every stub (so the
answer key always fits the blanks). Needs git tags module-1..8 (present in CI).
"""
import ast
import importlib.util
import os
import subprocess
import sys
import tempfile

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

# Load setup_module.py. NB: bind it to `sm`, not `setup_module` — pytest treats a
# module-level name `setup_module` as its xunit setup hook and would try to call it.
_spec = importlib.util.spec_from_file_location("agent_setup_cli", os.path.join(ROOT, "setup_module.py"))
sm = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(sm)
MODULES = sorted(sm.BUILD_TARGETS)


def _func_qualnames(src):
    tree = ast.parse(src)
    names = set()

    def walk(node, prefix):
        for c in node.body:
            if isinstance(c, (ast.FunctionDef, ast.AsyncFunctionDef)):
                names.add(prefix + c.name)
                names.add(c.name)
            elif isinstance(c, ast.ClassDef):
                walk(c, prefix + c.name + ".")

    walk(tree, "")
    return names


def test_manifest_symbols_exist_in_their_tag():
    for n in MODULES:
        for path, symbols in sm.BUILD_TARGETS[n].items():
            present = _func_qualnames(sm.tag_show(f"module-{n}", path))
            missing = [s for s in symbols if s not in present]
            assert not missing, f"module {n}: {path} missing {missing}"


def test_each_module_materializes_and_imports():
    for n in MODULES:
        with tempfile.TemporaryDirectory() as d:
            dest = os.path.join(d, "my_agent")
            sm.build(n, dest)
            r = subprocess.run([sys.executable, "-c", "import agent; agent.__version__"],
                               capture_output=True, text=True,
                               env={**os.environ, "PYTHONPATH": dest})
            assert r.returncode == 0, f"module {n} my_agent failed to import:\n{r.stderr}"


def test_build_targets_are_actually_stubbed():
    for n in MODULES:
        with tempfile.TemporaryDirectory() as d:
            dest = os.path.join(d, "my_agent")
            sm.build(n, dest)
            for path in sm.BUILD_TARGETS[n]:
                out = os.path.join(dest, sm.dest_path(path))
                assert f'raise NotImplementedError("Module {n}' in open(out).read(), \
                    f"module {n}: {path} not stubbed"


def test_reference_fills_every_stub():
    # the HEAD reference must define every blanked symbol, so the answer key fits.
    for n in MODULES:
        for path, symbols in sm.BUILD_TARGETS[n].items():
            ref = os.path.join(ROOT, path)
            if not os.path.exists(ref):
                continue
            present = _func_qualnames(open(ref).read())
            missing = [s for s in symbols if s not in present]
            assert not missing, f"reference {path} missing {missing} (module {n})"
