
"""Health Monitoring Service"""

import psutil
import time
import logging
from typing import Dict, Any
from datetime import datetime

logger = logging.getLogger(__name__)

class HealthService:
    """Monitor application and system health"""

    def __init__(self):
        self.start_time = time.time()
        
    def get_health_status(self) -> Dict[str, Any]:
        """
        Get comprehensive health status
        """
        uptime_seconds = time.time() - self.start_time
        
        cpu_percent = psutil.cpu_percent()
        memory = psutil.virtual_memory()
        
        status = {
            "status": "healthy",
            "timestamp": datetime.utcnow().isoformat(),
            "uptime_seconds": round(uptime_seconds, 2),
            "system": {
                "cpu_usage_percent": cpu_percent,
                "memory_usage_percent": memory.percent,
                "memory_available_mb": round(memory.available / (1024 * 1024), 2)
            }
        }
        
        return status
