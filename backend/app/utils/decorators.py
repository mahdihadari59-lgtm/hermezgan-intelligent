import time
import functools
import logging
from typing import Callable, Any, Optional, TypeVar, Tuple
from functools import wraps
import asyncio
import inspect
import hashlib

logger = logging.getLogger(__name__)

F = TypeVar('F', bound=Callable[..., Any])


def timing_decorator(logger_instance: Optional[logging.Logger] = None):
    def decorator(func: F) -> F:
        @wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            result = func(*args, **kwargs)
            elapsed = time.time() - start_time
            log = logger_instance or logger
            log.info(f"⏱️  {func.__name__} took {elapsed:.4f}s")
            return result

        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            start_time = time.time()
            result = await func(*args, **kwargs)
            elapsed = time.time() - start_time
            log = logger_instance or logger
            log.info(f"⏱️  {func.__name__} took {elapsed:.4f}s")
            return result

        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        return wrapper
    return decorator


def retry_decorator(max_retries: int = 3, delay: float = 1.0, backoff: float = 2.0, exceptions: Tuple[Exception, ...] = (Exception,)):
    def decorator(func: F) -> F:
        @wraps(func)
        def wrapper(*args, **kwargs):
            current_delay = delay
            last_exception = None
            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    last_exception = e
                    if attempt < max_retries - 1:
                        logger.warning(f"⚠️  {func.__name__} failed (attempt {attempt + 1}/{max_retries}): {e}")
                        time.sleep(current_delay)
                        current_delay *= backoff
            raise last_exception

        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            current_delay = delay
            last_exception = None
            for attempt in range(max_retries):
                try:
                    return await func(*args, **kwargs)
                except exceptions as e:
                    last_exception = e
                    if attempt < max_retries - 1:
                        logger.warning(f"⚠️  {func.__name__} failed (attempt {attempt + 1}/{max_retries}): {e}")
                        await asyncio.sleep(current_delay)
                        current_delay *= backoff
            raise last_exception

        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        return wrapper
    return decorator


def cache_decorator(ttl: int = 3600, prefix: str = "cache"):
    def decorator(func: F) -> F:
        @wraps(func)
        def wrapper(*args, **kwargs):
            from app.core.engine.redis_engine import get_cache
            key_parts = [prefix, func.__name__]
            key_parts.extend(str(arg) for arg in args)
            key_parts.extend(f"{k}:{v}" for k, v in sorted(kwargs.items()))
            cache_key = hashlib.md5(":".join(key_parts).encode()).hexdigest()
            cache = get_cache()
            cached = cache.get(cache_key)
            if cached is not None:
                logger.debug(f"📦  Cache hit: {func.__name__}")
                return cached
            result = func(*args, **kwargs)
            cache.set(cache_key, result, ttl)
            return result

        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            from app.core.engine.redis_engine import get_cache
            key_parts = [prefix, func.__name__]
            key_parts.extend(str(arg) for arg in args)
            key_parts.extend(f"{k}:{v}" for k, v in sorted(kwargs.items()))
            cache_key = hashlib.md5(":".join(key_parts).encode()).hexdigest()
            cache = get_cache()
            cached = cache.get(cache_key)
            if cached is not None:
                logger.debug(f"📦  Cache hit: {func.__name__}")
                return cached
            result = await func(*args, **kwargs)
            cache.set(cache_key, result, ttl)
            return result

        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        return wrapper
    return decorator


def log_decorator(logger_instance: Optional[logging.Logger] = None):
    def decorator(func: F) -> F:
        @wraps(func)
        def wrapper(*args, **kwargs):
            log = logger_instance or logger
            log.info(f"🔵  {func.__name__} called")
            try:
                result = func(*args, **kwargs)
                log.info(f"🟢  {func.__name__} completed")
                return result
            except Exception as e:
                log.error(f"🔴  {func.__name__} failed: {e}")
                raise

        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            log = logger_instance or logger
            log.info(f"🔵  {func.__name__} called")
            try:
                result = await func(*args, **kwargs)
                log.info(f"🟢  {func.__name__} completed")
                return result
            except Exception as e:
                log.error(f"🔴  {func.__name__} failed: {e}")
                raise

        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        return wrapper
    return decorator


def exception_handler(default_return: Any = None, log_error: bool = True, raise_errors: bool = False):
    def decorator(func: F) -> F:
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                if log_error:
                    logger.error(f"❌  {func.__name__} error: {e}", exc_info=True)
                if raise_errors:
                    raise
                return default_return

        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            try:
                return await func(*args, **kwargs)
            except Exception as e:
                if log_error:
                    logger.error(f"❌  {func.__name__} error: {e}", exc_info=True)
                if raise_errors:
                    raise
                return default_return

        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        return wrapper
    return decorator


def rate_limiter(max_requests: int, window_seconds: int = 60):
    requests = {}
    def decorator(func: F) -> F:
        @wraps(func)
        def wrapper(*args, **kwargs):
            key = "global"
            now = time.time()
            if key not in requests:
                requests[key] = []
            requests[key] = [t for t in requests[key] if now - t < window_seconds]
            if len(requests[key]) >= max_requests:
                from fastapi import HTTPException, status
                raise HTTPException(status_code=status.HTTP_429_TOO_MANY_REQUESTS, detail=f"بیش از حد مجاز (حداکثر {max_requests} در {window_seconds} ثانیه)")
            requests[key].append(now)
            return func(*args, **kwargs)
        return wrapper
    return decorator


def validate_input(validator_func: Callable):
    def decorator(func: F) -> F:
        @wraps(func)
        def wrapper(*args, **kwargs):
            sig = inspect.signature(func)
            bound_args = sig.bind(*args, **kwargs)
            bound_args.apply_defaults()
            for name, value in bound_args.arguments.items():
                if name == "data":
                    is_valid, error = validator_func(value)
                    if not is_valid:
                        from fastapi import HTTPException, status
                        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=error)
            return func(*args, **kwargs)
        return wrapper
    return decorator


def transaction_decorator(session_getter: Callable):
    def decorator(func: F) -> F:
        @wraps(func)
        def wrapper(*args, **kwargs):
            session = session_getter()
            try:
                result = func(session, *args, **kwargs)
                session.commit()
                return result
            except Exception as e:
                session.rollback()
                raise
            finally:
                session.close()

        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            session = session_getter()
            try:
                result = await func(session, *args, **kwargs)
                session.commit()
                return result
            except Exception as e:
                session.rollback()
                raise
            finally:
                session.close()

        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        return wrapper
    return decorator
