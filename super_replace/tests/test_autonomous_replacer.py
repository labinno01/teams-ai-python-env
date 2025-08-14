import pytest
import ast
from super_replace.core.autonomous_replacer import (
    super_replace_autonomous,
    check_rename_safety,
    get_binding_info,
    ScopeKind,
    ScopeBuilder,
    BindingKey
)

# --- CONFIG ---
# Set to True to enable debug prints from the transformer
DEBUG = True

# Helper to normalize code for comparison (remove extra newlines, etc.)
def normalize_code(code: str) -> str:
    return ast.unparse(ast.parse(code)).strip()


# --- Test cases for super_replace_autonomous (enhanced version) ---

def test_local_variable_replacement():
    code = """
def func():
    x = 1
    print(x)
"""
    expected = """
def func():
    y = 1
    print(y)
"""
    context = {"scope": "local", "functions": ["func"], "debug": DEBUG}
    result = super_replace_autonomous(code, "x", "y", context)
    assert normalize_code(result) == normalize_code(expected)

def test_global_variable_replacement():
    code = """
x = 1
def func():
    global x
    print(x)
"""
    expected = """
y = 1
def func():
    global y
    print(y)
"""
    context = {"scope": "global", "debug": DEBUG}
    result = super_replace_autonomous(code, "x", "y", context)
    assert normalize_code(result) == normalize_code(expected)

def test_nonlocal_variable_replacement():
    code = """
def outer():
    x = 1
    def inner():
        nonlocal x
        x = 2
        print(x)
"""
    expected = """
def outer():
    y = 1
    def inner():
        nonlocal y
        y = 2
        print(y)
"""
    context = {"scope": "nonlocal", "functions": ["inner"], "debug": DEBUG}
    result = super_replace_autonomous(code, "x", "y", context)
    assert normalize_code(result) == normalize_code(expected)

def test_class_attribute_replacement():
    code = """
class MyClass:
    def __init__(self):
        self.x = 1
    def method(self):
        print(self.x)
"""
    expected = code
    context = {"scope": "class", "debug": DEBUG}
    result = super_replace_autonomous(code, "x", "y", context)
    assert normalize_code(result) == normalize_code(expected)

def test_no_replacement_outside_scope():
    code = """
x = 1
def func():
    y = 1
    print(y)
"""
    expected = code
    context = {"scope": "local", "functions": ["func"], "debug": DEBUG}
    result = super_replace_autonomous(code, "x", "z", context)
    assert normalize_code(result) == normalize_code(expected)

def test_multiple_occurrences_in_scope():
    code = """
def func():
    a = 1
    b = a + 2
    print(a)
"""
    expected = """
def func():
    x = 1
    b = x + 2
    print(x)
"""
    context = {"scope": "local", "functions": ["func"], "debug": DEBUG}
    result = super_replace_autonomous(code, "a", "x", context)
    assert normalize_code(result) == normalize_code(expected)

def test_different_names_not_replaced():
    code = """
def func():
    x = 1
    y = 2
    print(x)
"""
    expected = code
    context = {"scope": "local", "functions": ["func"], "debug": DEBUG}
    result = super_replace_autonomous(code, "z", "a", context)
    assert normalize_code(result) == normalize_code(expected)


# --- Test cases for check_rename_safety --- #

def test_rename_safety_no_conflict():
    code = """
def func():
    my_var = 1
    print(my_var)
"""
    is_safe, issues = check_rename_safety(code, "my_var", "new_var", {"scope": "local"})
    assert is_safe is True
    assert not issues

def test_rename_safety_keyword_conflict():
    code = """
def func():
    my_var = 1
    print(my_var)
"""
    is_safe, issues = check_rename_safety(code, "my_var", "class", {"scope": "local"})
    assert is_safe is False
    assert "'class' is a Python keyword" in issues

def test_rename_safety_builtin_conflict():
    code = """
def func():
    my_var = 1
    print(my_var)
"""
    is_safe, issues = check_rename_safety(code, "my_var", "len", {"scope": "local"})
    assert is_safe is False
    assert "'len' shadows a builtin name" in issues

def test_rename_safety_existing_name_conflict():
    code = """
def func():
    old_name = 1
    new_name = 2
    print(old_name)
"""
    is_safe, issues = check_rename_safety(code, "old_name", "new_name", {"scope": "local"})
    assert is_safe is False
    assert any("Name 'new_name' already exists" in issue for issue in issues)


# --- Test cases for get_binding_info --- #

def test_get_binding_info_local():
    code = """
def func():
    x = 1
    print(x)
"""
    info = get_binding_info(code, "x")
    assert len(info['bindings']) == 1
    binding = info['bindings'][0]
    assert binding['scope_kind'] == ScopeKind.FUNCTION.name
    assert binding['scope_name'] == "func"
    assert binding['uses'] == 1
    assert binding['definitions'] == 1
    assert info['total_uses'] == 1
    assert info['total_definitions'] == 1

