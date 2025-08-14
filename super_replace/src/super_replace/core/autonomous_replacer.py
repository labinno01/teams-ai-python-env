# Force reload
# autonomous_replacer.py - FINAL VERSION
"""
Module: super_replace_autonomous - FINAL

Key fixes:
1. Correct binding resolution for all scope types (LEGB, class scope).
2. Unified selection logic based on a set of target BindingKeys.
3. Correct handling of function filters to select bindings, not restrict renaming.
4. Robust handling of nonlocal, global, and except handlers.
"""

from __future__ import annotations
import ast
import astor
from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Dict, List, Optional, Set, Any, Union, Iterable


class ScopeKind(Enum):
    MODULE = auto()
    FUNCTION = auto()
    CLASS = auto()
    COMPREHENSION = auto()
    LAMBDA = auto()


@dataclass
class Scope:
    kind: ScopeKind
    parent: Optional["Scope"]
    id: int
    node: Optional[ast.AST] = None
    locals: Dict[str, "Binding"] = field(default_factory=dict)
    globals_decl: Set[str] = field(default_factory=set)
    nonlocals_decl: Set[str] = field(default_factory=set)
    name: str = ""

    def nearest_module(self) -> "Scope":
        s = self
        while s.parent is not None:
            s = s.parent
        return s

    def nearest_function_having(self, name: str) -> Optional["Scope"]:
        s = self.parent
        while s is not None:
            if s.kind in (ScopeKind.FUNCTION, ScopeKind.LAMBDA) and name in s.locals:
                return s
            s = s.parent
        return None

    def resolve_free_lookup_parent(self) -> Optional["Scope"]:
        if self.kind == ScopeKind.CLASS:
            return self.nearest_module()
        return self.parent


@dataclass(frozen=True)
class BindingKey:
    scope_id: int
    name: str


@dataclass
class Binding:
    key: BindingKey
    defining_nodes: List[ast.AST] = field(default_factory=list)
    scope: Optional[Scope] = None


@dataclass
class Index:
    scopes: List[Scope] = field(default_factory=list)
    uses: Dict[BindingKey, List[ast.AST]] = field(default_factory=dict)
    defs: Dict[BindingKey, List[ast.AST]] = field(default_factory=dict)
    except_names: Dict[BindingKey, Set[ast.ExceptHandler]] = field(default_factory=dict)
    global_names: Dict[BindingKey, Set[ast.Global]] = field(default_factory=dict)
    nonlocal_names: Dict[BindingKey, Set[ast.Nonlocal]] = field(default_factory=dict)
    node_to_binding: Dict[ast.AST, BindingKey] = field(default_factory=dict)
    binding_key_to_scope: Dict[BindingKey, Scope] = field(default_factory=dict)


def _collect_targets_from_target(node: ast.AST, collector: Set[str]) -> None:
    if isinstance(node, ast.Name):
        collector.add(node.id)
    elif isinstance(node, (ast.Tuple, ast.List, ast.Set)):
        for elt in node.elts:
            _collect_targets_from_target(elt, collector)
    elif isinstance(node, ast.Starred):
        _collect_targets_from_target(node.value, collector)


