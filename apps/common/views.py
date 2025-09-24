from django.utils import timezone
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from apps.common.responses import success_response


class HealthCheckView(APIView):
    """System health check endpoint"""
    permission_classes = [AllowAny]
    
    def get(self, request):
        return success_response({
            "status": "healthy",
            "timestamp": timezone.now().isoformat(),
            "version": "1.0.0"
        })