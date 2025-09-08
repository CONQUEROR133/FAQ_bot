import asyncio
import time
import logging
import psutil
import gc
from typing import Dict, Any, Optional, Union, Callable, Awaitable
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from functools import wraps
from collections import OrderedDict
import threading
import weakref

logger = logging.getLogger(__name__)


@dataclass
class PerformanceMetrics:
    """Performance metrics tracking."""
    total_requests: int = 0
    avg_response_time: float = 0.0
    cache_hits: int = 0
    cache_misses: int = 0
    memory_usage_mb: float = 0.0
    cpu_usage_percent: float = 0.0
    active_connections: int = 0
    embeddings_load_time: float = 0.0
    database_query_time: float = 0.0
    
    @property
    def cache_hit_rate(self) -> float:
        """Calculate cache hit rate percentage."""
        total = self.cache_hits + self.cache_misses
        return (self.cache_hits / total * 100) if total > 0 else 0.0
    
    def update_memory_usage(self) -> None:
        """Update current memory usage."""
        try:
            process = psutil.Process()
            self.memory_usage_mb = process.memory_info().rss / 1024 / 1024
            self.cpu_usage_percent = process.cpu_percent()
        except Exception as e:
            logger.warning(f"Failed to update system metrics: {e}")


class LRUCache:
    """Thread-safe LRU cache implementation with TTL support."""
    
    def __init__(self, max_size: int = 1000, ttl_seconds: int = 3600):
        """Initialize LRU cache.
        
        Args:
            max_size: Maximum number of items to cache
            ttl_seconds: Time to live for cache entries
        """
        self.max_size = max_size
        self.ttl_seconds = ttl_seconds
        self._cache: OrderedDict = OrderedDict()
        self._timestamps: Dict[str, datetime] = {}
        self._lock = threading.RLock()
        self._hits = 0
        self._misses = 0
    
    def get(self, key: str) -> Optional[Any]:
        """Get item from cache.
        
        Args:
            key: Cache key
            
        Returns:
            Cached value or None if not found/expired
        """
        with self._lock:
            # Check if key exists and is not expired
            if key in self._cache:
                timestamp = self._timestamps.get(key)
                if timestamp and datetime.now() - timestamp < timedelta(seconds=self.ttl_seconds):
                    # Move to end (most recently used)
                    self._cache.move_to_end(key)
                    self._hits += 1
                    return self._cache[key]
                else:
                    # Expired, remove
                    self._remove_key(key)
            
            self._misses += 1
            return None
    
    def set(self, key: str, value: Any) -> None:
        """Set item in cache.
        
        Args:
            key: Cache key
            value: Value to cache
        """
        with self._lock:
            # Remove existing entry if present
            if key in self._cache:
                self._remove_key(key)
            
            # Add new entry
            self._cache[key] = value
            self._timestamps[key] = datetime.now()
            
            # Enforce size limit
            while len(self._cache) > self.max_size:
                oldest_key = next(iter(self._cache))
                self._remove_key(oldest_key)
    
    def _remove_key(self, key: str) -> None:
        """Remove key from cache and timestamps."""
        self._cache.pop(key, None)
        self._timestamps.pop(key, None)
    
    def clear(self) -> None:
        """Clear all cache entries."""
        with self._lock:
            self._cache.clear()
            self._timestamps.clear()
    
    def stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        with self._lock:
            total = self._hits + self._misses
            hit_rate = (self._hits / total * 100) if total > 0 else 0.0
            
            return {
                'size': len(self._cache),
                'max_size': self.max_size,
                'hits': self._hits,
                'misses': self._misses,
                'hit_rate': hit_rate,
                'ttl_seconds': self.ttl_seconds
            }


class AsyncConnectionPool:
    """Async connection pool for database operations."""
    
    def __init__(self, max_connections: int = 10):
        """Initialize connection pool.
        
        Args:
            max_connections: Maximum number of concurrent connections
        """
        self.max_connections = max_connections
        self._semaphore = asyncio.Semaphore(max_connections)
        self._active_connections = 0
        self._total_connections = 0
    
    async def acquire(self):
        """Acquire a connection from the pool."""
        await self._semaphore.acquire()
        self._active_connections += 1
        self._total_connections += 1
        return self
    
    def release(self):
        """Release a connection back to the pool."""
        self._active_connections -= 1
        self._semaphore.release()
    
    async def __aenter__(self):
        """Context manager entry."""
        await self.acquire()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.release()
    
    @property
    def active_connections(self) -> int:
        """Get number of active connections."""
        return self._active_connections
    
    @property
    def total_connections(self) -> int:
        """Get total connections created."""
        return self._total_connections


def timing_decorator(func: Callable) -> Callable:
    """Decorator to measure function execution time."""
    if asyncio.iscoroutinefunction(func):
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            start_time = time.time()
            try:
                result = await func(*args, **kwargs)
                return result
            finally:
                execution_time = time.time() - start_time
                logger.debug(f"{func.__name__} executed in {execution_time:.3f}s")
        return async_wrapper
    else:
        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            start_time = time.time()
            try:
                result = func(*args, **kwargs)
                return result
            finally:
                execution_time = time.time() - start_time
                logger.debug(f"{func.__name__} executed in {execution_time:.3f}s")
        return sync_wrapper


