import time
from django.db import connection
import logging
from django.utils.deprecation import MiddlewareMixin

logger = logging.getLogger(__name__)


class PerformanceMiddleware(MiddlewareMixin):
    """
    Middleware to log performance metrics
    """
    
    def process_request(self, request):
        request.start_time = time.time()
        return None
    
    def process_response(self, request, response):
        if hasattr(request, 'start_time'):
            duration = time.time() - request.start_time
            query_count = len(connection.queries)
            
            # Add performance headers
            response['X-Request-Duration'] = f"{duration:.3f}"
            response['X-Query-Count'] = str(query_count)
            
            # Log slow requests
            if duration > 2.0:  # More than 2 seconds
                logger.warning(
                    f"SLOW_REQUEST: {request.path} - "
                    f"Duration: {duration:.2f}s - "
                    f"Queries: {query_count} - "
                    f"Method: {request.method} - "
                    f"User: {request.user}"
                )
            elif duration > 1.0:  # More than 1 second
                logger.info(
                    f"MODERATE_REQUEST: {request.path} - "
                    f"Duration: {duration:.2f}s - "
                    f"Queries: {query_count}"
                )
        
        return response


class CacheControlMiddleware(MiddlewareMixin):
    """
    Add cache control headers
    """
    
    def process_response(self, request, response):
        # Add cache headers for static-like pages
        if request.path == '/' or request.path.startswith('/static/') or request.path.startswith('/media/'):
            response['Cache-Control'] = 'public, max-age=300'  # 5 minutes
        
        # Don't cache authenticated pages
        if request.user.is_authenticated:
            response['Cache-Control'] = 'private, no-cache, no-store, must-revalidate'
        
        return response