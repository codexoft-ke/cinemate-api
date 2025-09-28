import time
import hashlib
from django.conf import settings
from django.core.cache import cache
from django.http import JsonResponse
from django.utils.deprecation import MiddlewareMixin
from apps.common.responses import error_response


class RateLimitMiddleware(MiddlewareMixin):
    """Rate limiting middleware based on IP address and endpoint"""
    
    def process_request(self, request):
        if not settings.RATE_LIMIT_ENABLE:
            return None
            
        ip_address = self.get_client_ip(request)
        path = request.path_info
        method = request.method
        
        # Check if IP is blacklisted
        if self.is_ip_blacklisted(ip_address):
            return JsonResponse(
                error_response(
                    "IP address is temporarily blocked",
                    "IP_BLOCKED",
                    status_code=429
                ).data,
                status=429
            )
        
        # Define rate limits for different endpoints
        rate_limits = self.get_rate_limits(path)
        
        if rate_limits:
            key = f"rate_limit:{ip_address}:{path}:{method}"
            
            # Get current request count
            current_requests = cache.get(key, 0)
            
            if current_requests >= rate_limits['requests']:
                # Block IP temporarily if too many requests
                self.block_ip_temporarily(ip_address, 300)  # 5 minutes
                return JsonResponse(
                    error_response(
                        f"Rate limit exceeded. Max {rate_limits['requests']} requests per {rate_limits['window']} seconds",
                        "RATE_LIMIT_EXCEEDED",
                        status_code=429
                    ).data,
                    status=429
                )
            
            # Increment counter
            cache.set(key, current_requests + 1, rate_limits['window'])
        
        return None
    
    def get_client_ip(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip
    
    def get_rate_limits(self, path):
        """Define rate limits for different endpoint patterns"""
        if '/auth/' in path:
            return {'requests': 5, 'window': 60}  # 5 requests per minute
        elif '/movies/search' in path:
            return None  # No rate limiting for search
        elif '/movies/' in path:
            return {'requests': 100, 'window': 60}  # 100 requests per minute
        elif '/profile/' in path:
            return {'requests': 50, 'window': 60}  # 50 requests per minute
        return None
    
    def is_ip_blacklisted(self, ip_address):
        """Check if IP is in blacklist"""
        return cache.get(f"blacklist:{ip_address}", False)
    
    def block_ip_temporarily(self, ip_address, duration):
        """Temporarily block an IP address"""
        cache.set(f"blacklist:{ip_address}", True, duration)