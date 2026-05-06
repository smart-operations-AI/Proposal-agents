import asyncio
from typing import Dict, List, Callable, Any, Awaitable

class AgentMessageBus:
    """
    Asynchronous Pub/Sub message bus for lateral communication between agents.
    Supports dynamic subscription and unsubscription of handlers.
    """
    def __init__(self):
        self._subscribers: Dict[str, List[Callable[[Any], Awaitable[Any]]]] = {}
        self._lock = asyncio.Lock()

    async def subscribe(self, topic: str, handler: Callable[[Any], Awaitable[Any]]):
        """Adds a handler to a specific topic"""
        async with self._lock:
            if topic not in self._subscribers:
                self._subscribers[topic] = []
            self._subscribers[topic].append(handler)

    async def unsubscribe(self, topic: str, handler: Callable[[Any], Awaitable[Any]]):
        """Removes a specific handler from a topic to prevent memory leaks or duplicate execution"""
        async with self._lock:
            if topic in self._subscribers:
                try:
                    self._subscribers[topic].remove(handler)
                except ValueError:
                    # Handler wasn't in the list
                    pass

    async def publish(self, topic: str, message: Any) -> List[Any]:
        """
        Publishes a message to all subscribers of a topic and returns their responses.
        """
        handlers = []
        async with self._lock:
            handlers = self._subscribers.get(topic, []).copy()

        if not handlers:
            return []

        # Execute all handlers and gather results
        tasks = [handler(message) for handler in handlers]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Filter out exceptions if any
        return [res for res in results if not isinstance(res, Exception)]
