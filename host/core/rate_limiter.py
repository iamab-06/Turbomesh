import time
from collections import defaultdict, deque
from threading import Lock
from typing import Tuple, Optional

class SlidingWindowRateLimiter:
    """
    In-memory Sliding-Window Rate Limiter.
    Tracks requests per client IP across a rolling time window.
    Thread-safe and requires no external dependencies (e.g., Redis).
    """
    def __init__(self, max_requests: int = 5, window_seconds: int = 60, cleanup_interval: int = 300):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.cleanup_interval = cleanup_interval
        self._history = defaultdict(deque)
        self._lock = Lock()
        self._last_cleanup = time.time()

    def check(self, client_ip: str) -> Tuple[bool, int, int]:
        """
        Check if a request from client_ip is allowed under the rate limit.
        Returns:
            allowed (bool): True if request is accepted, False if rate limited.
            retry_after (int): Seconds remaining until the client can retry.
            remaining (int): Requests remaining in current rolling window.
        """
        now = time.time()
        cutoff = now - self.window_seconds

        with self._lock:
            # Periodic garbage collection for inactive IPs
            if now - self._last_cleanup > self.cleanup_interval:
                self._cleanup_stale_ips(cutoff)

            timestamps = self._history[client_ip]

            # 1. Slide window: evict timestamps outside the window
            while timestamps and timestamps[0] <= cutoff:
                timestamps.popleft()

            # 2. Check if limit reached
            if len(timestamps) >= self.max_requests:
                # Calculate remaining seconds until oldest request expires
                oldest_timestamp = timestamps[0]
                retry_after = max(1, int(self.window_seconds - (now - oldest_timestamp)))
                return False, retry_after, 0

            # 3. Allow and record timestamp
            timestamps.append(now)
            remaining = self.max_requests - len(timestamps)
            return True, 0, remaining

    def reset(self, client_ip: Optional[str] = None):
        """Reset history for a specific IP or all IPs (useful for testing)."""
        with self._lock:
            if client_ip:
                self._history.pop(client_ip, None)
            else:
                self._history.clear()

    def _cleanup_stale_ips(self, cutoff: float):
        """Remove IPs that have had zero activity in the rolling window."""
        stale_ips = [ip for ip, timestamps in self._history.items() if not timestamps or timestamps[-1] <= cutoff]
        for ip in stale_ips:
            del self._history[ip]
        self._last_cleanup = time.time()

# Global pairing rate limiter instance: 5 requests per 60 seconds
pairing_rate_limiter = SlidingWindowRateLimiter(max_requests=5, window_seconds=60)
