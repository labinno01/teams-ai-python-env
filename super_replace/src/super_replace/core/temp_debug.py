from super_replace.core.autonomous_replacer import EnhancedReplaceTransformer, ScopeKind, Index, Scope
import ast

# Create dummy objects for testing
class DummyNode:
    pass

class DummyIndex(Index):
    def __init__(self):
        super().__init__()
        self.scopes = [
            Scope(kind=ScopeKind.FUNCTION, parent=None, id=0, name="func1", node=DummyNode()),
            Scope(kind=ScopeKind.COMPREHENSION, parent=None, id=1, name="comp1", node=DummyNode()),
            Scope(kind=ScopeKind.MODULE, parent=None, id=2, name="module1", node=DummyNode())
        ]
        self.binding_key_to_scope = {} # Not strictly needed for this test

# Instantiate EnhancedReplaceTransformer
dummy_tree = ast.parse("x = 1")
dummy_index = DummyIndex()
transformer = EnhancedReplaceTransformer(
    tree=dummy_tree,
    index=dummy_index,
    target="x",
    replacement="y",
    scope_filter="local",
    debug=True
)

# Test _scope_matches_filter directly
print(f"Testing _scope_matches_filter with FUNCTION: {transformer._scope_matches_filter(dummy_index.scopes[0])}")
print(f"Testing _scope_matches_filter with COMPREHENSION: {transformer._scope_matches_filter(dummy_index.scopes[1])}")
print(f"Testing _scope_matches_filter with MODULE: {transformer._scope_matches_filter(dummy_index.scopes[2])}")

# Test _collect_target_binding_keys directly
print(f"Testing _collect_target_binding_keys: {transformer._collect_target_binding_keys()}")

# Test _selected_keys (this will call _scope_matches_filter internally)
print(f"Testing _selected_keys: {transformer._selected_keys()}")