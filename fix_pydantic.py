"""
Monkey patch to fix Pydantic v1 compatibility with Python 3.12
This must be imported before any langchain/langgraph imports
"""
import sys

def patch_pydantic_v1():
    """Patch Pydantic v1 to work with Python 3.12"""
    try:
        from pydantic.v1.typing import evaluate_forwardref
        import typing
        
        # Store original function
        _original_evaluate = evaluate_forwardref
        
        def patched_evaluate_forwardref(type_, globalns, localns):
            """Patched version that works with Python 3.12"""
            if sys.version_info >= (3, 12):
                # Python 3.12+ requires recursive_guard as keyword argument
                return type_._evaluate(globalns, localns, recursive_guard=frozenset())
            else:
                # Python < 3.12
                return _original_evaluate(type_, globalns, localns)
        
        # Apply patch
        import pydantic.v1.typing
        pydantic.v1.typing.evaluate_forwardref = patched_evaluate_forwardref
        
        print("✓ Applied Pydantic v1 Python 3.12 compatibility patch")
        return True
    except Exception as e:
        print(f"⚠ Could not apply Pydantic patch: {e}")
        return False

# Apply patch immediately when this module is imported
patch_pydantic_v1()
