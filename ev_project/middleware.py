import logging
import time

logger = logging.getLogger(__name__)


class RequestLoggingMiddleware:
    """
    Custom Middleware for VoltStream.

    Runs on EVERY request and response.

    What it does:
    1. Logs every incoming request (method, path, user)
    2. Measures how long the view took to respond
    3. Logs the response status code and time taken

    This helps with:
    - Debugging slow endpoints
    - Tracking which endpoints are being used
    - Monitoring suspicious activity
    """

    def __init__(self, get_response):
        """
        get_response is the next middleware or view in the chain.
        Django calls __init__ once when the server starts.
        """
        self.get_response = get_response

    def __call__(self, request):
        """
        Django calls this on EVERY request.
        Code before get_response runs BEFORE the view.
        Code after get_response runs AFTER the view.
        """

        # ============================================
        # BEFORE THE VIEW RUNS
        # ============================================

        # Start the timer
        start_time = time.time()

        # Get user info for logging
        if hasattr(request, "user") and request.user.is_authenticated:
            user = request.user.email
        else:
            user = "Anonymous"

        # Log the incoming request
        logger.info(f"REQUEST | {request.method} {request.path} | User: {user}")

        # ============================================
        # VIEW RUNS HERE (get_response calls the view)
        # ============================================
        response = self.get_response(request)

        # ============================================
        # AFTER THE VIEW RUNS
        # ============================================

        # Calculate how long the view took
        duration = time.time() - start_time
        duration_ms = round(duration * 1000, 2)

        # Log the response
        logger.info(
            f"RESPONSE | {request.method} {request.path} | "
            f"Status: {response.status_code} | "
            f"Time: {duration_ms}ms | "
            f"User: {user}"
        )

        # Warn if response took more than 1 second
        if duration > 1:
            logger.warning(
                f"SLOW REQUEST | {request.method} {request.path} | "
                f"Time: {duration_ms}ms — consider optimizing!"
            )

        return response