class ScopeBuilder(ast.NodeVisitor):
    
    def __init__(self):
        self.index = Index()
        self.scope = self._new_scope(ScopeKind.MODULE, None, "module")

    def _new_scope(self, kind: ScopeKind, parent: Optional[Scope], name: str = "") -> Scope:
        s = Scope(kind=kind, parent=parent, id=len(self.index.scopes), name=name)
        self.index.scopes.append(s)
        return s

    def _enter(self, kind: ScopeKind, name: str = "", node: ast.AST = None) -> Scope:
        self.scope = self._new_scope(kind, self.scope, name)
        self.scope.node = node
        return self.scope

    def _exit(self):
        assert self.scope.parent is not None
        self.scope = self.scope.parent

    def _binding_key_for_assignment(self, name: str) -> BindingKey:
        if name in self.scope.globals_decl:
            owner = self.scope.nearest_module()
        elif name in self.scope.nonlocals_decl:
            owner = self.scope.nearest_function_having(name)
            if owner is None:
                owner = self.scope
        else:
            owner = self.scope
            
        if name not in owner.locals:
            binding = Binding(BindingKey(owner.id, name), scope=owner)
            owner.locals[name] = binding
            self.index.binding_key_to_scope[binding.key] = owner
        return owner.locals[name].key

    def _binding_key_by_lookup(self, name: str) -> Optional[BindingKey]:
        if name in self.scope.globals_decl:
            mod = self.scope.nearest_module()
            if name not in mod.locals:
                mod.locals[name] = Binding(BindingKey(mod.id, name), scope=mod)
                self.index.binding_key_to_scope[mod.locals[name].key] = mod
            return mod.locals[name].key

        if name in self.scope.nonlocals_decl:
            fn = self.scope.nearest_function_having(name)
            if fn is not None and name in fn.locals:
                return fn.locals[name].key
            return None

        if name in self.scope.locals:
            return self.scope.locals[name].key

        if self.scope.kind == ScopeKind.CLASS:
            mod = self.scope.nearest_module()
            return mod.locals[name].key if name in mod.locals else None

        parent = self.scope.resolve_free_lookup_parent()
        while parent is not None:
            if name in parent.locals:
                return parent.locals[name].key
            parent = parent.parent

        return None

    def _record_def(self, key: BindingKey, node: ast.AST):
        self.index.defs.setdefault(key, []).append(node)
        scope = self.index.scopes[key.scope_id]
        if key.name in scope.locals:
            scope.locals[key.name].defining_nodes.append(node)
        self.index.node_to_binding[node] = key

    def _record_use(self, key: BindingKey, node: ast.AST):
        self.index.uses.setdefault(key, []).append(node)
        self.index.node_to_binding[node] = key

    def _record_assignment_targets(self, targets):
        for target in targets:
            for node in ast.walk(target):
                if isinstance(node, ast.Name) and isinstance(node.ctx, ast.Store):
                    key = self._binding_key_for_assignment(node.id)
                    self._record_def(key, node)

    def visit_Global(self, node: ast.Global):
        for name in node.names:
            self.scope.globals_decl.add(name)
            mod = self.scope.nearest_module()
            if name not in mod.locals:
                binding = Binding(BindingKey(mod.id, name), scope=mod)
                mod.locals[name] = binding
                self.index.binding_key_to_scope[binding.key] = mod
            key = mod.locals[name].key
            self.index.global_names.setdefault(key, set()).add(node)
        self.generic_visit(node)

    def visit_Nonlocal(self, node: ast.Nonlocal):
        for name in node.names:
            self.scope.nonlocals_decl.add(name)
            fn = self.scope.nearest_function_having(name)
            if fn and name in fn.locals:
                key = fn.locals[name].key
                self.index.nonlocal_names.setdefault(key, set()).add(node)
        self.generic_visit(node)

    def visit_FunctionDef(self, node: ast.FunctionDef):
        if self.scope.parent is not None:
            key = self._binding_key_for_assignment(node.name)
            self._record_def(key, node)
        self._enter(ScopeKind.FUNCTION, node.name, node)
        for arg in node.args.args + node.args.kwonlyargs:
            if arg.arg:
                key = self._binding_key_for_assignment(arg.arg)
                self._record_def(key, arg)
        if node.args.vararg:
            key = self._binding_key_for_assignment(node.args.vararg.arg)
            self._record_def(key, node.args.vararg)
        if node.args.kwarg:
            key = self._binding_key_for_assignment(node.args.kwarg.arg)
            self._record_def(key, node.args.kwarg)
        self.generic_visit(node)
        self._exit()

    visit_AsyncFunctionDef = visit_FunctionDef

    def visit_ClassDef(self, node: ast.ClassDef):
        if self.scope.parent is not None:
            key = self._binding_key_for_assignment(node.name)
            self._record_def(key, node)
        self._enter(ScopeKind.CLASS, node.name, node)
        self.generic_visit(node)
        self._exit()

    def visit_Lambda(self, node: ast.Lambda):
        self._enter(ScopeKind.LAMBDA, f"@L{node.lineno}", node)
        for arg in node.args.args + node.args.kwonlyargs:
            if arg.arg:
                key = self._binding_key_for_assignment(arg.arg)
                self._record_def(key, arg)
        if node.args.vararg:
            key = self._binding_key_for_assignment(node.args.vararg.arg)
            self._record_def(key, node.args.vararg)
        if node.args.kwarg:
            key = self._binding_key_for_assignment(node.args.kwarg.arg)
            self._record_def(key, node.args.kwarg)
        self.generic_visit(node)
        self._exit()

    def visit_ListComp(self, node: ast.ListComp):
        self._enter(ScopeKind.COMPREHENSION, "<listcomp>", node)
        for comp in node.generators:
            self.visit(comp)
        self.visit(node.elt)
        self._exit()

    def visit_SetComp(self, node: ast.SetComp):
        self._enter(ScopeKind.COMPREHENSION, "<setcomp>", node)
        for comp in node.generators:
            self.visit(comp)
        self.visit(node.elt)
        self._exit()

    def visit_DictComp(self, node: ast.DictComp):
        self._enter(ScopeKind.COMPREHENSION, "<dictcomp>", node)
        for comp in node.generators:
            self.visit(comp)
        self.visit(node.key)
        self.visit(node.value)
        self._exit()

    def visit_GeneratorExp(self, node: ast.GeneratorExp):
        self._enter(ScopeKind.COMPREHENSION, "<genexpr>", node)
        for comp in node.generators:
            self.visit(comp)
        self.visit(node.elt)
        self._exit()

    def visit_comprehension(self, node: ast.comprehension):
        self._record_assignment_targets([node.target])
        self.visit(node.iter)
        for if_clause in node.ifs:
            self.visit(if_clause)

    def visit_Assign(self, node: ast.Assign):
        self._record_assignment_targets(node.targets)
        self.generic_visit(node)

    def visit_AnnAssign(self, node: ast.AnnAssign):
        if node.target:
            self._record_assignment_targets([node.target])
        self.generic_visit(node)

    def visit_AugAssign(self, node: ast.AugAssign):
        self._record_assignment_targets([node.target])
        self.generic_visit(node)

    def visit_For(self, node: ast.For):
        self._record_assignment_targets([node.target])
        self.generic_visit(node)

    visit_AsyncFor = visit_For

    def visit_With(self, node: ast.With):
        for item in node.items:
            if item.optional_vars:
                self._record_assignment_targets([item.optional_vars])
        self.generic_visit(node)

    visit_AsyncWith = visit_With

    def visit_Import(self, node: ast.Import):
        for alias in node.names:
            name = alias.asname if alias.asname else alias.name.split('.')[0]
            key = self._binding_key_for_assignment(name)
            self._record_def(key, alias)
        self.generic_visit(node)

    def visit_ImportFrom(self, node: ast.ImportFrom):
        for alias in node.names:
            if alias.name == "*":
                continue
            name = alias.asname if alias.asname else alias.name
            key = self._binding_key_for_assignment(name)
            self._record_def(key, alias)
        self.generic_visit(node)

    def visit_ExceptHandler(self, node: ast.ExceptHandler):
        if node.name:
            key = self._binding_key_for_assignment(node.name)
            self.index.except_names.setdefault(key, set()).add(node)
            synthetic_name = ast.Name(id=node.name, ctx=ast.Store())
            self._record_def(key, synthetic_name)
        self.generic_visit(node)

    def visit_Name(self, node: ast.Name):
        key = self._binding_key_by_lookup(node.id)
        if key is not None:
            if isinstance(node.ctx, ast.Load):
                self._record_use(key, node)
            elif isinstance(node.ctx, ast.Del):
                self._record_use(key, node)

