"""Load a script from a skill folder (the folder names have hyphens).

En este repositorio las once skills viven en `.claude/skills/`, que es donde
Claude Code las descubre como skills del proyecto. Las rutas de abajo son el
unico cambio frente al repositorio original: la suite y los fixtures son los
mismos.
"""

import importlib.util
import os

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ROOT = os.path.join(REPO, ".claude", "skills")
FIX = os.path.join(REPO, "tests", "fixtures")


def load(folder, name):
    path = os.path.join(ROOT, folder, name + ".py")
    spec = importlib.util.spec_from_file_location("trader_" + name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod
