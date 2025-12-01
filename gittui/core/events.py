"""Event system for cross-panel communication."""

from dataclasses import dataclass, field
from typing import Callable, Dict, List, Any, Optional
from enum import Enum, auto


class EventType(Enum):
    REFRESH = auto()
    FOCUS_CHANGED = auto()
    FILE_STAGED = auto()
    FILE_UNSTAGED = auto()
    COMMIT_CREATED = auto()
    BRANCH_CHANGED = auto()
    COMMAND_OUTPUT = auto()
    ERROR = auto()
    STATUS_UPDATE = auto()
    QUIT = auto()
    RESIZE = auto()


@dataclass
class Event:
    type: EventType
    data: Dict[str, Any] = field(default_factory=dict)
    source: Optional[str] = None


class EventBus:
    def __init__(self):
        self._subscribers: Dict[EventType, List[Callable[[Event], None]]] = {}
        self._global_subscribers: List[Callable[[Event], None]] = []
    
    def subscribe(self, event_type: EventType, callback: Callable[[Event], None]):
        if event_type not in self._subscribers:
            self._subscribers[event_type] = []
        self._subscribers[event_type].append(callback)
    
    def subscribe_all(self, callback: Callable[[Event], None]):
        self._global_subscribers.append(callback)
    
    def unsubscribe(self, event_type: EventType, callback: Callable[[Event], None]):
        if event_type in self._subscribers:
            self._subscribers[event_type].remove(callback)
    
    def emit(self, event: Event):
        for callback in self._global_subscribers:
            try:
                callback(event)
            except Exception:
                pass
        
        if event.type in self._subscribers:
            for callback in self._subscribers[event.type]:
                try:
                    callback(event)
                except Exception:
                    pass
    
    def emit_simple(self, event_type: EventType, **data):
        self.emit(Event(type=event_type, data=data))
