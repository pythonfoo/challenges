from importlib import import_module
from importlib import resources

SOLUTION = dict()

def register_solution(func):
    """Decorator to register plug-ins"""
    name = func.__module__
    SOLUTION[name] = func
    return func

def get_all_solutions():
    _import_solutions()
    return SOLUTION.values()

def __getattr__(name):
    """Return a named plugin"""
    try:
        return SOLUTION[name]
    except KeyError:
        _import_solutions()
        if name in SOLUTION:
            return SOLUTION[name]
        else:
            raise AttributeError(
                f"module {__name__!r} has no attribute {name!r}"
            ) from None

def __dir__():
    """List available plug-ins"""
    _import_solutions()
    return list(SOLUTION.keys())

def _import_solutions():
    """Import all resources to register plug-ins"""
    for name in resources.contents(__name__):
        if name.endswith(".py"):
            import_module(f"{__name__}.{name[:-3]}")