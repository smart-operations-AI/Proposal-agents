import asyncio
from typing import Dict, List, Callable, Any, Awaitable

class AgentMessageBus:
    """
    Asynchronous Pub/Sub message bus for lateral communication between agents.
    """
    def __init__(self):
        self._subscribers: Dict[str, List[Callable[[Any], Awaitable[Any]]]] = {}
        self._lock = asyncio.Lock()

    async def subscribe(self, topic: str, handler: Callable[[Any], Awaitable[Any]]):
        async with self._lock:
            if topic not in self._subscribers:
                self._subscribers[topic] = []
            self._subscribers[topic].append(handler)

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
