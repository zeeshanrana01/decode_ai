import time
from collections import defaultdict
from typing import Dict, List, Tuple
from app.config import RATE_LIMIT_PER_MINUTE, MAX_TOOL_CALLS


class RateLimiter:
    """Sliding-window in-memory rate limiter per client key."""

    def __init__(self, limit_per_minute: int = RATE_LIMIT_PER_MINUTE):
        self.limit = limit_per_minute
        self.requests: Dict[str, List[float]] = defaultdict(list)

    def is_allowed(self, client_id: str) -> Tuple[bool, int]:
        """
        Returns (is_allowed, remaining_quota).
        """
        now = time.time()
        window_start = now - 60.0

        # Purge older requests
        timestamps = [t for t in self.requests[client_id] if t > window_start]
        self.requests[client_id] = timestamps

        if len(timestamps) >= self.limit:
            return False, 0

        self.requests[client_id].append(now)
        remaining = self.limit - len(self.requests[client_id])
        return True, remaining

    def reset(self, client_id: str = None):
        if client_id:
            self.requests.pop(client_id, None)
        else:
            self.requests.clear()


class ToolCallLimiter:
    """Limits max tool calls per query execution to prevent infinite agent loops."""

    def __init__(self, max_calls: int = MAX_TOOL_CALLS):
        self.max_calls = max_calls
        self.counts: Dict[str, int] = defaultdict(int)

    def record_call(self, session_id: str) -> bool:
        """
        Records a tool invocation.
        Returns True if within limit, False if limit exceeded.
        """
        self.counts[session_id] += 1
        return self.counts[session_id] <= self.max_calls

    def get_count(self, session_id: str) -> int:
        return self.counts[session_id]

    def reset(self, session_id: str):
        self.counts.pop(session_id, None)


rate_limiter = RateLimiter()
tool_call_limiter = ToolCallLimiter()
