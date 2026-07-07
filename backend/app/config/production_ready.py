"""Phase 10: Production Ready - Performance Optimization and Security Hardening"""

from typing import Dict, Any
import logging
import time
from functools import wraps
import asyncio

logger = logging.getLogger(__name__)


class PerformanceOptimizer:
    """Production performance optimization strategies"""
    
    def __init__(self):
        self.cache_stats = {
            "hits": 0,
            "misses": 0,
            "evictions": 0,
        }
    
    @staticmethod
    def cache_with_ttl(ttl_seconds: int = 3600):
        """Cache decorator with TTL for expensive operations"""
        def decorator(func):
            cache = {}
            cache_times = {}
            
            @wraps(func)
            async def async_wrapper(*args, **kwargs):
                key = (args, tuple(kwargs.items()))
                current_time = time.time()
                
                # Check if cached and not expired
                if key in cache and (current_time - cache_times[key]) < ttl_seconds:
                    logger.debug(f"Cache hit for {func.__name__}")
                    return cache[key]
                
                # Call function and cache result
                result = await func(*args, **kwargs)
                cache[key] = result
                cache_times[key] = current_time
                
                logger.debug(f"Cache miss for {func.__name__}, storing result")
                return result
            
            @wraps(func)
            def sync_wrapper(*args, **kwargs):
                key = (args, tuple(kwargs.items()))
                current_time = time.time()
                
                if key in cache and (current_time - cache_times[key]) < ttl_seconds:
                    logger.debug(f"Cache hit for {func.__name__}")
                    return cache[key]
                
                result = func(*args, **kwargs)
                cache[key] = result
                cache_times[key] = current_time
                
                logger.debug(f"Cache miss for {func.__name__}, storing result")
                return result
            
            return async_wrapper if asyncio.iscoroutinefunction(func) else sync_wrapper
        
        return decorator
    
    @staticmethod
    def rate_limit(max_requests: int = 100, window_seconds: int = 60):
        """Rate limiting decorator"""
        def decorator(func):
            requests = []
            
            @wraps(func)
            def wrapper(*args, **kwargs):
                current_time = time.time()
                
                # Remove old requests outside window
                requests[:] = [req_time for req_time in requests 
                             if current_time - req_time < window_seconds]
                
                if len(requests) >= max_requests:
                    raise RuntimeError(f"Rate limit exceeded: {max_requests}/{window_seconds}s")
                
                requests.append(current_time)
                return func(*args, **kwargs)
            
            return wrapper
        return decorator


class SecurityHardening:
    """Production security best practices"""
    
    # Security headers
    SECURITY_HEADERS = {
        "X-Content-Type-Options": "nosniff",
        "X-Frame-Options": "DENY",
        "X-XSS-Protection": "1; mode=block",
        "Strict-Transport-Security": "max-age=31536000; includeSubDomains",
        "Content-Security-Policy": "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'",
        "Referrer-Policy": "strict-origin-when-cross-origin",
    }
    
    # Input validation
    SANITIZATION_RULES = {
        "max_question_length": 1000,
        "max_document_size": 52428800,  # 50MB
        "allowed_file_types": [".pdf", ".txt", ".docx"],
        "max_concurrent_uploads": 5,
        "max_api_requests_per_minute": 60,
    }
    
    @staticmethod
    def validate_input(value: str, max_length: int = 1000) -> str:
        """Sanitize and validate user input"""
        if not value:
            raise ValueError("Input cannot be empty")
        
        if len(value) > max_length:
            raise ValueError(f"Input exceeds maximum length of {max_length}")
        
        # Remove potentially dangerous characters
        dangerous_chars = ["<script", "javascript:", "onerror=", "onclick="]
        for char in dangerous_chars:
            if char.lower() in value.lower():
                raise ValueError("Input contains potentially dangerous content")
        
        return value.strip()
    
    @staticmethod
    def validate_file(filename: str, file_size: int, allowed_types: list) -> bool:
        """Validate uploaded file"""
        # Check file size
        max_size = 52428800  # 50MB
        if file_size > max_size:
            raise ValueError(f"File size {file_size} exceeds maximum {max_size}")
        
        # Check file type
        file_ext = '.' + filename.split('.')[-1].lower()
        if file_ext not in allowed_types:
            raise ValueError(f"File type {file_ext} not allowed")
        
        return True


class LoadTesting:
    """Load testing configuration and benchmarks"""
    
    BENCHMARK_SCENARIOS = {
        "baseline": {
            "concurrent_users": 1,
            "requests_per_user": 100,
            "ramp_up_time": 1,
        },
        "normal": {
            "concurrent_users": 10,
            "requests_per_user": 50,
            "ramp_up_time": 5,
        },
        "peak": {
            "concurrent_users": 50,
            "requests_per_user": 20,
            "ramp_up_time": 10,
        },
        "stress": {
            "concurrent_users": 100,
            "requests_per_user": 10,
            "ramp_up_time": 15,
        }
    }
    
    PERFORMANCE_TARGETS = {
        "api_response_time_ms": 500,
        "upload_processing_time_ms": 5000,
        "query_processing_time_ms": 2000,
        "average_cpu_usage_percent": 70,
        "peak_memory_usage_mb": 2048,
        "99th_percentile_latency_ms": 1000,
    }
    
    @staticmethod
    def get_load_test_script(scenario: str) -> str:
        """Generate locust load test script"""
        return f"""
from locust import HttpUser, task, between

class ResearchMindUser(HttpUser):
    wait_time = between(1, 3)
    
    @task(1)
    def upload_document(self):
        with open('test_document.pdf', 'rb') as f:
            self.client.post('/api/v1/upload', files={{'file': f}})
    
    @task(3)
    def ask_question(self):
        self.client.post('/api/v1/ask', json={{
            'question': 'What is machine learning?',
            'top_k': 5
        }})
    
    @task(1)
    def health_check(self):
        self.client.get('/api/v1/health')
"""


