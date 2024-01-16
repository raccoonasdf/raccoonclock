from typing import TypeVar
from .timelib import Time
from observer import SearchlibCallable

T = TypeVar('T')
def find_discrete(start_time: Time,
                  end_time: Time,
                  f: SearchlibCallable[T],
                  epsilon: float = ...,
                  num: int = ...) -> tuple[list[Time], list[T]]: ...