class EnhancedReplaceTransformer(ast.NodeTransformer):
    def __init__(
        self,
        *,
        tree: ast.AST,
        index: Any,
        target: str,
        replacement: str,
        scope_filter: Optional[str] = None,
        target_functions: Optional[Iterable[str]] = None,
        target_binding_key: Any = None,
        debug: bool = False,
    ):
        super().__init__()
        self.tree = tree
        self.index = index
        self.target = target
        self.replacement = replacement
        self.scope_filter = scope_filter
        self.target_functions: Set[str] = set(target_functions or [])
        self.target_binding_key = target_binding_key
        self.debug = debug
        self._target_binding_keys: Optional[Set[Any]] = None

    def _scope_kind_name(self, scope: Any) -> str:
        k = getattr(scope, "kind", None)
        if hasattr(k, "name"):
            return str(k.name)
        return str(k) if k is not None else "UNKNOWN"

    def _is_module_scope(self, scope: Any) -> bool:
        return "MODULE" in self._scope_kind_name(scope).upper()

    def _is_function_like_scope(self, scope: Any) -> bool:
        kind = self._scope_kind_name(scope).upper()
        return "FUNCTION" in kind or "LAMBDA" in kind

    def _is_class_scope(self, scope: Any) -> bool:
        return "CLASS" in self._scope_kind_name(scope).upper()

    def _is_comprehension_scope(self, scope: Any) -> bool:
        return "COMPREHENSION" in self._scope_kind_name(scope).upper()

    def _scope_matches_filter(self, scope: Any) -> bool:
        if self.scope_filter is None:
            return True
        f = self.scope_filter.lower()
        if f == "local":
            return self._is_function_like_scope(scope) or self._is_comprehension_scope(scope)
        if f == "class":
            return self._is_class_scope(scope)
        if f in ("global", "nonlocal"): # filtrées plus tard par l’origine réelle du binding (module / nonlocal)
            return True
        return True

    def _iter_arg_nodes(self, args: ast.arguments):
        for a in getattr(args, "posonlyargs", []) or []:
            if a: yield a
        for a in (args.args or []):
            if a: yield a
        if getattr(args, "vararg", None):
            yield getattr(args, "vararg")
        for a in (getattr(args, "kwonlyargs", []) or []):
            if a: yield a
        if getattr(args, "kwarg", None):
            yield getattr(args, "kwarg")

    def _find_scope_for_node(self, owner_node):
        for sc in getattr(self.index, "scopes", []) or []:
            if getattr(sc, "node", None) is owner_node:
                return sc
        return None

    def _selected_scopes_from_keys(self, selected_keys):
        b2s = getattr(self.index, "binding_key_to_scope", {}) or {}
        scopes = set()
        for k in selected_keys:
            sc = b2s.get(k)
            if sc is not None:
                scopes.add(sc)
        return scopes

    def _rename_parameters_in_arguments(self, args: ast.arguments, owner_node: ast.AST):
        if self._target_binding_keys is None:
            self._target_binding_keys = self._collect_target_binding_keys()
        selected = self._target_binding_keys

        node2b = getattr(self.index, "node_to_binding", {}) or {}
        selected_set = set(selected)
        renamed = False

        # 1) Chemin lié par l’index (ast.arg -> BindingKey)
        for a in self._iter_arg_nodes(args):
            key = node2b.get(a)
            if key is not None and (key in selected_set) and (a.arg == self.target):
                if self.debug:
                    print(f"[rename param] {a.arg}@{getattr(a,'lineno','?')}:{getattr(a,'col_offset','?')} -> {self.replacement} reason=lambda-param-bound")
                a.arg = self.replacement
                renamed = True

        # 2) Fallback par portée
        if not renamed:
            owner_scope = self._find_scope_for_node(owner_node)
            if owner_scope and owner_scope in self._selected_scopes_from_keys(selected):
                for a in self._iter_arg_nodes(args):
                    if a.arg == self.target:
                        if self.debug:
                            print(f"[rename param] {a.arg}@{getattr(a,'lineno','?')}:{getattr(a,'col_offset','?')} -> {self.replacement} reason=lambda-param-fallback")
                        a.arg = self.replacement

    def _find_containing_function_scope(self, node: ast.AST) -> Optional[Any]:
        best = None
        for scope in getattr(self.index, "scopes", []) or []:
            if not self._is_function_like_scope(scope):
                continue
            scope_node = getattr(scope, "node", None)
            if scope_node is None:
                continue
            if self._is_node_inside(scope_node, node):
                if best is None:
                    best = scope
                else:
                    if self._is_node_inside(scope_node, getattr(best, "node", None) or scope_node) is False:
                        best = scope
        return best

    def _binding_of(self, node: ast.AST) -> Optional[Any]:
        return getattr(self.index, "node_to_binding", {}).get(node)

    def _ensure_selected_keys(self) -> Optional[Set[Any]]:
        if (self.target_binding_key is None and not self.scope_filter and not self.target_functions):
            self._target_binding_keys = None
            return None
        if self._target_binding_keys is not None:
            return self._target_binding_keys
        if self.target_binding_key is not None:
            self._target_binding_keys = {self.target_binding_key}
            return self._target_binding_keys
        self._target_binding_keys = self._selected_keys()
        return self._target_binding_keys

    def _in_target_fn(self, node: ast.AST) -> bool:
        if not self.target_functions:
            return True
        fn = self._find_containing_function_scope(node)
        return fn is not None and fn.name in self.target_functions

    def _selected_keys(self) -> Set[Any]:
        keys: Set[Any] = set()
        b2s = getattr(self.index, "binding_key_to_scope", {}) or {}

        for key, scope in b2s.items():
            if getattr(key, "name", None) != self.target:
                continue
            if not self._scope_matches_filter(scope):
                continue
            if self.target_functions:
                fn = self._find_containing_function_scope(getattr(scope, "node", None))
                fn_name = getattr(fn, "name", None) if fn else None
                if fn_name not in self.target_functions:
                    continue
            keys.add(key)
        return keys

    def _should_rename_node(self, node: ast.AST) -> bool:
        if not isinstance(node, ast.Name) or node.id != self.target:
            return False
        key = self._binding_of(node)
        if key is None:
            return False
        if self.target_binding_key is not None:
            decision = (key == self.target_binding_key)
            if self.debug: self._debug_decision(node, key, decision, "anchor")
            return decision
        selected = self._ensure_selected_keys()
        if selected is None:
            if self.debug: self._debug_decision(node, key, True, "no-filters")
            return True
        decision = key in selected
        if self.debug: self._debug_decision(node, key, decision, "filtered")
        return decision

    def _handler_matches_selection(self, mapping: Dict[Any, Set[ast.AST]], node: ast.AST) -> bool:
        selected = self._ensure_selected_keys()
        if selected is None:
            return True
        if not selected:
            return False
        for key in selected:
            nodes = mapping.get(key)
            if nodes and node in nodes:
                return True
        return False

    def visit_Name(self, node: ast.Name):
        if self._should_rename_node(node):
            return ast.copy_location(ast.Name(id=self.replacement, ctx=node.ctx), node)
        return node

    def visit_Global(self, node: ast.Global):
        if self.target in node.names:
            mapping = getattr(self.index, "global_names", {}) or {}
            if self._handler_matches_selection(mapping, node):
                new_names = [self.replacement if n == self.target else n for n in node.names]
                return ast.copy_location(ast.Global(names=new_names), node)
        return node

    def visit_Nonlocal(self, node: ast.Nonlocal):
        if self.target in node.names:
            mapping = getattr(self.index, "nonlocal_names", {}) or {}
            if self._handler_matches_selection(mapping, node):
                new_names = [self.replacement if n == self.target else n for n in node.names]
                return ast.copy_location(ast.Nonlocal(names=new_names), node)
        return node

    def visit_ExceptHandler(self, node: ast.ExceptHandler):
        if getattr(node, "name", None) == self.target:
            mapping = getattr(self.index, "except_names", {}) or {}
            if self._handler_matches_selection(mapping, node):
                new_node = ast.copy_location(ast.ExceptHandler(type=node.type, name=self.replacement, body=node.body), node)
                self.generic_visit(new_node)
                return new_node
        self.generic_visit(node)
        return node

    def visit_FunctionDef(self, node: ast.FunctionDef):
        self._rename_parameters_in_arguments(node.args, owner_node=node)
        return self.generic_visit(node)

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef):
        self._rename_parameters_in_arguments(node.args, owner_node=node)
        return self.generic_visit(node)

    def visit_Lambda(self, node: ast.Lambda):
        self._rename_parameters_in_arguments(node.args, owner_node=node)
        return self.generic_visit(node)

    def _debug_decision(self, node: ast.AST, key: Any, decision: bool, reason: str):
        try:
            ctx = type(getattr(node, "ctx", None)).__name__
        except Exception:
            ctx = "?"
        fn = self._find_containing_function_scope(node)
        fn_name = getattr(fn, "name", None) if fn else None
        origin = getattr(self.index, "binding_key_to_scope", {}).get(key)
        origin_kind = self._scope_kind_name(origin) if origin else None
        print(f"[rename? {decision}] {getattr(node, 'id', '?')}@{getattr(node, 'lineno', '?')}:{getattr(node, 'col_offset', '?')} ctx={ctx} fn={fn_name} origin={origin_kind} reason={reason}")

