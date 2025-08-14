# run_nonlocal_case.py (version simplifiée et normalisée)
import sys
import os
import difflib
import ast

# Ajoute le répertoire du script à modifier dans le path
sys.path.insert(0, os.path.abspath('super_replace/src/super_replace/core'))

from autonomous_replacer import super_replace_autonomous

SOURCE = """
def outer():
    x = 0
    def inner():
        nonlocal x
        x += 1
        return x
    return inner()
"""

EXPECTED = """
def outer():
    counter = 0
    def inner():
        nonlocal counter
        counter += 1
        return counter
    return inner()
"""

def normalize_code(code: str) -> str:
    return ast.unparse(ast.parse(code)).strip()

def _pretty_diff(a: str, b: str) -> str:
    return "".join(difflib.unified_diff(
        a.splitlines(keepends=True),
        b.splitlines(keepends=True),
        fromfile="got",
        tofile="expected",
    ))

def main():
    print("[debug] Appel direct de super_replace_autonomous avec context_rules={'scope': 'nonlocal', 'functions': ['inner']}")

    # Appel direct avec la bonne signature
    got = super_replace_autonomous(
        code=SOURCE,
        target="x",
        replacement="counter",
        context_rules={"scope": "nonlocal", "functions": ["inner"]}
    )

    if got is None:
        raise RuntimeError("super_replace_autonomous a retourné None.")

    print("===== Résultat =====")
    print(got)
    print("====================")

    try:
        assert normalize_code(got) == normalize_code(EXPECTED)
        print("OK: Le remplacement est correct.")
    except AssertionError:
        print("ERREUR: Le résultat ne correspond pas à l'attendu.")
        print(_pretty_diff(normalize_code(got), normalize_code(EXPECTED)))
        raise

if __name__ == "__main__":
    main()