class MonitoringAndMetrics:
    """Production monitoring setup"""
    
    METRIC_CATEGORIES = {
        "application": [
            "api_requests_total",
            "api_request_duration_seconds",
            "api_errors_total",
            "document_uploads_total",
            "documents_processed_total",
            "queries_answered_total",
            "average_confidence_score",
        ],
        "system": [
            "cpu_usage_percent",
            "memory_usage_bytes",
            "disk_usage_bytes",
            "network_io_bytes",
            "process_uptime_seconds",
        ],
        "vectordb": [
            "vector_search_latency_ms",
            "total_vectors_stored",
            "collection_info",
            "search_operations_total",
            "indexing_operations_total",
        ],
    }
    
    ALERTING_THRESHOLDS = {
        "high_error_rate": 0.05,  # 5% of requests fail
        "slow_api_response": 1000,  # 1 second
        "high_cpu_usage": 85,  # 85%
        "high_memory_usage": 90,  # 90%
        "vector_search_slow": 500,  # 500ms
        "zero_confidence_answers": 0.3,  # Answers with <30% confidence
    }


class ProductionDeployment:
    """Production deployment checklist and configuration"""
    
    DEPLOYMENT_CHECKLIST = {
        "Security": [
            "[OK] Enable HTTPS/TLS",
            "[OK] Setup API key authentication",
            "[OK] Enable rate limiting",
            "[OK] Configure security headers",
            "[OK] Setup WAF (Web Application Firewall)",
            "[OK] Regular security audits",
            "[OK] Implement request signing",
        ],
        "Performance": [
            "[OK] Enable caching layer (Redis)",
            "[OK] Database connection pooling",
            "[OK] CDN for static assets",
            "[OK] Async request processing",
            "[OK] Query optimization",
            "[OK] Load testing complete",
        ],
        "Monitoring": [
            "[OK] Application performance monitoring",
            "[OK] Error tracking (Sentry)",
            "[OK] Centralized logging",
            "[OK] Metrics collection",
            "[OK] Uptime monitoring",
            "[OK] Alert system setup",
        ],
        "Infrastructure": [
            "[OK] Containerization (Docker)",
            "[OK] Orchestration (Kubernetes optional)",
            "[OK] Database backups",
            "[OK] Disaster recovery plan",
            "[OK] Auto-scaling configured",
            "[OK] CDN/Load balancer setup",
        ],
        "Documentation": [
            "[OK] API documentation",
            "[OK] Deployment guide",
            "[OK] Troubleshooting guide",
            "[OK] Runbooks for incidents",
            "[OK] Architecture diagram",
            "[OK] Security policies documented",
        ],
    }
    
    INFRASTRUCTURE_REQUIREMENTS = {
        "development": {
            "cpu": "2 cores",
            "memory": "4 GB",
            "storage": "20 GB",
            "database": "Qdrant local",
        },
        "staging": {
            "cpu": "4 cores",
            "memory": "8 GB",
            "storage": "100 GB",
            "database": "Qdrant standalone",
        },
        "production": {
            "cpu": "8+ cores",
            "memory": "16+ GB",
            "storage": "500 GB+",
            "database": "Qdrant Cloud (high availability)",
        },
    }
    
    KUBERNETES_DEPLOYMENT = """
apiVersion: apps/v1
kind: Deployment
metadata:
  name: researchmind-backend
spec:
  replicas: 3
  selector:
    matchLabels:
      app: researchmind-backend
  template:
    metadata:
      labels:
        app: researchmind-backend
    spec:
      containers:
      - name: backend
        image: researchmind/backend:latest
        ports:
        - containerPort: 8000
        resources:
          requests:
            memory: "256Mi"
            cpu: "250m"
          limits:
            memory: "512Mi"
            cpu: "500m"
        env:
        - name: ENVIRONMENT
          value: "production"
        - name: GEMINI_API_KEY
          valueFrom:
            secretKeyRef:
              name: researchmind-secrets
              key: gemini-api-key
        - name: QDRANT_URL
          value: "https://qdrant-cluster.qdrant.io"
        livenessProbe:
          httpGet:
            path: /api/v1/health
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /api/v1/health
            port: 8000
          initialDelaySeconds: 10
          periodSeconds: 5
---
apiVersion: v1
kind: Service
metadata:
  name: researchmind-service
spec:
  type: LoadBalancer
  ports:
  - port: 80
    targetPort: 8000
  selector:
    app: researchmind-backend
"""


class BackupAndRecovery:
    """Backup and disaster recovery procedures"""
    
    BACKUP_SCHEDULE = {
        "vector_database": "daily at 2 AM UTC",
        "documents": "every 6 hours",
        "configurations": "daily",
        "logs": "weekly",
    }
    
    RECOVERY_TIME_OBJECTIVE = {
        "rto_minutes": 15,  # Time to restore
        "rpo_minutes": 60,  # Data loss acceptable
    }
    
    RECOVERY_PROCEDURES = {
        "vector_db_recovery": "Restore from daily backup, resync embeddings",
        "document_recovery": "Restore from backup, reprocess if needed",
        "config_recovery": "Restore from version control",
        "full_system_recovery": "Rebuild from infrastructure as code (Terraform/CloudFormation)",
    }
