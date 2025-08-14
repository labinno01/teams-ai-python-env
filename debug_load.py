import inspect
import importlib
import sys
import super_replace.core.autonomous_replacer as ar

print("module file:", inspect.getsourcefile(ar))
print("module file (fallback):", getattr(ar, "__file__", None))
print("module repr:", repr(ar))
print("module path in sys.modules:", [k for k in sys.modules.keys() if "autonomous_replacer" in k])

ET = getattr(ar, "EnhancedReplaceTransformer", None)
print("EnhancedReplaceTransformer is", ET)
if ET is not None:
    print("type:", type(ET))
    print("dir(ET):", sorted([n for n in dir(ET) if not n.startswith("__")]))
    # show if _scope_matches_filter exists and where it's defined
    print("_scope_matches_filter in ET.__dict__:", "_scope_matches_filter" in ET.__dict__)
    try:
        src = inspect.getsource(ET)
        print("---- source of EnhancedReplaceTransformer (first 2000 chars) ----")
        print(src[:2000])
    except Exception as e:
        print("cannot get source:", e)
