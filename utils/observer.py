from typing import Dict, List, Callable, Any
from dataclasses import dataclass, field

@dataclass
class Observer:
    """Base class for objects that need to be notified of changes."""
    def update(self, event: str, data: Any = None) -> None:
        pass

@dataclass
class Subject:
    """Base class for objects that need to notify observers."""
    _observers: Dict[str, List[Observer]] = field(default_factory=dict)

    def attach(self, event: str, observer: Observer) -> None:
        if event not in self._observers:
            self._observers[event] = []
        self._observers[event].append(observer)

    def detach(self, event: str, observer: Observer) -> None:
        if event in self._observers:
            self._observers[event].remove(observer)

    def notify(self, event: str, data: Any = None) -> None:
        if event in self._observers:
            for observer in self._observers[event]:
                observer.update(event, data)