def super_replace_autonomous(code: str, target: str, replacement: str, context_rules: dict) -> str:
    tree = ast.parse(code)
    builder = ScopeBuilder()
    builder.visit(tree)
    transformer = EnhancedReplaceTransformer(
        tree=tree,
        index=builder.index,
        target=target,
        replacement=replacement,
        scope_filter=context_rules.get("scope"),
        target_functions=context_rules.get("functions"),
        target_binding_key=context_rules.get("target_binding_key"),
        debug=context_rules.get("debug", False)
    )
    new_tree = transformer.visit(tree)
    ast.fix_missing_locations(new_tree)
    try:
        return astor.to_source(new_tree)
    except Exception:
        try:
            return ast.unparse(new_tree)
        except Exception as e:
            raise RuntimeError("Could not serialize AST back to source") from e

def get_binding_info(code: str, target: str) -> dict:
    tree = ast.parse(code)
    builder = ScopeBuilder()
    builder.visit(tree)
    info = {'bindings': [], 'total_uses': 0, 'total_definitions': 0}
    for scope in builder.index.scopes:
        if target in scope.locals:
            binding = scope.locals[target]
            uses = len(builder.index.uses.get(binding.key, []))
            defs = len(builder.index.defs.get(binding.key, []))
            info['bindings'].append({
                'scope_kind': scope.kind.name,
                'scope_name': scope.name,
                'scope_id': scope.id,
                'uses': uses,
                'definitions': defs,
                'binding_key': binding.key
            })
            info['total_uses'] += uses
            info['total_definitions'] += defs
    return info

