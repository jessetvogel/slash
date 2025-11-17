from __future__ import annotations

from collections.abc import Callable
from typing import Any, Generic, TypeVar

T = TypeVar("T")


OBSERVER_STACK: list[Observer] = []


class Readable(Generic[T]):
    """Base class for reactive readable objects.

    Tracks observers that depend on it so they can be notified when the value changes.

    Args:
        value: Initial value.
    """

    def __init__(self, value: T) -> None:
        self._value = value
        self._observers: set[Observer[Any]] = set()

    def get(self) -> T:
        """Get the current value.

        Also registers the current observer, if any, as a dependent.
        """
        if OBSERVER_STACK:
            observer = OBSERVER_STACK[-1]
            self._observers.add(observer)
            observer._dependencies.add(self)
        return self._value

    def __call__(self) -> T:
        return self.get()


class Observer(Generic[T]):
    """Base class for reactive observer objects.

    Args:
        fn: Function to execute when running the observer.
    """

    def __init__(self, fn: Callable[[], T]) -> None:
        self._fn = fn
        self._dependencies: set[Readable[Any]] = set()

    def _run(self) -> T:
        for dep in self._dependencies:
            dep._observers.discard(self)
        self._dependencies.clear()

        OBSERVER_STACK.append(self)
        try:
            return self._fn()
        finally:
            OBSERVER_STACK.pop()


class Signal(Readable[T]):
    """Reactive value that notifies observers when updated.

    Args:
        value: Initial value.
    """

    def set(self, value: T) -> None:
        """Set the value and notify all observers if it has changed.

        Args:
            value: New value to set.
        """
        if value != self._value:
            self._value = value
            for obs in list(self._observers):
                obs._run()

    def __repr__(self) -> str:
        return f"Signal({self._value})"


class Computed(Observer[T], Readable[T]):
    """Reactive value derived from other reactive values.

    Args:
        fn: Function that computes the value.
    """

    def __init__(self, fn: Callable[[], T]) -> None:
        Observer.__init__(self, fn)
        Readable.__init__(self, Observer._run(self))

    def _run(self) -> T:
        if (value := Observer._run(self)) != self._value:
            self._value = value
            for obs in list(self._observers):
                obs._run()
        return self._value

    def __repr__(self) -> str:
        return f"Computed({self._value})"


class Effect(Observer[Any]):
    """Reactive effect that runs automatically when its dependencies update."""

    def __init__(self, fn: Callable[[], Any]) -> None:
        super().__init__(fn)
        self._run()


__all__ = ["Signal", "Computed", "Effect"]
