from typing import Callable, Optional, TypeVar

# Argument type
A = TypeVar('A', contravariant=True)
# Return type
R = TypeVar('R', covariant=True)


def optionally(func: Callable[[Optional[A]], R], value: Optional[A]) -> Optional[R]:
    return func(value) if value is not None else None