def check_rename_safety(code: str, target: str, replacement: str, context_rules: dict) -> tuple[bool, list[str]]:
    issues = []
    try:
        tree = ast.parse(code)
        builder = ScopeBuilder()
        builder.visit(tree)
        replacement_bindings = []
        for scope in builder.index.scopes:
            if replacement in scope.locals:
                replacement_bindings.append((scope.kind.name, scope.name))
        if replacement_bindings:
            issues.append(f"Name '{replacement}' already exists in scopes: {replacement_bindings}")
        import keyword
        if keyword.iskeyword(replacement):
            issues.append(f"'{replacement}' is a Python keyword")
        import builtins
        if replacement in dir(builtins):
            issues.append(f"'{replacement}' shadows a builtin name")
    except Exception as e:
        issues.append(f"Error analyzing code: {e}")
    return len(issues) == 0, issues

if __name__ == "__main__":
    test_code = '''
def outer():
    x = 1
    def inner():
        nonlocal x
        x = 2
        return x
    def another():
        return x
    return inner, another
x = 10
'''
    
    print("=== FIXED VERSION TESTS ===")
    print("Original code:")
    print(test_code)
    print("\n1. Binding information for 'x':")
    binding_info = get_binding_info(test_code, "x")
    print(f"Total: {binding_info['total_uses']} uses, {binding_info['total_definitions']} definitions")
    for binding in binding_info['bindings']:
        print(f"  - {binding['scope_kind']} '{binding['scope_name']}': {binding['uses']} uses, {binding['definitions']} definitions")
    
    print("\n2. Replace local 'x' in 'outer' function:")
    result_local = super_replace_autonomous(test_code, "x", "local_x", {"functions": ["outer"], "scope": "local"})
    print(result_local)
    
    comp_code = '''
def func():
    x = [i for i in range(3)]
    i = 10
    return x, i
'''
    print("\n3. Comprehension scope test:")
    print("Original:")
    print(comp_code)
    comp_info = get_binding_info(comp_code, "i")
    print("Binding info for 'i':")
    for binding in comp_info['bindings']:
        print(f"  - {binding['scope_kind']} '{binding['scope_name']}': {binding['uses']} uses, {binding['definitions']} definitions")
