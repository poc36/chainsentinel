"""Custom middleware: request timing, audit logging, rate limiting."""

import time
import uuid
from typing import Any

from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import Response

from app.core.logging import get_logger

logger = get_logger(__name__)


class RequestTimingMiddleware(BaseHTTPMiddleware):
    """Middleware that measures and logs request processing time."""

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        """Process each request and add timing headers.

        Args:
            request: Incoming HTTP request.
            call_next: Next middleware/handler in the chain.

        Returns:
            HTTP response with X-Process-Time header.
        """
        request_id = str(uuid.uuid4())[:8]
        start_time = time.perf_counter()

        response = await call_next(request)

        process_time = round((time.perf_counter() - start_time) * 1000, 2)
        response.headers["X-Process-Time"] = f"{process_time}ms"
        response.headers["X-Request-ID"] = request_id

        logger.info(
            "request_completed",
            request_id=request_id,
            method=request.method,
            path=str(request.url.path),
            status_code=response.status_code,
            process_time_ms=process_time,
        )

        return response


class AuditLogMiddleware(BaseHTTPMiddleware):
    """Middleware that logs write operations for audit trail."""

    AUDITED_METHODS = {"POST", "PUT", "PATCH", "DELETE"}
    SKIP_PATHS = {"/health", "/docs", "/openapi.json", "/redoc"}

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        """Log write operations for audit purposes.

        Args:
            request: Incoming HTTP request.
            call_next: Next middleware/handler in the chain.

        Returns:
            HTTP response (unchanged).
        """
        if (
            request.method in self.AUDITED_METHODS
            and request.url.path not in self.SKIP_PATHS
        ):
            client_ip = request.client.host if request.client else "unknown"
            logger.info(
                "audit_log",
                method=request.method,
                path=str(request.url.path),
                client_ip=client_ip,
                user_agent=request.headers.get("user-agent", "unknown"),
            )

        return await call_next(request)
