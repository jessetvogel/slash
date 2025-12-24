from __future__ import annotations

from collections.abc import Callable
from typing import Any, Generic, TypeVar

from slash.core import Elem

T = TypeVar("T")


OBSERVER_STACK: list[Computed[Any] | Effect] = []


def get(x: Signal[T] | Computed[T]) -> T:
    if OBSERVER_STACK:
        observer = OBSERVER_STACK[-1]
        x._observers.add(observer)
        observer._dependencies.add(x)
    return x._value


def run(x: Computed[T] | Effect) -> None:
    for dep in x._dependencies:
        dep._observers.discard(x)
    x._dependencies.clear()
    OBSERVER_STACK.append(x)
    try:
        value = x._fn()
    finally:
        OBSERVER_STACK.pop()

    if isinstance(x, Computed):
        if not hasattr(x, "_value") or value != x._value:
            x._value = value
            for observer in x._observers:
                run(observer)


def to_elem(x: Signal[T] | Computed[T], tag: str = "span") -> Elem:
    elem = Elem(tag)
    Effect(lambda: elem.set_text(str(x())))
    return elem


class Signal(Generic[T]):
    """Reactive value that notifies observers when updated.

    Args:
        value: Initial value.
    """

    def __init__(self, value: T) -> None:
        self._value = value
        self._observers: set[Computed[Any] | Effect] = set()

    def set(self, value: T) -> None:
        """Set the value and notify all observers if it has changed.

        Args:
            value: New value to set.
        """
        if value != self._value:
            self._value = value
            self.trigger()

    def get(self) -> T:
        """Return the current value."""
        return get(self)

    def trigger(self) -> None:
        """Trigger all observers without changing the value."""
        for observer in self._observers:
            run(observer)

    def __call__(self) -> T:
        return self.get()

    def __repr__(self) -> str:
        return f"Signal({self._value})"

    def to_elem(self, tag: str = "span") -> Elem:
        """Create an element whose content is the value of the signal.

        The content of the returned element gets updated with the value of the signal.

        Args:
            tag: Tag of the element.

        Returns:
            Element with given tag whose content equals the value of the signal.
        """
        return to_elem(self, tag)


class Computed(Generic[T]):
    """Reactive value computed from other reactive values.

    Args:
        fn: Function that computes the value from other reactive values.
    """

    _value: T

    def __init__(self, fn: Callable[[], T]) -> None:
        self._fn = fn
        self._dependencies: set[Signal[Any] | Computed[Any]] = set()
        self._observers: set[Computed[Any] | Effect] = set()
        run(self)

    def get(self) -> T:
        """Return the current value."""
        return get(self)

    def __call__(self) -> T:
        return self.get()

    def __repr__(self) -> str:
        return f"Computed({self._value})"

    def to_elem(self, tag: str = "span") -> Elem:
        """Create an element whose content is the computed value.

        The content of the returned element gets updated with the computed value.

        Args:
            tag: Tag of the element.

        Returns:
            Element with given tag whose content equals the computed value.
        """
        return to_elem(self, tag)


class Effect:
    """Reactive effect that runs automatically when the reactive values that it depends are updated.

    Args:
        fn: Function that executes the effect from reactive values.
    """

    def __init__(self, fn: Callable[[], Any]) -> None:
        self._fn = fn
        self._dependencies: set[Signal[Any] | Computed[Any]] = set()
        run(self)


__all__ = ["Signal", "Computed", "Effect"]