class PerformanceManager:
    """Central performance management and optimization."""
    
    def __init__(self):
        """Initialize performance manager."""
        self.metrics = PerformanceMetrics()
        self.query_cache = LRUCache(max_size=500, ttl_seconds=1800)  # 30 minutes
        self.embedding_cache = LRUCache(max_size=1000, ttl_seconds=3600)  # 1 hour
        self.connection_pool = AsyncConnectionPool(max_connections=20)
        
        # Performance monitoring
        self._response_times = []
        self._start_time = time.time()
        
        # Memory management
        self._last_gc_time = time.time()
        self._gc_threshold = 300  # 5 minutes
        
        # Weak references for cleanup
        self._tracked_objects = weakref.WeakSet()
        
        logger.info("Performance manager initialized")
    
    def track_request(self, response_time: float) -> None:
        """Track request performance metrics.
        
        Args:
            response_time: Request response time in seconds
        """
        self.metrics.total_requests += 1
        self._response_times.append(response_time)
        
        # Keep only last 1000 response times
        if len(self._response_times) > 1000:
            self._response_times = self._response_times[-1000:]
        
        # Update average response time
        self.metrics.avg_response_time = sum(self._response_times) / len(self._response_times)
        
        # Update system metrics periodically
        if self.metrics.total_requests % 10 == 0:
            self.metrics.update_memory_usage()
            self.metrics.active_connections = self.connection_pool.active_connections
    
    def cache_query_result(self, query: str, result: Any) -> None:
        """Cache query result.
        
        Args:
            query: Search query
            result: Query result to cache
        """
        cache_key = f"query:{hash(query.lower().strip())}"
        self.query_cache.set(cache_key, result)
    
    def get_cached_query_result(self, query: str) -> Optional[Any]:
        """Get cached query result.
        
        Args:
            query: Search query
            
        Returns:
            Cached result or None if not found
        """
        cache_key = f"query:{hash(query.lower().strip())}"
        result = self.query_cache.get(cache_key)
        
        if result is not None:
            self.metrics.cache_hits += 1
        else:
            self.metrics.cache_misses += 1
        
        return result
    
    def cache_embedding(self, text: str, embedding: Any) -> None:
        """Cache text embedding.
        
        Args:
            text: Input text
            embedding: Generated embedding
        """
        cache_key = f"embedding:{hash(text.lower().strip())}"
        self.embedding_cache.set(cache_key, embedding)
    
    def get_cached_embedding(self, text: str) -> Optional[Any]:
        """Get cached embedding.
        
        Args:
            text: Input text
            
        Returns:
            Cached embedding or None if not found
        """
        cache_key = f"embedding:{hash(text.lower().strip())}"
        return self.embedding_cache.get(cache_key)
    
    def optimize_memory(self, force: bool = False) -> Dict[str, Any]:
        """Optimize memory usage.
        
        Args:
            force: Force immediate optimization
            
        Returns:
            Optimization results
        """
        current_time = time.time()
        
        if not force and current_time - self._last_gc_time < self._gc_threshold:
            return {'skipped': True, 'reason': 'threshold not reached'}
        
        self._last_gc_time = current_time
        
        # Get memory before optimization
        before_mb = psutil.Process().memory_info().rss / 1024 / 1024
        
        # Clear old cache entries
        query_stats_before = self.query_cache.stats()
        embedding_stats_before = self.embedding_cache.stats()
        
        # Trigger garbage collection
        collected = gc.collect()
        
        # Get memory after optimization
        after_mb = psutil.Process().memory_info().rss / 1024 / 1024
        
        result = {
            'forced': force,
            'memory_before_mb': before_mb,
            'memory_after_mb': after_mb,
            'memory_freed_mb': before_mb - after_mb,
            'gc_collected': collected,
            'query_cache_size': self.query_cache.stats()['size'],
            'embedding_cache_size': self.embedding_cache.stats()['size'],
            'tracked_objects': len(self._tracked_objects)
        }
        
        logger.info(f"Memory optimization completed: {result}")
        return result
    
    async def get_connection(self):
        """Get database connection from pool."""
        return await self.connection_pool.acquire()
    
    def get_performance_summary(self) -> Dict[str, Any]:
        """Get comprehensive performance summary."""
        uptime = time.time() - self._start_time
        
        return {
            'uptime_seconds': uptime,
            'total_requests': self.metrics.total_requests,
            'avg_response_time': self.metrics.avg_response_time,
            'requests_per_second': self.metrics.total_requests / uptime if uptime > 0 else 0,
            'memory_usage_mb': self.metrics.memory_usage_mb,
            'cpu_usage_percent': self.metrics.cpu_usage_percent,
            'cache_hit_rate': self.metrics.cache_hit_rate,
            'active_connections': self.metrics.active_connections,
            'query_cache_stats': self.query_cache.stats(),
            'embedding_cache_stats': self.embedding_cache.stats(),
            'connection_pool_stats': {
                'active': self.connection_pool.active_connections,
                'total_created': self.connection_pool.total_connections,
                'max_connections': self.connection_pool.max_connections
            }
        }
    
    def clear_caches(self) -> None:
        """Clear all caches."""
        self.query_cache.clear()
        self.embedding_cache.clear()
        logger.info("All caches cleared")
    
    def register_object(self, obj: Any) -> None:
        """Register object for tracking and cleanup."""
        self._tracked_objects.add(obj)
    
    async def shutdown(self) -> None:
        """Graceful shutdown with cleanup."""
        logger.info("Starting performance manager shutdown")
        
        # Clear caches
        self.clear_caches()
        
        # Force memory optimization
        self.optimize_memory(force=True)
        
        # Wait for active connections to finish (with timeout)
        timeout = 30  # seconds
        start_time = time.time()
        
        while self.connection_pool.active_connections > 0 and time.time() - start_time < timeout:
            logger.info(f"Waiting for {self.connection_pool.active_connections} active connections to finish")
            await asyncio.sleep(1)
        
        if self.connection_pool.active_connections > 0:
            logger.warning(f"Shutdown timeout reached with {self.connection_pool.active_connections} active connections")
        
        logger.info("Performance manager shutdown completed")


# Global performance manager instance
performance_manager = PerformanceManager()