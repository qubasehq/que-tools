"""Enhanced EventBus for intra-process messaging with async support
Provides robust pub/sub implementation with asyncio + queues
"""
import asyncio
import logging
import time
from typing import Callable, Dict, List, Any, Optional, Union
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)

class EventPriority(Enum):
    LOW = 1
    NORMAL = 2
    HIGH = 3
    CRITICAL = 4

@dataclass
class Event:
    name: str
    payload: Any
    timestamp: float
    priority: EventPriority = EventPriority.NORMAL
    source: Optional[str] = None
    correlation_id: Optional[str] = None

class EventBus:
    """Enhanced event bus with async support and priority handling"""
    
    def __init__(self, max_queue_size: int = 1000):
        self._subscribers: Dict[str, List[Callable]] = {}
        self._async_subscribers: Dict[str, List[Callable]] = {}
        self._event_queue: asyncio.Queue = asyncio.Queue(maxsize=max_queue_size)
        self._running = False
        self._processor_task: Optional[asyncio.Task] = None
        self._stats = {
            "events_published": 0,
            "events_processed": 0,
            "errors": 0
        }
    
    def subscribe(self, event_name: str, handler: Callable, async_handler: bool = False):
        """Subscribe to events"""
        if async_handler:
            self._async_subscribers.setdefault(event_name, []).append(handler)
        else:
            self._subscribers.setdefault(event_name, []).append(handler)
        
        logger.debug(f"Subscribed to '{event_name}' (async={async_handler})")
    
    def unsubscribe(self, event_name: str, handler: Callable):
        """Unsubscribe from events"""
        # Remove from sync subscribers
        if event_name in self._subscribers:
            try:
                self._subscribers[event_name].remove(handler)
                if not self._subscribers[event_name]:
                    del self._subscribers[event_name]
            except ValueError:
                pass
        
        # Remove from async subscribers
        if event_name in self._async_subscribers:
            try:
                self._async_subscribers[event_name].remove(handler)
                if not self._async_subscribers[event_name]:
                    del self._async_subscribers[event_name]
            except ValueError:
                pass
    
    def publish(self, event_name: str, payload: Any = None, 
                priority: EventPriority = EventPriority.NORMAL,
                source: Optional[str] = None,
                correlation_id: Optional[str] = None):
        """Publish event (sync)"""
        event = Event(
            name=event_name,
            payload=payload,
            timestamp=time.time(),
            priority=priority,
            source=source,
            correlation_id=correlation_id
        )
        
        # Handle sync subscribers immediately
        self._handle_sync_subscribers(event)
        
        # Queue for async processing
        try:
            self._event_queue.put_nowait(event)
            self._stats["events_published"] += 1
        except asyncio.QueueFull:
            logger.warning(f"Event queue full, dropping event: {event_name}")
            self._stats["errors"] += 1
    
    async def publish_async(self, event_name: str, payload: Any = None,
                           priority: EventPriority = EventPriority.NORMAL,
                           source: Optional[str] = None,
                           correlation_id: Optional[str] = None):
        """Publish event (async)"""
        event = Event(
            name=event_name,
            payload=payload,
            timestamp=time.time(),
            priority=priority,
            source=source,
            correlation_id=correlation_id
        )
        
        # Handle sync subscribers immediately
        self._handle_sync_subscribers(event)
        
        # Queue for async processing
        await self._event_queue.put(event)
        self._stats["events_published"] += 1
    
    def _handle_sync_subscribers(self, event: Event):
        """Handle synchronous subscribers"""
        handlers = self._subscribers.get(event.name, [])
        for handler in handlers:
            try:
                handler(event)
            except Exception as e:
                logger.error(f"Error in sync handler for '{event.name}': {e}")
                self._stats["errors"] += 1
    
    async def _handle_async_subscribers(self, event: Event):
        """Handle asynchronous subscribers"""
        handlers = self._async_subscribers.get(event.name, [])
        
        # Run all async handlers concurrently
        if handlers:
            tasks = []
            for handler in handlers:
                try:
                    if asyncio.iscoroutinefunction(handler):
                        tasks.append(asyncio.create_task(handler(event)))
                    else:
                        # Wrap sync function in async
                        tasks.append(asyncio.create_task(asyncio.to_thread(handler, event)))
                except Exception as e:
                    logger.error(f"Error creating task for '{event.name}': {e}")
                    self._stats["errors"] += 1
            
            if tasks:
                # Wait for all handlers to complete
                results = await asyncio.gather(*tasks, return_exceptions=True)
                for i, result in enumerate(results):
                    if isinstance(result, Exception):
                        logger.error(f"Error in async handler for '{event.name}': {result}")
                        self._stats["errors"] += 1
    
    async def start(self):
        """Start the event bus processor"""
        if self._running:
            return
        
        self._running = True
        self._processor_task = asyncio.create_task(self._process_events())
        logger.info("EventBus started")
    
    async def stop(self):
        """Stop the event bus processor"""
        if not self._running:
            return
        
        self._running = False
        
        if self._processor_task:
            self._processor_task.cancel()
            try:
                await self._processor_task
            except asyncio.CancelledError:
                pass
        
        logger.info("EventBus stopped")
    
    async def _process_events(self):
        """Main event processing loop"""
        logger.info("Event processor started")
        
        while self._running:
            try:
                # Get event with timeout to allow graceful shutdown
                event = await asyncio.wait_for(self._event_queue.get(), timeout=1.0)
                
                # Process async subscribers
                await self._handle_async_subscribers(event)
                
                self._stats["events_processed"] += 1
                
            except asyncio.TimeoutError:
                # Normal timeout, continue loop
                continue
            except Exception as e:
                logger.error(f"Error processing event: {e}")
                self._stats["errors"] += 1
    
    def get_stats(self) -> Dict[str, Any]:
        """Get event bus statistics"""
        return {
            **self._stats,
            "queue_size": self._event_queue.qsize(),
            "subscriber_count": sum(len(handlers) for handlers in self._subscribers.values()),
            "async_subscriber_count": sum(len(handlers) for handlers in self._async_subscribers.values()),
            "running": self._running
        }
    
    def clear_subscribers(self):
        """Clear all subscribers"""
        self._subscribers.clear()
        self._async_subscribers.clear()
        logger.info("All subscribers cleared")

# Global event bus instance
_global_eventbus = EventBus()

# Legacy compatibility functions
def subscribe(event_name: str, handler: Callable):
    """Subscribe to events (legacy compatibility)"""
    _global_eventbus.subscribe(event_name, handler)

def publish(event_name: str, payload: Any = None):
    """Publish event (legacy compatibility)"""
    _global_eventbus.publish(event_name, payload)

# New async functions
async def start_eventbus():
    """Start the global event bus"""
    await _global_eventbus.start()

async def stop_eventbus():
    """Stop the global event bus"""
    await _global_eventbus.stop()

def get_eventbus() -> EventBus:
    """Get the global event bus instance"""
    return _global_eventbus
