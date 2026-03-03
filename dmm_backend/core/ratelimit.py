from typing import Callable, Any

try:
    from slowapi import Limiter  # type: ignore
    from slowapi.util import get_remote_address  # type: ignore
    from slowapi.middleware import SlowAPIMiddleware  # type: ignore
    _available = True
except Exception:  # pragma: no cover - optional dependency
    Limiter = None  # type: ignore
    get_remote_address = None  # type: ignore
    SlowAPIMiddleware = None  # type: ignore
    _available = False


class _NoopLimiter:
    def limit(self, _rule: str) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
        def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
            return func
        return decorator


if _available:
    limiter = Limiter(key_func=get_remote_address)
else:
    limiter = _NoopLimiter()


def add_rate_limit_middleware(app):
    """Attach slowapi middleware if available; otherwise no-op."""
    if _available and SlowAPIMiddleware is not None:
        app.state.limiter = limiter
        app.add_middleware(SlowAPIMiddleware)