def test_get_binding_info_global():
    code = """
x = 1
def func():
    global x
    print(x)
"""
    info = get_binding_info(code, "x")
    assert len(info['bindings']) == 1
    binding = info['bindings'][0]
    assert binding['scope_kind'] == ScopeKind.MODULE.name
    assert binding['scope_name'] == "module"
    assert binding['uses'] == 1 # One use in print(x)
    assert binding['definitions'] == 1 # One definition x = 1
    assert info['total_uses'] == 1
    assert info['total_definitions'] == 1

def test_get_binding_info_nonlocal():
    code = """
def outer():
    x = 1
    def inner():
        nonlocal x
        x = 2
        print(x)
"""
    info = get_binding_info(code, "x")
    assert len(info['bindings']) == 1 # Only one binding for x (in outer)
    binding = info['bindings'][0]
    assert binding['scope_kind'] == ScopeKind.FUNCTION.name
    assert binding['scope_name'] == "outer"
    assert binding['uses'] == 2 # x = 2 and print(x)
    assert binding['definitions'] == 1 # x = 1
    assert info['total_uses'] == 2
    assert info['total_definitions'] == 1


# --- Specific regression tests for nonlocal/global issues ---

def test_inner_nonlocal_reference_not_replaced_as_local():
    code = """
def outer():
    x = 1
    def inner():
        nonlocal x
        x = 2
        return x
    return inner
"""
    expected = code
    context = {"scope": "local", "functions": ["inner"], "debug": DEBUG}
    result = super_replace_autonomous(code, "x", "y", context)
    assert normalize_code(result) == normalize_code(expected)

def test_replace_nonlocal_defining_scope():
    code = """
def outer():
    x = 1
    def inner():
        nonlocal x
        x = 2
        return x
    return inner
"""
    expected = """
def outer():
    y = 1
    def inner():
        nonlocal y
        y = 2
        return y
    return inner
"""
    builder = ScopeBuilder()
    tree = ast.parse(code)
    builder.visit(tree)
    outer_scope_id = -1
    for scope in builder.index.scopes:
        if scope.kind == ScopeKind.FUNCTION and scope.name == "outer":
            outer_scope_id = scope.id
            break
    assert outer_scope_id != -1, "Outer scope not found"
    target_binding_key = BindingKey(outer_scope_id, "x")
    context = {"scope": "nonlocal", "target_binding_key": target_binding_key, "debug": DEBUG}
    result = super_replace_autonomous(code, "x", "y", context)
    assert normalize_code(result) == normalize_code(expected)

def test_global_variable_not_replaced_as_local():
    code = """
global_var = 1
def func():
    print(global_var)
"""
    expected = code
    context = {"scope": "local", "functions": ["func"], "debug": DEBUG}
    result = super_replace_autonomous(code, "global_var", "new_global_var", context)
    assert normalize_code(result) == normalize_code(expected)

def test_global_variable_replaced_as_global():
    code = """
global_var = 1
def func():
    global global_var
    print(global_var)
"""
    expected = """
new_global_var = 1
def func():
    global new_global_var
    print(new_global_var)
"""
    context = {"scope": "global", "debug": DEBUG}
    result = super_replace_autonomous(code, "global_var", "new_global_var", context)
    assert normalize_code(result) == normalize_code(expected)

def test_nonlocal_variable_replaced_as_nonlocal_scope():
    code = """
def outer():
    x = 1
    def inner():
        nonlocal x
        x = 2
        return x
    return inner
"""
    expected = """
def outer():
    y = 1
    def inner():
        nonlocal y
        y = 2
        return y
    return inner
"""
    context = {"scope": "nonlocal", "debug": DEBUG}
    result = super_replace_autonomous(code, "x", "y", context)
    assert normalize_code(result) == normalize_code(expected)

def test_local_variable_shadowing_global():
    code = """
x = 10 # global x
def func():
    x = 1 # local x
    print(x)
"""
    expected = """
x = 10 # global x
def func():
    y = 1 # local y
    print(y)
"""
    context = {"scope": "local", "functions": ["func"], "debug": DEBUG}
    result = super_replace_autonomous(code, "x", "y", context)
    assert normalize_code(result) == normalize_code(expected)

def test_global_variable_shadowed_by_local_not_replaced_as_global():
    code = """
x = 10 # global x
def func():
    x = 1 # local x
    print(x)
"""
    expected = code
    context = {"scope": "global", "debug": DEBUG}
    result = super_replace_autonomous(code, "x", "y", context)
    assert normalize_code(result) == normalize_code(expected)

def test_comprehension_scope():
    code = """
items = [1, 2, 3]
result = [x * 2 for x in items if x > 1]
"""
    expected = """
items = [1, 2, 3]
result = [y * 2 for y in items if y > 1]
"""
    context = {"scope": "local", "debug": DEBUG}
    result = super_replace_autonomous(code, "x", "y", context)
    assert normalize_code(result) == normalize_code(expected)

def test_lambda_scope():
    code = """
def apply_func(f, val):
    return f(val)

my_lambda = lambda x: x * 2
result = apply_func(my_lambda, 5)
"""
    expected = """
def apply_func(f, val):
    return f(val)

my_lambda = lambda y: y * 2
result = apply_func(my_lambda, 5)
"""
    context = {"scope": "local", "debug": DEBUG}
    result = super_replace_autonomous(code, "x", "y", context)
    assert normalize_code(result) == normalize_code(expected)
